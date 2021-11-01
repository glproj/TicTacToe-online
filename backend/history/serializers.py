from rest_framework import serializers
from .models import Game


class GameSerializer(serializers.ModelSerializer):
    winner = serializers.SlugRelatedField(slug_field="username", read_only=True)
    loser = serializers.SlugRelatedField(slug_field="username", read_only=True)
    class Meta:
        model = Game
        fields = ("winner", "loser", "started", "finished", "moves")
