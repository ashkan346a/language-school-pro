from django.db import models
from django.utils import timezone
import uuid


class Enrollment(models.Model):
    STATUS = [
        ('pending', 'Pending Approval'),
        ('active', 'Active — In Orbit'),
        ('completed', 'Mission Complete'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]
    student = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey('catalog.Course', on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=10, choices=STATUS, default='active')
    enrolled_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percent = models.PositiveSmallIntegerField(default=0)
    final_score = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-enrolled_at']

    def __str__(self):
        return f"{self.student.email} → {self.course.title} ({self.status})"

    def recalculate_progress(self):
        total = self.course.modules.count() * 1  # simplistic; can be lesson count
        if total == 0:
            self.progress_percent = 100 if self.status == 'completed' else 0
        else:
            done = self.lessonprogress_set.filter(is_completed=True).count()
            self.progress_percent = min(100, int((done / max(1, total)) * 100))
        if self.progress_percent >= 100 and self.status != 'completed':
            self.status = 'completed'
            self.completed_at = timezone.now()
        self.save(update_fields=['progress_percent', 'status', 'completed_at'])


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    lesson = models.ForeignKey('catalog.Lesson', on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    seconds_spent = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('enrollment', 'lesson')

    def mark_complete(self):
        if not self.is_completed:
            self.is_completed = True
            self.completed_at = timezone.now()
            self.save()
            self.enrollment.recalculate_progress()


class Assignment(models.Model):
    lesson = models.ForeignKey('catalog.Lesson', on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=160)
    instructions = models.TextField()
    due_date = models.DateTimeField(null=True, blank=True)
    max_points = models.PositiveSmallIntegerField(default=100)

    def __str__(self):
        return f"Assignment: {self.title}"


class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    file = models.FileField(upload_to='assignments/submissions/', blank=True, null=True)
    notes = models.TextField(blank=True)
    score = models.PositiveSmallIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Submission for {self.assignment.title} by {self.enrollment.student.email}"


class Certificate(models.Model):
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='certificate')
    certificate_number = models.CharField(max_length=32, unique=True, editable=False)
    issued_at = models.DateTimeField(default=timezone.now)
    pdf = models.FileField(upload_to='certificates/generated/', blank=True, null=True)
    template_version = models.CharField(max_length=20, default='cosmic-v1')
    is_valid = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            self.certificate_number = f"AET-{uuid.uuid4().hex[:12].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Certificate {self.certificate_number} — {self.enrollment}"
