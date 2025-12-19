from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Match
import json

def match_view(request, match_id):
    """Render match page"""
    match = get_object_or_404(Match, id=match_id)
    
    
    player_color = None
    if request.user.is_authenticated:
        if match.player_white == request.user:
            player_color = 'white'
        elif match.player_black == request.user:
            player_color = 'black'
        else:
            player_color = 'spectator'
    else:
        player_color = 'spectator'
    
    context = {
        'match': match,
        'player_color': player_color,
        'match_id': match_id,
    }
    
    return render(request, 'match.html', context)

def lobby_view(request):
    """Display match lobby with available matches"""
    
    waiting_matches = Match.objects.filter(status='WAIT').order_by('-start_time')
    live_matches = Match.objects.filter(status='LIVE').order_by('-start_time')[:10]
    recent_matches = Match.objects.filter(status='END').order_by('-end_time')[:10]
    
    context = {
        'waiting_matches': waiting_matches,
        'live_matches': live_matches,
        'recent_matches': recent_matches,
    }
    
    return render(request, 'lobby.html', context)

@login_required
@require_http_methods(["POST"])
def create_match(request):
    """Create a new match"""
    try:
        
        match = Match.objects.create(
            player_white=request.user,
            status='WAIT',
            current_fen='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        )
        
        return JsonResponse({
            'success': True,
            'match_id': match.id,
            'redirect_url': f'/match/{match.id}/'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
@require_http_methods(["POST"])
def join_match(request, match_id):
    """Join an existing match"""
    try:
        match = get_object_or_404(Match, id=match_id)
        
        
        if match.status != 'WAIT':
            return JsonResponse({
                'success': False,
                'error': 'Match is not available to join'
            }, status=400)
        
        
        if match.player_white == request.user or match.player_black == request.user:
            return JsonResponse({
                'success': True,
                'match_id': match.id,
                'redirect_url': f'/match/{match.id}/'
            })
        
        
        if not match.player_black:
            match.player_black = request.user
            match.status = 'LIVE'
            match.save()
            
            return JsonResponse({
                'success': True,
                'match_id': match.id,
                'redirect_url': f'/match/{match.id}/'
            })
        
        if not match.player_white:
            match.player_white = request.user
            match.status = 'LIVE'
            match.save()
            
            return JsonResponse({
                'success': True,
                'match_id': match.id,
                'redirect_url': f'/match/{match.id}/'
            })
        
        return JsonResponse({
            'success': False,
            'error': 'Match is full'
        }, status=400)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@require_http_methods(["GET"])
def match_state(request, match_id):
    """Get current match state (for AJAX requests)"""
    try:
        match = get_object_or_404(Match, id=match_id)
        
        return JsonResponse({
            'success': True,
            'match': {
                'id': match.id,
                'status': match.status,
                'result': match.result,
                'current_fen': match.current_fen,
                'move_history': match.move_history,
                'player_white': match.player_white.username if match.player_white else None,
                'player_black': match.player_black.username if match.player_black else None,
                'white_connected': match.white_connected,
                'black_connected': match.black_connected,
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@login_required
@require_http_methods(["POST"])
def leave_match(request, match_id):
    """Leave a match (resign if game is live)"""
    try:
        match = get_object_or_404(Match, id=match_id)
        
        
        if match.status == 'WAIT' and match.player_white == request.user:
            match.delete()
            return JsonResponse({
                'success': True,
                'message': 'Match cancelled'
            })
        
        
        if match.status == 'LIVE':
            if match.player_white == request.user:
                match.result = '0-1'
                match.status = 'END'
                match.end_time = timezone.now()
                match.save()
            elif match.player_black == request.user:
                match.result = '1-0'
                match.status = 'END'
                match.end_time = timezone.now()
                match.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Left match'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@require_http_methods(["GET"])
def lobby_data(request):
    """Get lobby data for AJAX updates"""
    try:
        waiting_matches = Match.objects.filter(status='WAIT').values(
            'id', 'player_white__username', 'start_time'
        ).order_by('-start_time')
        
        live_matches = Match.objects.filter(status='LIVE').values(
            'id', 'player_white__username', 'player_black__username', 'start_time'
        ).order_by('-start_time')[:10]
        
        return JsonResponse({
            'success': True,
            'waiting_matches': list(waiting_matches),
            'live_matches': list(live_matches),
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)