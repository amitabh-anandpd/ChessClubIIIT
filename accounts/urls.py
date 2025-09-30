from . import views
from django.urls import path, include

urlpatterns = [
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('profile/', views.profile, name="profile"),
    path('api/profiles/', views.api_profiles, name='api_profiles'),
]