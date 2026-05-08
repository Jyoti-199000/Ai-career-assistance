"""
Accounts models — UserProfile and related user data models.
Extends Django's built-in User with a OneToOneField profile.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class UserProfile(models.Model):
    """Extended user profile with career-related fields."""

    EXPERIENCE_CHOICES = [
        ('beginner', 'Beginner (0-1 years)'),
        ('intermediate', 'Intermediate (1-3 years)'),
        ('advanced', 'Advanced (3-5 years)'),
        ('expert', 'Expert (5+ years)'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Personal info
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, default='')
    phone = models.CharField(max_length=20, blank=True, default='')
    location = models.CharField(max_length=100, blank=True, default='')
    date_of_birth = models.DateField(blank=True, null=True)

    # Professional info
    headline = models.CharField(max_length=200, blank=True, default='')
    experience_level = models.CharField(
        max_length=20, choices=EXPERIENCE_CHOICES,
        default='beginner',
    )
    education = models.TextField(blank=True, default='')
    career_interests = models.TextField(blank=True, default='')
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)

    # Social links
    linkedin_url = models.URLField(blank=True, default='')
    github_url = models.URLField(blank=True, default='')
    twitter_url = models.URLField(blank=True, default='')
    portfolio_url = models.URLField(blank=True, default='')

    # Preferences
    theme = models.CharField(
        max_length=10,
        choices=[('dark', 'Dark'), ('light', 'Light'), ('auto', 'Auto')],
        default='dark',
    )
    email_notifications = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)

    # Tracking
    profile_completed = models.BooleanField(default=False)
    onboarding_done = models.BooleanField(default=False)
    streak_count = models.PositiveIntegerField(default=0)
    last_active = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f'{self.user.username} — Profile'

    @property
    def full_name(self):
        return f'{self.user.first_name} {self.user.last_name}'.strip() or self.user.username

    @property
    def completion_percentage(self):
        """Calculate profile completion percentage."""
        fields = [
            bool(self.user.first_name),
            bool(self.user.last_name),
            bool(self.bio),
            bool(self.avatar),
            bool(self.headline),
            bool(self.education),
            bool(self.career_interests),
            bool(self.phone),
            bool(self.location),
            bool(self.linkedin_url or self.github_url),
            bool(self.resume_file),
            self.user_skills.exists(),
        ]
        return int((sum(fields) / len(fields)) * 100)


class UserSkill(models.Model):
    """Skills associated with a user profile."""

    PROFICIENCY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ]

    profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='user_skills',
    )
    name = models.CharField(max_length=100)
    proficiency = models.CharField(
        max_length=20, choices=PROFICIENCY_CHOICES, default='beginner',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = ['profile', 'name']

    def __str__(self):
        return f'{self.name} ({self.proficiency})'


class UserActivity(models.Model):
    """Track user activities for the activity timeline."""

    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('resume_analysis', 'Resume Analysis'),
        ('roadmap_generated', 'Roadmap Generated'),
        ('interview_completed', 'Interview Completed'),
        ('course_saved', 'Course Saved'),
        ('code_executed', 'Code Executed'),
        ('profile_updated', 'Profile Updated'),
        ('career_saved', 'Career Saved'),
        ('achievement_earned', 'Achievement Earned'),
    ]

    profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='activities',
    )
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default='')
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'User Activities'

    def __str__(self):
        return f'{self.profile.user.username}: {self.title}'


class Achievement(models.Model):
    """Achievement badges for gamification."""

    BADGE_TYPES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='fas fa-trophy')
    badge_type = models.CharField(max_length=20, choices=BADGE_TYPES, default='bronze')
    criteria = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['badge_type', 'name']

    def __str__(self):
        return f'{self.name} ({self.badge_type})'


class UserAchievement(models.Model):
    """Tracks achievements earned by users."""

    profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='achievements',
    )
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['profile', 'achievement']
        ordering = ['-earned_at']

    def __str__(self):
        return f'{self.profile.user.username} — {self.achievement.name}'


class Notification(models.Model):
    """User notification system."""

    NOTIFICATION_TYPES = [
        ('info', 'Info'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('achievement', 'Achievement'),
        ('system', 'System'),
    ]

    profile = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='notifications',
    )
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES, default='info',
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    action_url = models.CharField(max_length=500, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} — {"Read" if self.is_read else "Unread"}'
