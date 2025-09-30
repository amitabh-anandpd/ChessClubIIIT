from django.apps import AppConfig
import os

class TournamentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tournaments'
    path = os.path.dirname(os.path.abspath(__file__))