from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.db.models import Q, Avg
from django.views.decorators.http import require_GET

from .models import User, UserProfile
from tournaments.models import TournamentResult, Match

def user_profile(request, username):
    user = User.objects.filter(username=username).first()
    results = (
        TournamentResult.objects
        .filter(player=user)
        .select_related("tournament")
        .order_by("-tournament__start_date")
    )

    tournaments = []
    for r in results:
        tournaments.append({
            "name": r.tournament.name,
            "date": r.tournament.start_date,
            "result": r.result_text(),
            "result_class": r.badge_class(),
        })
        
    matches_obj = user.matches
    matches = []
    for m in matches_obj:
        opponent = m.player2 if m.player1 == user else m.player1
        
        if m.result == 'DRAW':
            result_class = "badge-warning"
        elif (m.result == 'PLAYER1' and m.player1 == user) or (m.result == 'PLAYER2' and m.player2 == user):
            result_class = "badge-success"
        elif m.result != 'PENDING':
            result_class = "badge-danger"
        else:
            result_class = "badge-secondary"
        matches.append({
            "result_class": result_class,
            "result": m.result,
            "opponent": opponent,
            "date": m.scheduled_at,
            "fen": getattr(m, "fen", None),
        })
    if not user:
        return redirect("/")
    return render(request, 'profile_view.html', context={"user":user, "tournaments":tournaments, "matches": matches})

def profile(request):
    users = User.objects.all()
    active_count = len(users)
    avg_rating = int(UserProfile.objects.aggregate(avg=Avg('rating'))['avg'])
    match_count = len(Match.objects.all())
    return render(request, 'profile.html', {"active_count": active_count, "avg_rating": avg_rating, "match_count": match_count})

@require_GET
def api_profiles(request):
    search = request.GET.get('search', '')
    rating = request.GET.get('rating', '')

    users = User.objects.select_related('profile').all()

    if search:
        users = users.filter(username__icontains=search)

    if rating:
        if rating == '2000+':
            users = users.filter(profile__rating__gte=2000)
        elif rating == '1800-1999':
            users = users.filter(profile__rating__gte=1800, profile__rating__lte=1999)
        elif rating == '1600-1799':
            users = users.filter(profile__rating__gte=1600, profile__rating__lte=1799)
        elif rating == '1400-1599':
            users = users.filter(profile__rating__gte=1400, profile__rating__lte=1599)
        elif rating == '<1400':
            users = users.filter(profile__rating__lt=1400)

    data = []
    for index, user in enumerate(users, start=1):
        data.append({
            "username": user.username,
            "name": f"{user.first_name} {user.last_name}".strip() or user.username,
            "rating": user.profile.rating,
            "rank": index,  # ✅ dynamic rank
            "profile_url": f"/profile/{user.username}/",
        })
    return JsonResponse({"profiles": data})