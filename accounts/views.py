from django.conf import settings
from django.shortcuts import render, redirect

from .models import User
from tournaments.models import Tournament

def profile(request, username):
    user = User.objects.filter(username=username).first()
    tournaments = user.tournaments
    matches = user.matches
    if not user:
        return redirect("/")
    return render(request, 'profile.html', context={"user":user, "tournaments":tournaments, "matches": matches})