from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Tournament, TournamentRegistration, Match
from .services import generate_pairings

def is_manager(user):
    return user.is_superuser

@login_required
def toggle_registration(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    reg, created = TournamentRegistration.objects.get_or_create(user=request.user, tournament=tournament)
    if not created:
        reg.delete()
    return redirect('tournaments')

@user_passes_test(is_manager)
def generate_matches(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    users = [r.user for r in tournament.registrations.all()]

    if tournament.pairing_type.startswith('CUSTOM'):
        return redirect('tournaments')

    pairings = generate_pairings(tournament, users)

    Match.objects.filter(tournament=tournament).delete()
    for u1, u2 in pairings:
        Match.objects.create(tournament=tournament, player1=u1, player2=u2)

    return redirect('tournaments')

def tournament_detail(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    return render(request, 'tournament-detail.html', {'tournament': tournament})