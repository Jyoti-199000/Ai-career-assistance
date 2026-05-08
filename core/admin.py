"""
Admin registration for core models.
"""

from django.contrib import admin
from .models import (
    CareerRecommendation, ResumeAnalysis, SavedRoadmap,
    InterviewSession, SavedCourse, UserNote, ChatMessage,
    CareerProgress, RecentlyViewedCareer,
)


@admin.register(CareerRecommendation)
class CareerRecommendationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'match_score', 'is_favorite', 'created_at']
    list_filter = ['is_favorite', 'growth_outlook']
    search_fields = ['title', 'user__username']


@admin.register(ResumeAnalysis)
class ResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'overall_score', 'created_at']
    list_filter = ['overall_score']


@admin.register(SavedRoadmap)
class SavedRoadmapAdmin(admin.ModelAdmin):
    list_display = ['goal', 'user', 'progress', 'is_active', 'created_at']
    list_filter = ['is_active']


@admin.register(InterviewSession)
class InterviewSessionAdmin(admin.ModelAdmin):
    list_display = ['role', 'user', 'score', 'completed', 'created_at']
    list_filter = ['completed']


@admin.register(SavedCourse)
class SavedCourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'platform', 'user', 'progress', 'completed']
    list_filter = ['platform', 'completed']


@admin.register(UserNote)
class UserNoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'is_pinned', 'updated_at']


@admin.register(CareerProgress)
class CareerProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'overall_score', 'resumes_analyzed', 'interviews_completed']


@admin.register(RecentlyViewedCareer)
class RecentlyViewedCareerAdmin(admin.ModelAdmin):
    list_display = ['career_title', 'user', 'viewed_at']
