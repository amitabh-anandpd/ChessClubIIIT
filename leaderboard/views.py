from django.conf import settings
from django.shortcuts import render, redirect
from django.db import transaction

from accounts.models import User

def leaderboard(request):
    users = User.objects.all().order_by('-profile__rating')
    leaderboard_data = []
    with transaction.atomic():
        for index, user in enumerate(users, start=1):
            profile = user.profile
            current_rank = index
            
            if profile.rank != current_rank:
                profile.last_rank = profile.rank or current_rank
                profile.rank = current_rank
                profile.save(update_fields=['rank', 'last_rank'])
                
            rank_change = (profile.last_rank or current_rank) - current_rank

            leaderboard_data.append({
                "user": user,
                "current_rank": current_rank,
                "rank_change": rank_change,
                "moved_up": current_rank < profile.last_rank,
                "moved_down": current_rank > profile.last_rank,
                "rating_change": profile.rating - profile.last_rating,
            })
    return render(request, 'leaderboard.html', {"leaderboard": leaderboard_data})
    