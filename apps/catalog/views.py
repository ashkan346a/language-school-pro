"""
Catalog views for Aether — Course catalog and detail with premium space aesthetic.
Everything admin-configurable via Course/Module/Lesson models.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Prefetch
from .models import Course, Module, Lesson
from apps.core.models import Language
from apps.core.views import _get_site_data
from apps.learning.models import Enrollment, LessonProgress


def course_list(request):
    """Beautiful public course catalog. Supports ?lang=slug filter and search q=."""
    q = request.GET.get('q', '').strip()
    lang_slug = request.GET.get('lang', '').strip()

    courses = Course.objects.filter(is_published=True).select_related('language', 'instructor__user').prefetch_related('modules')

    if lang_slug:
        courses = courses.filter(language__slug=lang_slug)
    if q:
        courses = courses.filter(
            Q(title__icontains=q) |
            Q(subtitle__icontains=q) |
            Q(description__icontains=q) |
            Q(language__name__icontains=q)
        )

    languages = Language.objects.filter(is_active=True).order_by('order')
    site, *_ = _get_site_data()  # defensive

    context = {
        'site': site,
        'courses': courses,
        'languages': languages,
        'active_lang': lang_slug,
        'q': q,
    }
    return render(request, 'public/courses.html', context)


def course_detail(request, slug):
    """Stunning mission briefing + curriculum for a single course."""
    course = get_object_or_404(
        Course.objects.select_related('language', 'instructor__user')
        .prefetch_related(
            Prefetch('modules', queryset=Module.objects.prefetch_related('lessons').order_by('order'))
        ),
        slug=slug,
        is_published=True
    )

    # If user enrolled, pass progress info for orbital indicators
    enrollment = None
    progress_map = {}
    if request.user.is_authenticated:
        try:
            enrollment = Enrollment.objects.select_related('course').get(student=request.user, course=course)
            for lp in LessonProgress.objects.filter(enrollment=enrollment).select_related('lesson'):
                progress_map[lp.lesson_id] = lp
        except Enrollment.DoesNotExist:
            enrollment = None

    # Compute simple total lessons for progress display
    total_lessons = sum(m.lessons.count() for m in course.modules.all())
    completed = len(progress_map) if progress_map else 0
    site, *_ = _get_site_data()

    context = {
        'site': site,
        'course': course,
        'enrollment': enrollment,
        'progress_map': progress_map,
        'total_lessons': total_lessons,
        'completed_lessons': completed,
        'progress_percent': int((completed / max(total_lessons, 1)) * 100) if total_lessons else 0,
    }
    return render(request, 'public/course_detail.html', context)


@login_required
def enroll(request, slug):
    """Simple enroll action. Creates active enrollment (or re-activates). In real would go through payments."""
    course = get_object_or_404(Course, slug=slug, is_published=True)

    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'status': 'active'}
    )
    if not created and enrollment.status != 'active':
        enrollment.status = 'active'
        enrollment.save(update_fields=['status'])

    messages.success(request, f"Trajectory locked. Welcome aboard {course.title}. Check your Mission Control.")
    return redirect('dashboard')
