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
    moves = models.CharField(max_length=10) # the first character is the first mark played.
    # The rest of the characters are the coordinates of the moves
    # example: 'x3571986' correspond to the moves at 
    # https://codepen.io/denypatrascu/pen/pvYdYg          |     |
    # 1 2 3
    # 4 5 6
    # 7 8 9
