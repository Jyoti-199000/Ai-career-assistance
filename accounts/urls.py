"""
URL configuration for accounts app.
Includes page views and API endpoints.
"""

from django.urls import path
from . import views

urlpatterns = [
    # ─── Page Routes ──────────────────────────────────────
    path('signup/', views.signup_page, name='signup'),
    path('login/', views.login_page, name='login'),
    path('forgot-password/', views.forgot_password_page, name='forgot_password'),
    path('profile/', views.profile_page, name='profile'),
    path('settings/', views.settings_page, name='settings'),

    # ─── Auth API ─────────────────────────────────────────
    path('api/signup/', views.api_signup, name='api_signup'),
    path('api/login/', views.api_login, name='api_login'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/token/refresh/', views.api_token_refresh, name='api_token_refresh'),

    # ─── Profile API ─────────────────────────────────────
    path('api/profile/', views.api_profile, name='api_profile'),
    path('api/profile/update/', views.api_profile_update, name='api_profile_update'),
    path('api/profile/avatar/', views.api_avatar_upload, name='api_avatar_upload'),
    path('api/profile/change-password/', views.api_change_password, name='api_change_password'),

    # ─── Skills API ───────────────────────────────────────
    path('api/skills/', views.api_skills_list, name='api_skills_list'),
    path('api/skills/add/', views.api_skill_add, name='api_skill_add'),
    path('api/skills/<int:skill_id>/delete/', views.api_skill_delete, name='api_skill_delete'),

    # ─── Activity & Notifications API ─────────────────────
    path('api/activity/', views.api_activity_list, name='api_activity_list'),
    path('api/notifications/', views.api_notifications, name='api_notifications'),
    path('api/notifications/<int:pk>/read/', views.api_notification_read, name='api_notification_read'),
    path('api/notifications/read-all/', views.api_notifications_read_all, name='api_notifications_read_all'),

    # ─── Dashboard API ────────────────────────────────────
    path('api/dashboard/', views.api_dashboard_stats, name='api_dashboard_stats'),
]
