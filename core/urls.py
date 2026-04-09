from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('resume/', views.resume_page, name='resume'),
    path('roadmap/', views.roadmap_page, name='roadmap'),
    path('interview/', views.interview_page, name='interview'),
    path('courses/', views.courses_page, name='courses'),
    path('editor/', views.editor_page, name='editor'),

    # API endpoints
    path('api/analyze-resume/', views.api_analyze_resume, name='api_analyze_resume'),
    path('api/generate-roadmap/', views.api_generate_roadmap, name='api_generate_roadmap'),
    path('api/interview/', views.api_interview, name='api_interview'),
    path('api/execute-code/', views.api_execute_code, name='api_execute_code'),
]
