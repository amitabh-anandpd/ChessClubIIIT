import random
from .models import TournamentMatch

def generate_pairings(tournament, users):
    if tournament.pairing_type == 'RANDOM':
        return random_pairings(users)
    if tournament.pairing_type == 'ROUND_ROBIN':
        return round_robin(users)
    if tournament.pairing_type == 'SWISS':
        return swiss_pairings(tournament, users)
    if tournament.pairing_type == 'KNOCKOUT':
        return knockout_pairings(tournament, users)
    return []

def random_pairings(users):
    users = list(users)
    random.shuffle(users)
    return [(users[i], users[i+1]) for i in range(0, len(users)-1, 2)]

def round_robin(users):
    users = list(users)
    pairings = []
    for i in range(len(users)):
        for j in range(i+1, len(users)):
            pairings.append((users[i], users[j]))
    return pairings

def swiss_pairings(tournament, users):

    users = list(users)
    
    if len(users) < 2:
        return []
    
    
    existing_matches = TournamentMatch.objects.filter(tournament=tournament)
    
    
    if not existing_matches.exists():
        random.shuffle(users)
        pairings = [(users[i], users[i+1]) for i in range(0, len(users)-1, 2)]
        return pairings
    
    
    user_scores = {}
    for user in users:
        wins = existing_matches.filter(result='PLAYER1', player1=user).count() + \
               existing_matches.filter(result='PLAYER2', player2=user).count()
        draws = existing_matches.filter(result='DRAW', player1=user).count() + \
                existing_matches.filter(result='DRAW', player2=user).count()
        user_scores[user] = wins + (draws * 0.5)
    
    
    sorted_users = sorted(users, key=lambda u: user_scores[u], reverse=True)
    
    
    previous_pairings = set()
    for match in existing_matches:
        pair = tuple(sorted([match.player1.id, match.player2.id]))
        previous_pairings.add(pair)
    
    
    pairings = []
    paired = set()
    
    for i, user1 in enumerate(sorted_users):
        if user1 in paired:
            continue
        
        
        for j in range(i+1, len(sorted_users)):
            user2 = sorted_users[j]
            if user2 in paired:
                continue
            
            pair = tuple(sorted([user1.id, user2.id]))
            if pair not in previous_pairings:
                pairings.append((user1, user2))
                paired.add(user1)
                paired.add(user2)
                break
    
    return pairings

def knockout_pairings(tournament, users):

    users = list(users)
    
    if len(users) < 2:
        return []
    
    existing_matches = TournamentMatch.objects.filter(tournament=tournament)
    
    
    if not existing_matches.exists():
        random.shuffle(users)  
        pairings = [(users[i], users[i+1]) for i in range(0, len(users)-1, 2)]
        return pairings
    
    
    latest_matches = existing_matches.order_by('-scheduled_at')
    
    if not latest_matches.exists():
        return []
    
    
    latest_time = latest_matches.first().scheduled_at
    current_round = latest_matches.filter(scheduled_at=latest_time)
    
    
    incomplete = current_round.filter(result='PENDING')
    if incomplete.exists():
        return []  
    
    
    winners = []
    for match in current_round:
        if match.result == 'PLAYER1':
            winners.append(match.player1)
        elif match.result == 'PLAYER2':
            winners.append(match.player2)
        
        
    
    if len(winners) < 2:
        return []  
    
    
    pairings = [(winners[i], winners[i+1]) for i in range(0, len(winners)-1, 2)]
    return pairings

def get_tournament_standings(tournament):

    from .models import TournamentRegistration
    
    users = [r.user for r in tournament.registrations.all()]
    matches = TournamentMatch.objects.filter(tournament=tournament)
    
    standings = []
    for user in users:
        wins = matches.filter(result='PLAYER1', player1=user).count() + \
               matches.filter(result='PLAYER2', player2=user).count()
        losses = matches.filter(result='PLAYER2', player1=user).count() + \
                 matches.filter(result='PLAYER1', player2=user).count()
        draws = matches.filter(result='DRAW', player1=user).count() + \
                matches.filter(result='DRAW', player2=user).count()
        
        points = wins + (draws * 0.5)
        
        standings.append({
            'user': user,
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'points': points,
            'games': wins + losses + draws
        })
    
    
    standings.sort(key=lambda x: (x['points'], x['wins']), reverse=True)
    
    return standings