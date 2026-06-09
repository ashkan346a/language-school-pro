from django.db import models
from django.utils.text import slugify
from django.utils import timezone


LEVEL_CHOICES = [
    ('A1', 'A1 — Entry Vector'),
    ('A2', 'A2 — Launch Vector'),
    ('B1', 'B1 — Stable Orbit'),
    ('B2', 'B2 — Deep Trajectory'),
    ('C1', 'C1 — Deep Space'),
    ('C2', 'C2 — Command Level'),
]

FORMAT_CHOICES = [
    ('self_paced', 'Self-Paced Mission'),
    ('live_cohort', 'Live Cohort'),
    ('private', 'Private Command'),
]


class Course(models.Model):
    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=80, unique=True, blank=True)
    language = models.ForeignKey('core.Language', on_delete=models.PROTECT, related_name='courses')
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES, default='A1')
    subtitle = models.CharField(max_length=200, blank=True)
    description = models.TextField(help_text="Rich mission briefing. Supports Markdown.")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    currency = models.CharField(max_length=3, default='USD')
    duration_weeks = models.PositiveSmallIntegerField(default=8)
    format = models.CharField(max_length=20, choices=FORMAT_CHOICES, default='self_paced')
    max_enrollments = models.PositiveSmallIntegerField(default=24, help_text="0 = unlimited")
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', blank=True, null=True)
    what_you_will_learn = models.JSONField(default=list, blank=True, help_text="List of objectives, e.g. ['Master 1200 words', ...]")
    requirements = models.TextField(blank=True)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    instructor = models.ForeignKey('accounts.TeacherProfile', on_delete=models.SET_NULL, null=True, blank=True, related_name='courses_taught')
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-is_featured', '-published_at']

    def __str__(self):
        return f"{self.title} ({self.language.name} {self.level})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:70]
            self.slug = base
        super().save(*args, **kwargs)

    @property
    def display_price(self):
        if self.price == 0:
            return "Free"
        return f"{self.price} {self.currency}"


class Module(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=160)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('course', 'order')

    def __str__(self):
        return f"{self.course.title} — M{self.order}: {self.title}"


class Lesson(models.Model):
    CONTENT_TYPES = [
        ('text', 'Transmission (Text/Markdown)'),
        ('video', 'Video Briefing'),
        ('mixed', 'Mixed'),
    ]
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=160)
    order = models.PositiveIntegerField(default=0)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES, default='text')
    content = models.TextField(blank=True, help_text="Markdown or rich content for the lesson.")
    video_url = models.URLField(blank=True, help_text="YouTube/Vimeo or hosted URL")
    duration_min = models.PositiveSmallIntegerField(default=12)
    is_preview = models.BooleanField(default=False, help_text="Available without enrollment")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.module.title} / L{self.order}: {self.title}"
