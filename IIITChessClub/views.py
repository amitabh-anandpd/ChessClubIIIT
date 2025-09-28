from django.conf import settings
from django.shortcuts import render, redirect
import json


from dotenv import load_dotenv
env_path = settings.BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)


def home(request):
    return render(request, 'home.html')

def leaderboard(request):
    return render(request, 'leaderboard.html')

def profile(request):
    return render(request, 'profile.html')