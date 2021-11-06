from django.contrib import admin
from .models import Room

class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'nb_of_players')
admin.site.register(Room, RoomAdmin)
