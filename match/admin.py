from django.contrib import admin
from .models import Match

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['id', 'player_white', 'player_black', 'status', 'start_time']
    list_filter = ['status']
    search_fields = ['player_white__username', 'player_black__username']