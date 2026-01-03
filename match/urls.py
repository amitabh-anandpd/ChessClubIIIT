from django.urls import path
from . import views

urlpatterns = [
    
    path('lobby/', views.lobby_view, name='match_lobby'),
    path('<int:match_id>/', views.match_view, name='match_view'),
    
    
    path('api/create/', views.create_match, name='create_match'),
    path('api/<int:match_id>/join/', views.join_match, name='join_match'),
    path('api/<int:match_id>/leave/', views.leave_match, name='leave_match'),
    path('api/<int:match_id>/state/', views.match_state, name='match_state'),
    path('api/lobby/data/', views.lobby_data, name='lobby_data'),
]