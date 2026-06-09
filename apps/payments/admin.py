from django.contrib import admin
from .models import Coupon, Transaction


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'percent_off', 'amount_off', 'uses', 'max_uses', 'is_active')
    list_editable = ('is_active',)
    search_fields = ('code',)
    filter_horizontal = ('applicable_courses',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'currency', 'status', 'provider', 'created_at')
    list_filter = ('status', 'provider')
    search_fields = ('user__email', 'provider_reference')
    actions = ['mark_succeeded']

    def mark_succeeded(self, request, queryset):
        queryset.update(status='succeeded')
    mark_succeeded.short_description = "Mark as Succeeded (manual fulfillment)"
