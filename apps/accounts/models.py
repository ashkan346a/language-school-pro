from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Custom user. Email is the primary identifier for friendliness."""
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.get_full_name() or self.email


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    target_languages = models.ManyToManyField('core.Language', blank=True, related_name='students')
    weekly_goal_hours = models.PositiveSmallIntegerField(default=5)
    current_streak_days = models.PositiveIntegerField(default=0)
    total_minutes_learned = models.PositiveIntegerField(default=0)
    preferred_format = models.CharField(
        max_length=20,
        choices=[('self_paced', 'Self-Paced'), ('live_cohort', 'Live Cohort'), ('private', 'Private')],
        default='self_paced'
    )
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Student: {self.user.email}"


class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    title = models.CharField(max_length=120, default="Lead Language Architect")
    bio = models.TextField(blank=True)
    photo = models.ImageField(upload_to='teachers/', blank=True, null=True)
    languages_taught = models.ManyToManyField('core.Language', blank=True, related_name='teachers')
    years_experience = models.PositiveSmallIntegerField(default=5)
    short_quote = models.CharField(max_length=160, blank=True, help_text="Short signature quote for cards")

    def __str__(self):
        return f"Teacher: {self.user.get_full_name() or self.user.email}"
