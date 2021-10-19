from rest_framework import serializers

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ("winner", "loser", "started", "finished")