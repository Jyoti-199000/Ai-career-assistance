"""
Admin registration for accounts models.
"""

from django.contrib import admin
from .models import (
    UserProfile, UserSkill, UserActivity,
    Achievement, UserAchievement, Notification,
)


class UserSkillInline(admin.TabularInline):
    model = UserSkill
    extra = 0


class UserActivityInline(admin.TabularInline):
    model = UserActivity
    extra = 0
    readonly_fields = ['activity_type', 'title', 'created_at']
    max_num = 10


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'headline', 'experience_level', 'streak_count', 'last_active']
    list_filter = ['experience_level', 'theme', 'profile_completed']
    search_fields = ['user__username', 'user__email', 'headline']
    inlines = [UserSkillInline, UserActivityInline]


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name', 'badge_type', 'icon']
    list_filter = ['badge_type']


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['profile', 'achievement', 'earned_at']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'profile', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
