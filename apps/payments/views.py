"""
Payments — Stripe Checkout + coupon + webhook fulfillment for Aether.
Everything defensive for Railway. Manual admin fallback always available.
"""
import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone

from apps.catalog.models import Course
from apps.learning.models import Enrollment
from .models import Transaction, Coupon
from apps.core.views import _get_site_data


stripe.api_key = settings.STRIPE_SECRET_KEY or ''


@login_required
def checkout(request, course_slug):
    """Premium glass checkout. Supports live coupon via HTMX. Creates pending enrollment + tx."""
    site, *_ = _get_site_data()
    try:
        course = Course.objects.get(slug=course_slug, is_published=True)
    except Course.DoesNotExist:
        messages.error(request, "مسیر مورد نظر یافت نشد.")
        return redirect('catalog:course_list')

    # Free or already active -> instant
    if course.price <= 0:
        enrollment, _ = Enrollment.objects.get_or_create(student=request.user, course=course, defaults={'status': 'active'})
        messages.success(request, "ثبت‌نام رایگان انجام شد.")
        return redirect('learning:dashboard')

    existing = Enrollment.objects.filter(student=request.user, course=course).first()
    if existing and existing.status in ('active', 'completed'):
        return redirect('learning:learn', enrollment_id=existing.id)

    # Coupon from GET or session (HTMX updates)
    coupon_code = request.GET.get('coupon', '') or request.session.get('aether_coupon', '')
    discount = 0
    applied_coupon = None
    if coupon_code:
        try:
            c = Coupon.objects.get(code__iexact=coupon_code, is_active=True)
            if c.is_valid():
                applied_coupon = c
                if c.percent_off:
                    discount = int(course.price * c.percent_off / 100)
                else:
                    discount = min(int(c.amount_off), int(course.price))
        except Coupon.DoesNotExist:
            pass

    final_price = max(0, int(course.price) - discount)

    context = {
        'site': site,
        'course': course,
        'final_price': final_price,
        'original_price': course.price,
        'discount': discount,
        'coupon_code': coupon_code,
        'applied_coupon': applied_coupon,
        'stripe_pk': settings.STRIPE_PUBLISHABLE_KEY,
    }
    return render(request, 'public/checkout.html', context)


@login_required
@require_POST
def validate_coupon(request):
    """HTMX endpoint: validate coupon code and return updated summary fragment."""
    code = (request.POST.get('code') or '').strip().upper()
    course_slug = request.POST.get('course_slug')
    try:
        course = Course.objects.get(slug=course_slug)
    except Course.DoesNotExist:
        return HttpResponse('<span class="text-rose-400 text-xs">دوره یافت نشد</span>')

    discount = 0
    msg = ''
    if code:
        try:
            c = Coupon.objects.get(code=code, is_active=True)
            if c.is_valid():
                if c.percent_off:
                    discount = int(course.price * c.percent_off / 100)
                else:
                    discount = min(int(c.amount_off), int(course.price))
                request.session['aether_coupon'] = code
                msg = f'کوپن «{code}» اعمال شد'
            else:
                msg = 'کوپن منقضی یا نامعتبر است'
        except Coupon.DoesNotExist:
            msg = 'کوپن یافت نشد'

    final = max(0, int(course.price) - discount)
    html = f'''
    <div class="text-sm">
      <div class="flex justify-between"><span>قیمت پایه</span><span>{int(course.price)} {course.currency}</span></div>
      {f'<div class="flex justify-between text-emerald-400"><span>تخفیف ({code})</span><span>-{discount}</span></div>' if discount else ''}
      <div class="flex justify-between pt-2 mt-2 border-t border-white/10 font-semibold"><span>قابل پرداخت</span><span>{final} {course.currency}</span></div>
      <div class="text-[10px] text-white/50 mt-1">{msg}</div>
    </div>
    '''
    return HttpResponse(html)


