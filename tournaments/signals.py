from django.db.models.signals import post_save
from django.dispatch import receiver
from tournaments.models import TournamentMatch
from match.models import Match


@receiver(post_save, sender=TournamentMatch)
def create_match_when_scheduled(sender, instance, created, **kwargs):
    if instance.scheduled_at is None:
        return

    if instance.live_match is not None:
        return

    live_match = Match.objects.create(
        player_white=instance.player1,
        player_black=instance.player2,
        scheduled_start=instance.scheduled_at,
        status="WAIT"
    )

    instance.live_match = live_match
    instance.save(update_fields=["live_match"])
