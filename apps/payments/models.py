from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    code = models.CharField(max_length=30, unique=True)
    percent_off = models.PositiveSmallIntegerField(default=0, help_text="0-100")
    amount_off = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_until = models.DateTimeField(null=True, blank=True)
    max_uses = models.PositiveIntegerField(default=100)
    uses = models.PositiveIntegerField(default=0)
    applicable_courses = models.ManyToManyField('catalog.Course', blank=True, help_text="Empty = applies to all")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        if self.percent_off:
            return f"{self.code} ({self.percent_off}% off)"
        return f"{self.code} (${self.amount_off} off)"

    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        if self.uses >= self.max_uses:
            return False
        return now >= self.valid_from


class Transaction(models.Model):
    STATUS = [
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed'),
        ('manual', 'Manual / Admin Activated'),
    ]
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='transactions')
    enrollment = models.ForeignKey('learning.Enrollment', on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    status = models.CharField(max_length=10, choices=STATUS, default='pending')
    provider = models.CharField(max_length=30, default='stripe', help_text="stripe | manual")
    provider_reference = models.CharField(max_length=120, blank=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.email} — {self.amount} {self.currency} ({self.status})"
