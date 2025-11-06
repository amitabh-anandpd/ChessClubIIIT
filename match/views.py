from django.shortcuts import render, get_object_or_404
from .models import Match

def match_view(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    return render(request, 'match/match.html', {'match': match})

def lobby_view(request):
    matches = Match.objects.filter(status='LIVE')
    return render(request, 'match/lobby.html', {'matches': matches})
