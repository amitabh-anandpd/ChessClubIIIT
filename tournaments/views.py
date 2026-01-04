from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Tournament, TournamentRegistration, TournamentMatch
from .services import generate_pairings
from django.utils.timezone import now
from django.views.decorators.http import require_POST

def is_manager(user):
    return user.is_superuser

@require_POST
@login_required
def toggle_registration(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    reg, created = TournamentRegistration.objects.get_or_create(user=request.user, tournament=tournament)
    if not created:
        reg.delete()
    return redirect('tournaments')

@require_POST
@user_passes_test(is_manager)
def generate_matches(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    users = [r.user for r in tournament.registrations.all()]

    if tournament.pairing_type.startswith('CUSTOM'):
        return redirect('tournaments')

    pairings = generate_pairings(tournament, users)

    TournamentMatch.objects.filter(tournament=tournament).delete()
    for u1, u2 in pairings:
        TournamentMatch.objects.create(tournament=tournament, player1=u1, player2=u2)

    return redirect('tournaments')

def tournament_detail(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    return render(request, 'tournament-details.html', {'tournament': tournament})

def tournaments(request):
    upcoming_tournaments = Tournament.objects.filter(
        is_active=True,
        start_date__gte=now().date()
    ).order_by('start_date')
    if request.user.is_authenticated:
        registered_ids = set(
            TournamentRegistration.objects.filter(user=request.user)
            .values_list("tournament_id", flat=True)
        )
    else:
        registered_ids = set()
    return render(request, 'tournaments.html',
                  {"upcoming_tournaments": upcoming_tournaments,
                   "registered_ids": registered_ids,
                   })