@login_required
def create_stripe_session(request, course_slug):
    """Called from checkout template POST to actually create the session (kept separate for clarity)."""
    # For simplicity the template can POST to this or we do it in checkout view on "Pay" button.
    # Here we implement the actual session creation.
    course = get_object_or_404(Course, slug=course_slug, is_published=True)
    if course.price <= 0:
        return redirect('catalog:enroll', slug=course_slug)

    enrollment, _ = Enrollment.objects.get_or_create(
        student=request.user, course=course,
        defaults={'status': 'pending'}
    )

    coupon_code = request.session.get('aether_coupon', '')
    discount = 0
    coupon_obj = None
    if coupon_code:
        try:
            c = Coupon.objects.get(code__iexact=coupon_code, is_active=True)
            if c.is_valid():
                coupon_obj = c
                if c.percent_off:
                    discount = int(course.price * c.percent_off / 100)
                else:
                    discount = min(int(c.amount_off), int(course.price))
        except Exception:
            pass

    amount = max(50, int((course.price - discount) * 100))  # cents, Stripe min safety

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': course.currency.lower(),
                    'product_data': {'name': course.title, 'description': (course.subtitle or '')[:120]},
                    'unit_amount': amount,
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri('/payments/success/?session_id={CHECKOUT_SESSION_ID}&enrollment=' + str(enrollment.id)),
            cancel_url=request.build_absolute_uri('/payments/cancel/?enrollment=' + str(enrollment.id)),
            customer_email=request.user.email,
            metadata={
                'enrollment_id': str(enrollment.id),
                'course_slug': course.slug,
                'coupon': coupon_code or '',
            }
        )

        # Record pending transaction
        Transaction.objects.create(
            user=request.user,
            enrollment=enrollment,
            amount=(amount / 100.0),
            currency=course.currency,
            status='pending',
            provider='stripe',
            provider_reference=session.id,
            coupon=coupon_obj,
        )
        return redirect(session.url, permanent=False)
    except Exception as e:
        messages.error(request, "خطا در اتصال به درگاه پرداخت. لطفاً دوباره تلاش کنید یا از ادمین استفاده کنید.")
        return redirect('catalog:course_detail', slug=course_slug)


@login_required
def success(request):
    """Stripe success redirect. Idempotent activation + tx update."""
    session_id = request.GET.get('session_id')
    enrollment_id = request.GET.get('enrollment')

    enrollment = None
    if enrollment_id:
        enrollment = Enrollment.objects.filter(id=enrollment_id, student=request.user).first()

    if session_id and stripe.api_key:
        try:
            sess = stripe.checkout.Session.retrieve(session_id)
            if sess.payment_status == 'paid':
                if enrollment:
                    enrollment.status = 'active'
                    enrollment.save(update_fields=['status'])
                # Mark tx
                Transaction.objects.filter(provider_reference=session_id).update(status='succeeded', enrollment=enrollment)
                # Clear coupon
                request.session.pop('aether_coupon', None)
                messages.success(request, "پرداخت موفق. خوش آمدید به مدار.")
                if enrollment:
                    return redirect('learning:learn', enrollment_id=enrollment.id)
        except Exception:
            pass

    if enrollment:
        enrollment.status = 'active'
        enrollment.save(update_fields=['status'])
        return redirect('learning:dashboard')

    messages.info(request, "پرداخت ثبت شد. وضعیت در داشبورد به‌روزرسانی می‌شود.")
    return redirect('learning:dashboard')


@login_required
def cancel(request):
    messages.warning(request, "پرداخت لغو شد. می‌توانید دوباره تلاش کنید.")
    return redirect('catalog:course_list')


@csrf_exempt
def stripe_webhook(request):
    """Production webhook for reliable fulfillment."""
    payload = request.body
    sig = request.META.get('HTTP_STRIPE_SIGNATURE', '')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(payload, sig, endpoint_secret)
    except Exception:
        return HttpResponseBadRequest('Bad signature')

    if event['type'] == 'checkout.session.completed':
        sess = event['data']['object']
        enrollment_id = sess.get('metadata', {}).get('enrollment_id')
        if enrollment_id:
            try:
                enr = Enrollment.objects.get(id=enrollment_id)
                enr.status = 'active'
                enr.save(update_fields=['status'])
                Transaction.objects.filter(provider_reference=sess.get('id')).update(status='succeeded', enrollment=enr)
            except Enrollment.DoesNotExist:
                pass

    return HttpResponse(status=200)