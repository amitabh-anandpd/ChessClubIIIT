import random

def generate_pairings(tournament, users):
    if tournament.pairing_type == 'RANDOM':
        return random_pairings(users)
    if tournament.pairing_type == 'ROUND_ROBIN':
        return round_robin(users)
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
