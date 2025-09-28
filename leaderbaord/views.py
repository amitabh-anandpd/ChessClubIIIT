from django.conf import settings
from django.shortcuts import render, redirect

from accounts.models import User

def leaderboard(request):
    users = User.objects.all().order_by('rank')
    return render(request, 'leaderboard.html', {"users": users})
    