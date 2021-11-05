from django.db import models

class Room(models.Model):
    name = models.CharField(max_length=50)
    nb_of_players = models.IntegerField()