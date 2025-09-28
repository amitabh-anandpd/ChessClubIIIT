from django.conf import settings
from django.shortcuts import render, redirect

from .models import User


def profile(request, username):
    user = User.objects.filter(username=username).first()
    if not user:
        return redirect("/")
    return render(request, 'profile.html', context={"user":user})