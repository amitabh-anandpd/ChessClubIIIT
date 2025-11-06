from django.db import models
from django.contrib.auth.models import User

class Match(models.Model):
    player_white = models.ForeignKey(User, on_delete=models.CASCADE, related_name='white_matches')
    player_black = models.ForeignKey(User, on_delete=models.CASCADE, related_name='black_matches')
    status = models.CharField(max_length=10, choices=[('WAIT', 'Waiting'), ('LIVE', 'Live'), ('END', 'Ended')])
    current_fen = models.TextField(default='')
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    result = models.CharField(max_length=10, blank=True)  # '1-0', '0-1', '½-½'

    def __str__(self):
        return f"{self.player_white} vs {self.player_black}"
