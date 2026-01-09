from django.urls import path
from . import views

urlpatterns = [
    path('register/<int:tournament_id>/', views.toggle_registration, name='toggle_registration'),
    path('generate/<int:tournament_id>/', views.generate_matches, name='generate_matches'),
    path('next-round/<int:tournament_id>/', views.generate_next_round, name='generate_next_round'),
    path('<int:tournament_id>/', views.tournament_detail, name='tournament_detail'),
    path('match/<int:match_id>/schedule/', views.schedule_match, name='schedule_match'),
    path('', views.tournaments, name='tournaments'),
]