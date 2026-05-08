"""
Signals — auto-create UserProfile when a User is created.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile, Notification


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile automatically when a new User is created."""
    if created:
        profile = UserProfile.objects.create(user=instance)
        # Welcome notification
        Notification.objects.create(
            profile=profile,
            notification_type='success',
            title='Welcome to Edumart! 🎉',
            message='Your account has been created. Start by completing your profile and exploring our AI career tools.',
            action_url='/profile/',
        )


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save profile when user is saved."""
    if hasattr(instance, 'profile'):
        instance.profile.save()
