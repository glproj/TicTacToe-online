from django.db import models
from django.contrib.auth import get_user_model


class Game(models.Model):
    winner = models.OneToOneField(
        get_user_model(), on_delete=models.SET_NULL, null=True, related_name="winner"
    )
    loser = models.OneToOneField(
        get_user_model(), on_delete=models.SET_NULL, null=True, related_name="loser"
    )
    started = models.DateTimeField()
    finished = models.DateTimeField(auto_now_add=True)