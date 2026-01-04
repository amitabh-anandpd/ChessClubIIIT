from django.urls import path
from . import views

urlpatterns = [
    path('register/<int:tournament_id>/', views.toggle_registration, name='toggle_registration'),
    path('generate/<int:tournament_id>/', views.generate_matches, name='generate_matches'),
    path('<int:tournament_id>/', views.tournament_detail, name='tournament_detail'),
]
