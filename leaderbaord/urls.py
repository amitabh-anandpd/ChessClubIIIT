from . import views
from django.urls import path, include

urlpatterns = [
    path('leaderboard', views.leaderboard, name='leaderboard'),
]