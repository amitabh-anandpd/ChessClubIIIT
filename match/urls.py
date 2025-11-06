from django.urls import path
from . import views

urlpatterns = [
    path('<int:match_id>/', views.match_view, name='match_view'),
    path('lobby/', views.lobby_view, name='match_lobby'),
]
