from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, StudentProfile, TeacherProfile


@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):
    if created:
        # Default to student profile for new signups
        StudentProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profiles(sender, instance, **kwargs):
    if hasattr(instance, 'student_profile'):
        instance.student_profile.save()
    if hasattr(instance, 'teacher_profile'):
        instance.teacher_profile.save()
