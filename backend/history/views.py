from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from .models import Game
from .serializers import GameSerializer

User = get_user_model()


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GameSerializer
    def get_queryset(self):
        username = self.request.query_params.get('user')
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response(status.HTTP_400_BAD_REQUEST)
            games = user.winner.all() | user.loser.all()
            return games.order_by('-started')
        return Game.objects.all()
        
    def list(self, request):
        games = self.get_queryset()
        games_serialized = GameSerializer(games, many=True)
        return Response(games_serialized.data)
