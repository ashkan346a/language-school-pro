"""
Learning views — Mission Control (dashboard) and immersive lesson viewer.
Uses HTMX for live progress updates. Orbital progress visuals.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from .models import Enrollment, LessonProgress
from apps.catalog.models import Lesson
from apps.core.views import _get_site_data


@login_required
def dashboard(request):
    """Student Mission Control: list of active/completed trajectories with beautiful orbital progress."""
    enrollments = (
        Enrollment.objects.filter(student=request.user)
        .select_related('course__language', 'course__instructor__user')
        .prefetch_related('course__modules__lessons')
        .order_by('-enrolled_at')
    )

    # Annotate simple progress for each (recalc if needed)
    for enr in enrollments:
        enr.recalculate_progress()  # ensures up to date
        # total lessons
        enr._total_lessons = sum(m.lessons.count() for m in enr.course.modules.all()) or 1
        enr._completed = LessonProgress.objects.filter(enrollment=enr, is_completed=True).count()

    site, *_ = _get_site_data()
    context = {
        'site': site,
        'enrollments': enrollments,
    }
    return render(request, 'public/dashboard.html', context)


@login_required
def learn(request, enrollment_id, lesson_id=None):
    """Immersive learning view: sidebar mission log + main transmission viewer.
    Beautiful, focused, non-generic.
    """
    enrollment = get_object_or_404(
        Enrollment.objects.select_related('course__language', 'course__instructor__user'),
        pk=enrollment_id, student=request.user
    )

    modules = enrollment.course.modules.prefetch_related('lessons').order_by('order')

    # Determine current lesson
    current_lesson = None
    if lesson_id:
        current_lesson = get_object_or_404(Lesson, pk=lesson_id, module__course=enrollment.course)

    if not current_lesson:
        # pick first preview or first lesson
        for m in modules:
            for les in m.lessons.order_by('order'):
                current_lesson = les
                break
            if current_lesson:
                break

    # Progress map
    progress = {
        lp.lesson_id: lp for lp in LessonProgress.objects.filter(enrollment=enrollment)
    }

    # Compute overall
    total_lessons = sum(m.lessons.count() for m in modules)
    done = sum(1 for lp in progress.values() if lp.is_completed)
    percent = int((done / max(total_lessons, 1)) * 100) if total_lessons else 0
    site, *_ = _get_site_data()

    context = {
        'site': site,
        'enrollment': enrollment,
        'modules': modules,
        'current_lesson': current_lesson,
        'progress': progress,
        'percent': percent,
        'total_lessons': total_lessons,
        'done_lessons': done,
    }
    return render(request, 'public/learn.html', context)


@login_required
@require_POST
def mark_lesson_complete(request, lesson_id):
    """HTMX endpoint: mark a lesson complete for current user's enrollment on that course.
    Returns a small HTML fragment for swap.
    """
    lesson = get_object_or_404(Lesson, pk=lesson_id)

    # Find the enrollment for this user + course
    try:
        enrollment = Enrollment.objects.get(student=request.user, course=lesson.module.course)
    except Enrollment.DoesNotExist:
        return HttpResponse("No active enrollment for this mission.", status=400)

    lp, _ = LessonProgress.objects.get_or_create(enrollment=enrollment, lesson=lesson)
    lp.mark_complete()

    # Return a success badge fragment (htmx will swap)
    return HttpResponse(
        f'<span class="inline-flex items-center gap-1 text-emerald-400 text-xs px-2 py-0.5 rounded border border-emerald-400/30">'
        f'<span>WAYPOINT REACHED</span></span>',
        content_type='text/html'
    )
