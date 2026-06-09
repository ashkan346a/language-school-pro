from django.contrib import admin
from .models import SiteSettings, Language, Stat, Feature, Testimonial, FAQ


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'tagline')
    readonly_fields = ('pk',)

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'accent_color', 'is_active', 'order')
    list_editable = ('is_active', 'order', 'accent_color')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'code')


@admin.register(Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ('value', 'label', 'icon_key', 'order', 'is_active')
    list_editable = ('order', 'is_active')


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon_key', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    search_fields = ('title',)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('name', 'role', 'rating', 'is_featured', 'order')
    list_editable = ('is_featured', 'order', 'rating')
    search_fields = ('name', 'role', 'quote')


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'category', 'order', 'is_active')
    list_editable = ('order', 'is_active', 'category')
    search_fields = ('question',)
