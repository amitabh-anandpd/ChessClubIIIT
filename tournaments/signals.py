from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from tournaments.models import TournamentMatch
from match.models import Match


@receiver(post_save, sender=TournamentMatch)
def create_live_match(sender, instance, created, **kwargs):
    # Only act when first created
    if not created:
        return

    # Prevent duplicates
    if instance.live_match is not None:
        return

    # Create the real match
    live_match = Match.objects.create(
        player_white=instance.player1,
        player_black=instance.player2,
        status="WAIT",  # or "LIVE" if you want auto-start
        start_time=instance.scheduled_at or timezone.now(),
    )

    # Link them
    instance.live_match = live_match
    instance.save(update_fields=["live_match"])
