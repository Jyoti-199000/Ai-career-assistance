"""
Serializers for the accounts app — handles user registration,
login, profile management, and related data.
"""

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from .models import (
    UserProfile, UserSkill, UserActivity,
    Achievement, UserAchievement, Notification,
)


class UserRegistrationSerializer(serializers.Serializer):
    """Handles user signup with validation."""

    username = serializers.CharField(min_length=3, max_length=30)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=30, required=False, default='')
    last_name = serializers.CharField(max_length=30, required=False, default='')
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError('This username is already taken.')
        return value.lower()

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('An account with this email already exists.')
        return value.lower()

    def validate_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer for nested representations."""

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class UserSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSkill
        fields = ['id', 'name', 'proficiency', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserProfileSerializer(serializers.ModelSerializer):
    """Full profile serializer with computed fields."""

    user = UserSerializer(read_only=True)
    skills = UserSkillSerializer(source='user_skills', many=True, read_only=True)
    completion_percentage = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'full_name', 'avatar', 'bio', 'phone',
            'location', 'date_of_birth', 'headline', 'experience_level',
            'education', 'career_interests', 'resume_file',
            'linkedin_url', 'github_url', 'twitter_url', 'portfolio_url',
            'theme', 'email_notifications', 'push_notifications',
            'profile_completed', 'onboarding_done', 'streak_count',
            'skills', 'completion_percentage',
            'last_active', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'user', 'profile_completed', 'streak_count',
            'last_active', 'created_at', 'updated_at',
        ]


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating profile fields."""

    first_name = serializers.CharField(max_length=30, required=False)
    last_name = serializers.CharField(max_length=30, required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'email',
            'bio', 'phone', 'location', 'date_of_birth',
            'headline', 'experience_level', 'education',
            'career_interests', 'linkedin_url', 'github_url',
            'twitter_url', 'portfolio_url', 'theme',
            'email_notifications', 'push_notifications',
        ]

    def update(self, instance, validated_data):
        # Update User model fields
        user = instance.user
        if 'first_name' in validated_data:
            user.first_name = validated_data.pop('first_name')
        if 'last_name' in validated_data:
            user.last_name = validated_data.pop('last_name')
        if 'email' in validated_data:
            new_email = validated_data.pop('email')
            if User.objects.exclude(pk=user.pk).filter(email__iexact=new_email).exists():
                raise serializers.ValidationError({'email': 'This email is already in use.'})
            user.email = new_email
        user.save()

        # Update profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    """Handles password change with validation."""

    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Current password is incorrect.')
        return value

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError(
                {'new_password_confirm': 'New passwords do not match.'}
            )
        return attrs


class UserActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivity
        fields = ['id', 'activity_type', 'title', 'description', 'metadata', 'created_at']
        read_only_fields = ['id', 'created_at']


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'name', 'description', 'icon', 'badge_type']


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)

    class Meta:
        model = UserAchievement
        fields = ['id', 'achievement', 'earned_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'title', 'message', 'is_read', 'action_url', 'created_at']
        read_only_fields = ['id', 'created_at']
