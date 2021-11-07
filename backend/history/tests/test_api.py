from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from history.models import Game
from history.serializers import GameSerializer
from datetime import datetime, timedelta
from django.urls import reverse
import collections
import pytz

User = get_user_model()


class GameApiTestCase(APITestCase):
    def setUp(self):
        self.serializer_datetime_format = "%Y-%m-%dT%H:%M:%SZ"
        user1 = User.objects.create_user(
            email="example1@email.com", username="example1", password="example123"
        )
        user2 = User.objects.create_user(
            email="example2@email.com", username="example2", password="example123"
        )
        user3 = User.objects.create_user(
            email="example3@email.com", username="example3", password="example123"
        )
        self.setup_datetime = datetime(
            year=2021, month=11, day=21, hour=13, minute=12, tzinfo=pytz.UTC
        )

        game = Game(started=self.setup_datetime - timedelta(minutes=2))
        game1 = Game(started=self.setup_datetime - timedelta(minutes=10))
        game_tie = Game(
            started=self.setup_datetime - timedelta(minutes=5),
        )

        game.save()
        game_tie.save()
        game1.save()

        game.played_by.set([user1, user2])
        game.winner = user1
        game.loser = user2
        game.moves = "x3571986"
        game.finished = self.setup_datetime

        game1.played_by.set([user2, user3])
        game1.winner = user3
        game1.loser = user2
        game1.moves = "x3571986"
        game1.finished = self.setup_datetime - timedelta(minutes=7)

        game_tie.played_by.set([user1, user2])
        # since the game is a tie, there are no winners.
        game_tie.moves = "o215368794"
        game_tie.finished = self.setup_datetime - timedelta(minutes=3)

        game.save()
        game1.save()
        game_tie.save()

    def test_listing_games(self):
        game_list_url = reverse("game-list")
        response = self.client.get(game_list_url)
        all_games = Game.objects.all()
        all_games_serialized = GameSerializer(all_games, many=True)
        self.assertEqual(response.data, all_games_serialized.data)

    def test_detail_of_normal_game(self):
        game = Game.objects.all()[0]
        game_detail_url = reverse("game-detail", args=[game.pk])
        response = self.client.get(game_detail_url)
        game_serialized = GameSerializer(game)
        self.assertEqual(
            response.data,
            game_serialized.data
        )

    def test_detail_of_tie_game(self):
        game = Game.objects.get(winner=None)
        game_detail_url = reverse("game-detail", args=[game.pk])
        response = self.client.get(game_detail_url)
        game_serialized = GameSerializer(game)
        self.assertEqual(
            response.data,
            game_serialized.data
        )

    def test_get_all_games_of_an_user(self):
        example1 = User.objects.all()[0]
        game_list_url = reverse("game-list") + "?user=example1"
        response = self.client.get(game_list_url)
        example1_games = example1.game_set.all()
        example1_games_serialized = GameSerializer(example1_games, many=True)
        self.assertEqual(response.data, example1_games_serialized.data)

