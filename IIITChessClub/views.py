from django.conf import settings
from django.shortcuts import render, redirect
import json
from accounts.models import User, UserProfile


from dotenv import load_dotenv
env_path = settings.BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)


def home(request):
    top_users = User.objects.select_related("profile").order_by("profile__rank")[:5]
    return render(request, 'home.html', {"top_users": top_users})

def profile(request):
    return render(request, 'profile.html')

def tournaments(request):
    return render(request, 'tournaments.html')

def newsletters(request):
    return render(request, 'newsletters.html')