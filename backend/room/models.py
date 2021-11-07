from django.db import models

class Room(models.Model):
    name = models.CharField(max_length=50)
    nb_of_players = models.IntegerField()

    def __str__(self):
        return f"{self.name}, {self.nb_of_players} player(s)"