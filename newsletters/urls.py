from django.urls import path
from . import views

urlpatterns = [
    path('', views.newsletter_list, name='newsletters'),
    path('<slug:slug>/', views.newsletter_article, name='newsletter_article'),
]
