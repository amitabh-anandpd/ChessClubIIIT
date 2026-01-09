from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Tournament, TournamentRegistration, TournamentMatch
from .services import generate_pairings, get_tournament_standings
from django.utils.timezone import now
from django.views.decorators.http import require_POST
from django.contrib import messages

def is_manager(user):
    return user.is_superuser

@require_POST
@login_required
def toggle_registration(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    reg, created = TournamentRegistration.objects.get_or_create(
        user=request.user, 
        tournament=tournament
    )
    if not created:
        reg.delete()
        messages.info(request, "You have unregistered from the tournament.")
    else:
        messages.success(request, "You have registered for the tournament!")
    return redirect(request.META.get('HTTP_REFERER', 'tournaments'))

@require_POST
@user_passes_test(is_manager)
def generate_matches(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    
    
    is_multi_round = tournament.is_multi_round
    
    
    if not is_multi_round:
        if TournamentMatch.objects.filter(tournament=tournament).exists():
            messages.warning(request, "Matches already generated for this tournament.")
            return redirect(request.META.get("HTTP_REFERER", "tournaments"))
    
    users = [r.user for r in tournament.registrations.all()]
    
    if len(users) < 2:
        messages.error(request, "Need at least 2 players to generate matches.")
        return redirect(request.META.get("HTTP_REFERER", "tournaments"))

    if tournament.pairing_type.startswith('CUSTOM'):
        messages.info(request, "Custom tournaments require manual match creation.")
        return redirect('tournaments')

    pairings = generate_pairings(tournament, users)
    
    if not pairings:
        if is_multi_round:
            messages.warning(request, "No pairings available. Complete existing matches first.")
        else:
            messages.warning(request, "Unable to generate pairings.")
        return redirect(request.META.get('HTTP_REFERER', 'tournaments'))
    
    
    if is_multi_round and not TournamentMatch.objects.filter(tournament=tournament).exists():
        tournament.current_round = 1
        tournament.save()
    
    
    for u1, u2 in pairings:
        TournamentMatch.objects.create(
            tournament=tournament, 
            player1=u1, 
            player2=u2,
            round_number=tournament.current_round
        )
    
    round_text = f" (Round {tournament.current_round})" if is_multi_round else ""
    messages.success(request, f"Generated {len(pairings)} match(es){round_text}.")
    return redirect(request.META.get('HTTP_REFERER', 'tournaments'))

@require_POST
@user_passes_test(is_manager)
def generate_next_round(request, tournament_id):
    """Generate next round for Swiss or Knockout tournaments"""
    tournament = get_object_or_404(Tournament, id=tournament_id)
    
    if not tournament.is_multi_round:
        messages.error(request, "This tournament doesn't support multiple rounds.")
        return redirect('tournament_detail', tournament_id=tournament_id)
    
    
    current_round_matches = TournamentMatch.objects.filter(
        tournament=tournament,
        round_number=tournament.current_round
    )
    
    if not current_round_matches.exists():
        messages.error(request, "No matches in current round. Generate initial matches first.")
        return redirect('tournament_detail', tournament_id=tournament_id)
    
    incomplete = current_round_matches.filter(result='PENDING')
    if incomplete.exists():
        messages.warning(request, f"Complete all {incomplete.count()} match(es) in Round {tournament.current_round} before generating next round.")
        return redirect('tournament_detail', tournament_id=tournament_id)
    
    
    tournament.current_round += 1
    tournament.save()
    
    users = [r.user for r in tournament.registrations.all()]
    pairings = generate_pairings(tournament, users)
    
    if not pairings:
        tournament.current_round -= 1
        tournament.save()
        messages.info(request, "Tournament complete! No more rounds to generate.")
        return redirect('tournament_detail', tournament_id=tournament_id)
    
    
    for u1, u2 in pairings:
        TournamentMatch.objects.create(
            tournament=tournament,
            player1=u1,
            player2=u2,
            round_number=tournament.current_round
        )
    
    messages.success(request, f"Generated Round {tournament.current_round} with {len(pairings)} match(es).")
    return redirect('tournament_detail', tournament_id=tournament_id)

def tournament_detail(request, tournament_id):
    tournament = get_object_or_404(Tournament, id=tournament_id)
    registered_ids = []
    if request.user.is_authenticated:
        registered_ids = list(
            request.user.tournament_registrations.values_list('tournament_id', flat=True)
        )
    
    
    all_matches = tournament.matches.all().order_by('-round_number', 'id')
    
    
    can_generate_next = False
    if tournament.is_multi_round:
        current_round_matches = all_matches.filter(round_number=tournament.current_round)
        if current_round_matches.exists():
            all_complete = not current_round_matches.filter(result='PENDING').exists()
            can_generate_next = all_complete
    
    
    standings = get_tournament_standings(tournament)
    
    
    matches_by_round = {}
    for match in all_matches:
        round_num = match.round_number
        if round_num not in matches_by_round:
            matches_by_round[round_num] = []
        matches_by_round[round_num].append(match)
    
    return render(request, 'tournament-details.html', {
        'tournament': tournament,
        'matches': all_matches,
        'matches_by_round': matches_by_round,
        'registrations': tournament.registrations.select_related('user'),
        'registered_ids': registered_ids,
        'today': now().date(),
        'can_generate_next': can_generate_next,
        'standings': standings,
        'is_manager': request.user.is_staff or request.user.is_superuser,
    })

def tournaments(request):
    upcoming_tournaments = Tournament.objects.all()
    if request.user.is_authenticated:
        registered_ids = set(
            TournamentRegistration.objects.filter(user=request.user)
            .values_list("tournament_id", flat=True)
        )
    else:
        registered_ids = set()
    tournaments_with_matches = set(
        TournamentMatch.objects.values_list("tournament_id", flat=True)
    )
    return render(request, 'tournaments.html', {
        "upcoming_tournaments": upcoming_tournaments,
        "registered_ids": registered_ids,
        'is_manager': request.user.is_staff or request.user.is_superuser,
        'tournaments_with_matches': tournaments_with_matches,
    })

@user_passes_test(is_manager)
def schedule_match(request, match_id):
    match = get_object_or_404(TournamentMatch, id=match_id)

    if request.method == "POST":
        match.scheduled_at = request.POST.get("datetime")
        match.time_minutes = request.POST.get("minutes")
        match.increment_seconds = request.POST.get("increment")
        match.save()
        messages.success(request, "Match scheduled successfully!")
        return redirect('tournament_detail', match.tournament.id)

    return render(request, "schedule-match.html", {
        "match": match
    })