from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<slug:course_slug>/', views.checkout, name='checkout'),
    path('checkout/<slug:course_slug>/create-session/', views.create_stripe_session, name='create_session'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
    path('webhook/', views.stripe_webhook, name='webhook'),
    # HTMX coupon validator (live in checkout)
    path('coupon/validate/', views.validate_coupon, name='validate_coupon'),
]