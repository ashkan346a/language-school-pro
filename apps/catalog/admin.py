from django.contrib import admin
from .models import Course, Module, Lesson


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ('order', 'title', 'content_type', 'duration_min', 'is_preview')


class ModuleInline(admin.StackedInline):
    model = Module
    extra = 1
    show_change_link = True
    inlines = [LessonInline]  # Note: nested inlines limited; lessons also editable on module


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'language', 'level', 'format', 'price', 'is_featured', 'is_published')
    list_editable = ('is_featured', 'is_published')
    list_filter = ('language', 'level', 'format', 'is_published')
    search_fields = ('title', 'subtitle', 'description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]
    autocomplete_fields = ('instructor', 'language')
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'language', 'level', 'instructor')}),
        ('Mission Details', {'fields': ('subtitle', 'description', 'what_you_will_learn', 'requirements')}),
        ('Flight Parameters', {'fields': ('price', 'currency', 'duration_weeks', 'format', 'max_enrollments', 'thumbnail')}),
        ('Visibility', {'fields': ('is_featured', 'is_published', 'published_at')}),
    )
