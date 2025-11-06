from django.conf import settings
from django.shortcuts import render, redirect
from django.utils.timezone import now
import json
from accounts.models import User, UserProfile
from tournaments.models import Tournament
from newsletters.models import Newsletter


from dotenv import load_dotenv
env_path = settings.BASE_DIR / ".env"
if env_path.exists():
    load_dotenv(env_path)


def home(request):
    next_tournament = (
        Tournament.objects
        .filter(start_date__gte=now().date())
        .order_by('start_date')
        .first()
    )
    latest_newsletter = (
        Newsletter.objects
        .order_by('-published_date')
        .first()
    )
    top_users = User.objects.select_related("profile").order_by("-profile__rating")[:5]
    return render(request, 'home.html', {"top_users": top_users, "next_tournament": next_tournament, "latest_newsletter": latest_newsletter})

def tournaments(request):
    upcoming_tournaments = Tournament.objects.filter(
        is_active=True,
        start_date__gte=now().date()
    ).order_by('start_date')
    return render(request, 'tournaments.html', {"upcoming_tournaments": upcoming_tournaments})

def login(request):
    if request.user.is_authenticated:
        return redirect('/')
    return render(request, 'login.html')

def match(request):
    return render(request, 'match.html')