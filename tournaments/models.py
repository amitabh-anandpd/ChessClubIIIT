from django.db import models
from django.utils import timezone
from accounts.models import User

class Tournament(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
    
    def to_dict(self, include_matches=False):
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
        if include_matches:
            data["matches"] = [match.to_dict() for match in self.matches.all()]
        return data
    
    class Meta:
        ordering = ['-start_date']


class Match(models.Model):
    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name='matches'
    )

    player1 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='matches_as_player1'
    )
    player2 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='matches_as_player2'
    )
    
    fen = models.TextField(null=True, blank=True)

    winner = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True, related_name='matches_won'
    )
    result = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('DRAW', 'Draw'),
            ('PLAYER1', 'Player 1 Won'),
            ('PLAYER2', 'Player 2 Won'),
        ],
        default='PENDING'
    )

    scheduled_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.tournament.name}: {self.player1.username} vs {self.player2.username}"

    def to_dict(self):
        return {
            "id": self.id,
            "tournament_id": self.tournament.id,
            "tournament_name": self.tournament.name,
            "player1": self.player1.to_dict(),
            "player2": self.player2.to_dict(),
            "winner": self.winner.to_dict() if self.winner else None,
            "result": self.result,
            "scheduled_at": self.scheduled_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
    
    class Meta:
        ordering = ['-scheduled_at']
        unique_together = ('tournament', 'player1', 'player2')

class TournamentResult(models.Model):
    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name="results"
    )
    player = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="tournament_results"
    )
    position = models.IntegerField(blank=True, null=True)
    points = models.FloatField(default=0)
    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.player.username} - {self.tournament.name} ({self.position or 'N/A'})"

    def badge_class(self):
        if self.position == 1:
            return "badge-success"
        elif self.position == 2:
            return "badge-warning"
        elif self.position == 3:
            return "badge-warning"
        else:
            return "badge-secondary"

    def result_text(self):
        if self.position:
            if self.position == 1:
                return "1st Place"
            elif self.position == 2:
                return "2nd Place"
            elif self.position == 3:
                return "3rd Place"
            else:
                return f"{self.position}th Place"
        return "Participant"
