from django.contrib import admin
from .models import Tournament, Match

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('tournament', 'player1', 'player2', 'result', 'winner', 'scheduled_at')
    list_filter = ('tournament', 'result')
    search_fields = ('player1__username', 'player2__username')
