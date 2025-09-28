from . import views
from django.urls import path, include

urlpatterns = [
    path('profile/<str:username>', views.profile, name='profile'),
]