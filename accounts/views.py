from django.conf import settings
from django.shortcuts import render, redirect
from django.db.models import Q

from .models import User
from tournaments.models import TournamentResult

def profile(request, username):
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