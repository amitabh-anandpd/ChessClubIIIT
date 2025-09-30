from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import transaction
from django.db.models import Q

class User(AbstractUser):
    
    def __str__(self):
        return f"{self.username}"

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email": self.email,
            "profile": self.profile.to_dict(),
        }
    
    @property
    def initials(self):
        return str(self.first_name[0]+self.last_name[0])
    
    @property
    def tournaments(self):
        from tournaments.models import Tournament
        return Tournament.objects.filter(
            Q(matches__player1=self) | Q(matches__player2=self)
        ).distinct()
    
    @property
    def matches(self):
        from tournaments.models import Match
        return Match.objects.filter(Q(player1=self) | Q(player2=self)).select_related("tournament")


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    rating = models.IntegerField(default=600)
    last_rating = models.IntegerField(default=600)
    last_rank = models.IntegerField(default=0)
    chessdotcom = models.CharField(max_length=64, blank=True, null=True)
    lichess = models.CharField(max_length=64, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user.id,
            "rating": self.rating,
            "last_rating": self.last_rating,
            "last_rank": self.last_rank,
            "chessdotcom": self.chessdotcom,
            "lichess": self.lichess,
        }
    
    def save(self, *args, **kwargs):
        with transaction.atomic():
            if self.pk:
                old = UserProfile.objects.get(pk=self.pk)
                if old.rating != self.rating:
                    self.last_rating = old.rating
            else:
                self.last_rating = self.rating

            super().save(*args, **kwargs)
    
    @property
    def rating_change(self):
        return self.rating - self.last_rating

    @property
    def rank_change(self, current_rank):
        return self.last_rank - current_rank

    @property
    def moved_up_in_rank(self, current_rank):
        return current_rank < self.last_rank

    @property
    def moved_down_in_rank(self, current_rank):
        return current_rank > self.last_rank