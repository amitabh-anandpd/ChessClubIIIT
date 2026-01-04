from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone

import json

class Match(models.Model):
    STATUS_CHOICES = [
        ('WAIT', 'Waiting'),
        ('LIVE', 'Live'),
        ('END', 'Ended')
    ]
    
    RESULT_CHOICES = [
        ('1-0', 'White Wins'),
        ('0-1', 'Black Wins'),
        ('1/2-1/2', 'Draw'),
        ('*', 'Ongoing')
    ]
    

    player_white = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='matches_white',
        null = True,
        blank=True
    )
    player_black = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='matches_black',
        null = True,
        blank = True
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='WAIT')
    current_fen = models.TextField(default='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    move_history = models.JSONField(default=list)
    scheduled_start = models.DateTimeField(null=True, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    result = models.CharField(max_length=10, choices=RESULT_CHOICES, default='*')
    
    
    white_connected = models.BooleanField(default=False)
    black_connected = models.BooleanField(default=False)
    
    def __str__(self):
        white_name = self.player_white.username if self.player_white else "Waiting"
        black_name = self.player_black.username if self.player_black else "Waiting"
        return f"{white_name} vs {black_name}"
    
    def add_move(self, move_san, move_from, move_to, fen):
        move_data = {
            'san': move_san,
            'from': move_from,
            'to': move_to,
            'fen': fen
        }
        if not isinstance(self.move_history, list):
            self.move_history = []
        self.move_history.append(move_data)
        self.current_fen = fen
        self.save()
    
    def get_current_turn(self):
        
        parts = self.current_fen.split()
        return 'white' if parts[1] == 'w' else 'black'
    
    def can_join(self, user):
        if self.scheduled_start and timezone.now() < self.scheduled_start:
            return False
        if self.status != 'WAIT':
            return False
        if not self.player_white or not self.player_black:
            return True
        return False
    
    def join_as_player(self, user):
        if not self.player_white:
            self.player_white = user
        elif not self.player_black:
            self.player_black = user
            self.status = 'LIVE'  
        self.save()
        return self.get_player_color(user)
    
    def get_player_color(self, user):
        if self.player_white == user:
            return 'white'
        elif self.player_black == user:
            return 'black'
        return None