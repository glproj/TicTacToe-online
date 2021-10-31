from django.contrib import admin
from .models import Game

class GameAdmin(admin.ModelAdmin):
    list_display = ('winner', 'loser', 'moves')
admin.site.register(Game, GameAdmin)
