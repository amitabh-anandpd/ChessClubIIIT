from django.db import models
from django.utils import timezone
from accounts.models import User

class Tournament(models.Model):
    name = models.CharField(max_length=200)
    PAIRING_TYPE_CHOICES = [
        ('RANDOM', 'Random (Tournament)'),
        ('ROUND_ROBIN', 'Round Robin'),
        ('CUSTOM_TOURNAMENT', 'Custom Tournament'),
        ('CUSTOM_ROUND_ROBIN', 'Custom Round Robin'),
    ]

    pairing_type = models.CharField(max_length=30, choices=PAIRING_TYPE_CHOICES, default='RANDOM')
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField(default=timezone.now)
    end_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    base_minutes = models.PositiveIntegerField(default=10)
    increment_seconds = models.PositiveIntegerField(default=0)

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
            "pairing_type": self.pairing_type,
            "base_minutes": self.base_minutes,
            "increment_seconds": self.increment_seconds,
        }
        if include_matches:
            data["matches"] = [match.to_dict() for match in self.matches.all()]
        return data
    
    class Meta:
        ordering = ['-start_date']
        
    @property
    def time_control_display(self):
        return f"{self.base_minutes}+{self.increment_seconds}"



class TournamentMatch(models.Model):
    tournament = models.ForeignKey(
        Tournament, on_delete=models.CASCADE, related_name='matches'
    )

    player1 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='matches_as_player1'
    )
    player2 = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='matches_as_player2'
    )
    match_created = models.BooleanField(default=False)
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
    live_match = models.OneToOneField(
        "match.Match",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tournament_pairing"
    )

    def __str__(self):
        return f"{self.tournament.name}: {self.player1.username} vs {self.player2.username}"

    def to_dict(self):
        return {
            "id": self.id,
            "tournament_id": self.tournament.id,
            "tournament_name": self.tournament.name,
            "player1": self.player1.to_dict(),
            "player2": self.player2.to_dict(),
            "scheduled_at": self.scheduled_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "live_match_id": self.live_match.id if self.live_match else None,
            "result": self.result,
            "match_created": self.match_created,
            "fen": self.fen,
        }
    
    class Meta:
        ordering = ['-scheduled_at']
        constraints = [
            models.UniqueConstraint(
                fields=['tournament', 'player1', 'player2'],
                name='unique_pair'
            )
        ]

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
    
class TournamentRegistration(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name="registrations")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tournament_registrations")
    registered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("tournament", "user")

    def __str__(self):
        return f"{self.user.username} in {self.tournament.name}"

