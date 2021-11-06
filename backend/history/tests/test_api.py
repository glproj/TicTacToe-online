from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from history.models import Game
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

        self.setup_datetime = datetime(
            year=2021, month=11, day=21, hour=13, minute=12, tzinfo=pytz.UTC
        )

        game = Game(started=self.setup_datetime - timedelta(minutes=2))
        game_tie = Game(
            started=self.setup_datetime - timedelta(minutes=5),
        )
        game.save()
        game_tie.save()

        game.played_by.set([user1, user2])
        game.winner = user1
        game.loser = user2
        game.moves = "x3571986"
        game.finished = self.setup_datetime

        game_tie.played_by.set([user1, user2])
        # since the game is a tie, there are no winners.
        game_tie.moves = "o215368794"
        game_tie.finished = self.setup_datetime - timedelta(minutes=3)

        game.save()
        game_tie.save()

    def test_listing_games(self):
        game_list_url = reverse("game-list")
        response = self.client.get(game_list_url)
        self.assertEqual(
            response.data,
            [
                collections.OrderedDict(
                    {
                        "played_by": ["example1", "example2"],
                        "winner": "example1",
                        "loser": "example2",
                        "started": (
                            self.setup_datetime - timedelta(minutes=2)
                        ).strftime(self.serializer_datetime_format),
                        "finished": self.setup_datetime.strftime(
                            self.serializer_datetime_format
                        ),
                        "moves": "x3571986",
                    }
                ),
                collections.OrderedDict(
                    {
                        "played_by": ["example1", "example2"],
                        "winner": None,
                        "loser": None,
                        "started": (
                            self.setup_datetime - timedelta(minutes=5)
                        ).strftime(self.serializer_datetime_format),
                        "finished": (
                            self.setup_datetime - timedelta(minutes=3)
                        ).strftime(self.serializer_datetime_format),
                        "moves": "o215368794",
                    }
                ),
            ],
        )

    def test_detail_of_normal_game(self):
        pass

    def test_detail_of_tie_game(self):
        pass