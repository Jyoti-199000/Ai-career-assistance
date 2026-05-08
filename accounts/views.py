"""
Accounts views — JWT authentication, user registration, profile
management, notifications, and settings.
"""

import json
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .models import UserProfile, UserSkill, UserActivity, Notification
from .serializers import (
    UserRegistrationSerializer,
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    ChangePasswordSerializer,
    UserSkillSerializer,
    UserActivitySerializer,
    NotificationSerializer,
)


# ─── Page Views ───────────────────────────────────────────────

def signup_page(request):
    """Render signup page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/signup.html')


def login_page(request):
    """Render login page."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/login.html')


def forgot_password_page(request):
    """Render forgot password page."""
    return render(request, 'accounts/forgot_password.html')


@login_required(login_url='/auth/login/')
def profile_page(request):
    """Render user profile page."""
    return render(request, 'accounts/profile.html')


@login_required(login_url='/auth/login/')
def settings_page(request):
    """Render user settings page."""
    return render(request, 'accounts/settings.html')


# ─── API: Authentication ─────────────────────────────────────

@api_view(['POST'])
@permission_classes([AllowAny])
def api_signup(request):
    """Register a new user and return JWT tokens."""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        # Log the activity
        if hasattr(user, 'profile'):
            UserActivity.objects.create(
                profile=user.profile,
                activity_type='login',
                title='Account Created',
                description='Welcome to Edumart! Your account has been created.',
            )

        return Response({
            'success': True,
            'message': 'Account created successfully!',
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            },
        }, status=status.HTTP_201_CREATED)

    return Response({
        'success': False,
        'errors': serializer.errors,
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """Authenticate user and return JWT tokens."""
    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')
    remember_me = request.data.get('remember_me', False)

    if not username or not password:
        return Response({
            'success': False,
            'errors': {'detail': 'Username and password are required.'},
        }, status=status.HTTP_400_BAD_REQUEST)

    # Allow login with email or username
    if '@' in username:
        try:
            user_obj = User.objects.get(email__iexact=username)
            username = user_obj.username
        except User.DoesNotExist:
            return Response({
                'success': False,
                'errors': {'detail': 'Invalid email or password.'},
            }, status=status.HTTP_401_UNAUTHORIZED)

    user = authenticate(request, username=username, password=password)
    if user is None:
        return Response({
            'success': False,
            'errors': {'detail': 'Invalid credentials.'},
        }, status=status.HTTP_401_UNAUTHORIZED)

    # Create Django session too (for template views)
    login(request, user)

    refresh = RefreshToken.for_user(user)

    # Update streak
    if hasattr(user, 'profile'):
        profile = user.profile
        profile.last_active = timezone.now()
        profile.save(update_fields=['last_active'])

        UserActivity.objects.create(
            profile=profile,
            activity_type='login',
            title='Logged In',
            description='User logged in to the platform.',
        )

    return Response({
        'success': True,
        'message': 'Login successful!',
        'tokens': {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        },
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
        },
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """Blacklist the refresh token and logout."""
    try:
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
    except Exception:
        pass

    logout(request)
    return Response({'success': True, 'message': 'Logged out successfully.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def api_token_refresh(request):
    """Refresh JWT access token."""
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response(
            {'error': 'Refresh token required.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    try:
        refresh = RefreshToken(refresh_token)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    except Exception:
        return Response(
            {'error': 'Invalid or expired refresh token.'},
            status=status.HTTP_401_UNAUTHORIZED,
        )


# ─── API: Profile ────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_profile(request):
    """Get current user's profile."""
    profile = request.user.profile
    serializer = UserProfileSerializer(profile)
    return Response(serializer.data)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def api_profile_update(request):
    """Update current user's profile."""
    profile = request.user.profile
    serializer = UserProfileUpdateSerializer(
        profile, data=request.data, partial=True,
    )
    if serializer.is_valid():
        serializer.save()

        UserActivity.objects.create(
            profile=profile,
            activity_type='profile_updated',
            title='Profile Updated',
            description='You updated your profile information.',
        )

        return Response({
            'success': True,
            'message': 'Profile updated successfully!',
            'profile': UserProfileSerializer(profile).data,
        })
    return Response({
        'success': False,
        'errors': serializer.errors,
    }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_avatar_upload(request):
    """Upload user avatar image."""
    if 'avatar' not in request.FILES:
        return Response(
            {'error': 'No avatar file provided.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    profile = request.user.profile
    profile.avatar = request.FILES['avatar']
    profile.save(update_fields=['avatar'])
    return Response({
        'success': True,
        'message': 'Avatar updated!',
        'avatar_url': profile.avatar.url if profile.avatar else None,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_change_password(request):
    """Change user password."""
    serializer = ChangePasswordSerializer(
        data=request.data, context={'request': request},
    )
    if serializer.is_valid():
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({
            'success': True,
            'message': 'Password changed successfully!',
        })
    return Response({
        'success': False,
        'errors': serializer.errors,
    }, status=status.HTTP_400_BAD_REQUEST)


# ─── API: Skills ──────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_skills_list(request):
    """List all user skills."""
    skills = request.user.profile.user_skills.all()
    serializer = UserSkillSerializer(skills, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_skill_add(request):
    """Add a new skill."""
    serializer = UserSkillSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(profile=request.user.profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_skill_delete(request, skill_id):
    """Delete a skill."""
    try:
        skill = request.user.profile.user_skills.get(id=skill_id)
        skill.delete()
        return Response({'success': True, 'message': 'Skill removed.'})
    except UserSkill.DoesNotExist:
        return Response(
            {'error': 'Skill not found.'},
            status=status.HTTP_404_NOT_FOUND,
        )


# ─── API: Activity & Notifications ───────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_activity_list(request):
    """Get user activity timeline."""
    activities = request.user.profile.activities.all()[:20]
    serializer = UserActivitySerializer(activities, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_notifications(request):
    """Get user notifications."""
    notifications = request.user.profile.notifications.all()[:20]
    serializer = NotificationSerializer(notifications, many=True)
    unread = request.user.profile.notifications.filter(is_read=False).count()
    return Response({
        'notifications': serializer.data,
        'unread_count': unread,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_notification_read(request, pk):
    """Mark a notification as read."""
    try:
        notification = request.user.profile.notifications.get(pk=pk)
        notification.is_read = True
        notification.save(update_fields=['is_read'])
        return Response({'success': True})
    except Notification.DoesNotExist:
        return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_notifications_read_all(request):
    """Mark all notifications as read."""
    request.user.profile.notifications.filter(is_read=False).update(is_read=True)
    return Response({'success': True, 'message': 'All notifications marked as read.'})


# ─── API: Dashboard Stats ────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_dashboard_stats(request):
    """Get dashboard statistics for the current user."""
    user = request.user
    profile = user.profile

    # Get or create career progress
    from core.models import CareerProgress, ResumeAnalysis, SavedRoadmap, InterviewSession, SavedCourse
    progress, _ = CareerProgress.objects.get_or_create(user=user)

    # Counts
    resume_count = ResumeAnalysis.objects.filter(user=user).count()
    roadmap_count = SavedRoadmap.objects.filter(user=user).count()
    interview_count = InterviewSession.objects.filter(user=user).count()
    course_count = SavedCourse.objects.filter(user=user).count()
    skills_count = profile.user_skills.count()

    # Recent activity
    recent = UserActivity.objects.filter(profile=profile)[:5]
    recent_data = UserActivitySerializer(recent, many=True).data

    # Unread notifications count
    unread_notifs = profile.notifications.filter(is_read=False).count()

    return Response({
        'user': {
            'username': user.username,
            'first_name': user.first_name,
            'full_name': profile.full_name,
            'avatar': profile.avatar.url if profile.avatar else None,
            'streak': profile.streak_count,
            'completion': profile.completion_percentage,
        },
        'stats': {
            'resumes_analyzed': resume_count,
            'roadmaps_created': roadmap_count,
            'interviews_completed': interview_count,
            'courses_saved': course_count,
            'skills_count': skills_count,
            'overall_score': progress.overall_score,
        },
        'recent_activity': recent_data,
        'unread_notifications': unread_notifs,
    })
