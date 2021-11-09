from django.db import models
from django.contrib.auth import get_user_model
class Room(models.Model):
    name = models.CharField(max_length=50)
    players = models.ManyToManyField(get_user_model())
    nb_of_players = models.IntegerField()

    def __str__(self):
        return f"{self.name}, {self.nb_of_players} player(s)"