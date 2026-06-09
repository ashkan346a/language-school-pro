from django.contrib import admin
from .models import Enrollment, LessonProgress, Assignment, Submission, Certificate


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'status', 'progress_percent', 'enrolled_at')
    list_filter = ('status', 'course__language', 'course__level')
    search_fields = ('student__email', 'course__title')
    readonly_fields = ('progress_percent',)
    actions = ['mark_completed']

    def mark_completed(self, request, queryset):
        for e in queryset:
            e.status = 'completed'
            e.completed_at = e.completed_at or __import__('django.utils.timezone').utils.timezone.now()
            e.progress_percent = 100
            e.save()
    mark_completed.short_description = "Mark selected as Mission Complete"


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'lesson', 'is_completed', 'completed_at')
    list_filter = ('is_completed',)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'lesson', 'max_points', 'due_date')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'enrollment', 'score', 'submitted_at')
    search_fields = ('enrollment__student__email',)


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('certificate_number', 'enrollment', 'issued_at', 'is_valid')
    actions = ['invalidate_certs']

    def invalidate_certs(self, request, queryset):
        queryset.update(is_valid=False)
    invalidate_certs.short_description = "Invalidate selected certificates"
