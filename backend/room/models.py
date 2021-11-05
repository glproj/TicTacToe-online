from django.db import models

class Room(models.Model):
    nb_of_players = models.IntegerField()