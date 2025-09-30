from django.apps import AppConfig
import os

class LeaderboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'leaderboard'
    path = os.path.dirname(os.path.abspath(__file__))