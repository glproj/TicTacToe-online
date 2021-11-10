from datetime import datetime
from channels.db import database_sync_to_async as db_sync
from asgiref.sync import sync_to_async
from channels.testing.websocket import WebsocketCommunicator
from django.utils import timezone
import pytz
from room.models import Room
import pytest
from config.asgi import application
from django.contrib.auth import get_user_model
from history.models import Game
from freezegun import freeze_time

User = get_user_model()


@pytest.mark.django_db(transaction=True)
class TestRoomConsumer:
    @db_sync
    def get_user(self, username):
        return User.objects.get(username=username)

    async def simulate_game(self, player1, player2, moves):
        """Simulate a game where player1 starts and returns
        the message received from both players when the game ends.
        The game lasts 5 minutes.

        :param player1: player that goes first
        :type player1: WebsocketsCommunicator
        :param player2: player that goes second
        :type player2: WebsocketsCommunicator
        :param moves: game moves, like '1234567' (player1 wins in this example)
        :type moves: string
        """
        game_start = timezone.datetime(2007, 7, 7, 7, 7, 7, 7)
        with freeze_time(game_start) as frozen_datetime:
            playing = player1
            for position in moves:
                await playing.send_json_to({"position": position})
                if position == moves[-1]:
                    frozen_datetime.tick(timezone.timedelta(minutes=5))
                player1_response = await player1.receive_json_from()
                player2_response = await player2.receive_json_from()
                playing = player2 if playing == player1 else player1
            return player1_response, player2_response

    @pytest.mark.asyncio
    async def test_sending_position(self, connect_players):
        """Checks if player2 can receive positions correctly"""
        player1, player2 = connect_players
        await player1.send_json_to({"type": "position_played", "position": "1"})
        position_received = await player2.receive_json_from()
        assert {"position": "1"} == position_received

    def test_room_generated_by_lobby(self, connect_players):
        """Checks if Room is generated correctly after players connect"""
        room_queryset = Room.objects.all()
        assert room_queryset.count() == 1
        assert room_queryset[0].name == "lobby"
        assert room_queryset[0].nb_of_players == 2

    @pytest.mark.asyncio
    async def test_room_is_deleted_after_player_quits(self, connect_players):
        """Disconnects a player and checks if the room is deleted"""
        player1 = connect_players[0]
        await player1.disconnect()
        room_queryset_length = await sync_to_async(Room.objects.all().count)()
        assert room_queryset_length == 0

    @pytest.mark.asyncio
    async def test_player_connects_to_full_room(self, connect_players):
        """Connects a player to a full room"""
        player3 = WebsocketCommunicator(application, "ws/game/lobby/")
        connected, subprotocol = await player3.connect()
        assert not connected

    @pytest.mark.parametrize("moves", ["1234567", "123456879", "314589"])
    @pytest.mark.asyncio
    async def test_message_after_game_end(self, connect_players, moves):
        player1, player2 = connect_players
        player1_response, player2_response = await self.simulate_game(
            player1, player2, moves
        )
        if moves == "123456789":
            assert player1_response == {"result": "draw", "position": "9"}
            assert player2_response == {"result": "draw", "position": "9"}
        elif moves == "1234567":
            assert player1_response == {"result": "player1_win", "position": "7"}
            assert player2_response == {"result": "player1_win", "position": "7"}
        elif moves == "314589":
            assert player1_response == {"result": "player2_win", "position": "9"}
            assert player2_response == {"result": "player2_win", "position": "9"}

    def test_user_added_to_players_field_after_connection(self, connect_players):
        room = Room.objects.all()[0]
        assert list(room.players.all()) == [
            User.objects.get(username="example1"),
            User.objects.get(username="example2"),
        ]

    @pytest.mark.parametrize("position", ["10", "fjkdsalç", "0"])
    @pytest.mark.asyncio
    async def test_sending_invalid_positions(self, connect_players, position):
        player1, player2 = connect_players
        await player1.send_json_to({"type": "position_played", "position": position})
        assert await player1.receive_json_from() == {"error": "invalid position"}

    @pytest.mark.asyncio
    async def test_sending_positions_out_of_your_turn(self, connect_players):
        player1, player2 = connect_players
        await player1.send_json_to({"type": "position_played", "position": 1})
        await player1.receive_json_from()
        await player2.receive_json_from()
        await player1.send_json_to({"type": "position_played", "position": 2})
        assert await player1.receive_json_from() == {"error": "not your turn"}

        await player1.send_json_to({"type": "position_played", "position": 3})
        assert await player1.receive_json_from() == {"error": "not your turn"}

        await player2.send_json_to({"type": "position_played", "position": 2})
        await player2.receive_json_from()
        await player2.send_json_to({"type": "position_played", "position": 3})
        assert await player2.receive_json_from() == {"error": "not your turn"}

        await player2.send_json_to({"type": "position_played", "position": 4})
        assert await player2.receive_json_from() == {"error": "not your turn"}

    @pytest.mark.parametrize("moves", ["1234567", "123456879"])
    @pytest.mark.asyncio
    async def test_game_instance_created_after_game_ends(self, connect_players, moves):
        player1, player2 = connect_players
        await self.simulate_game(player1, player2, moves)

        @db_sync
        def first_game():
            return Game.objects.all()[0]

        game = await first_game()
        assert await db_sync(Game.objects.count)() == 1

        p1_user = await self.get_user("example1")
        p2_user = await self.get_user("example2")
        if moves == "1234567":
            assert await db_sync(lambda: game.winner)() == p1_user
            assert await db_sync(lambda: game.loser)() == p2_user
        else:
            assert game.winner == None
            assert game.loser == None
        played_by = await db_sync(lambda: list(game.played_by.all()))()
        assert played_by == [p1_user, p2_user]
        assert game.started == timezone.datetime(
            2007, 7, 7, 7, 7, 7, 7, tzinfo=pytz.utc
        )
        assert game.finished == timezone.datetime(
            2007, 7, 7, 7, 12, 7, 7, tzinfo=pytz.utc
        )

    @pytest.mark.parametrize("moves", ["1234567", "123456879"])
    @pytest.mark.asyncio
    async def test_game_instance_created_after_game_ends_without_auth(
        self, connect_players_without_auth, moves
    ):
        player1, player2 = connect_players_without_auth
        await self.simulate_game(player1, player2, moves)

        @db_sync
        def first_game():
            return Game.objects.all()[0]

        game = await first_game()
        assert await db_sync(Game.objects.count)() == 1

        p1_user = await self.get_user("anonymous1")
        p2_user = await self.get_user("anonymous2")
        if moves == "1234567":
            assert await db_sync(lambda: game.winner)() == p1_user
            assert await db_sync(lambda: game.loser)() == p2_user
        else:
            assert game.winner == None
            assert game.loser == None
        played_by = await db_sync(lambda: list(game.played_by.all()))()
        assert played_by == [p1_user, p2_user]
        assert game.started == timezone.datetime(
            2007, 7, 7, 7, 7, 7, 7, tzinfo=pytz.utc
        )
        assert game.finished == timezone.datetime(
            2007, 7, 7, 7, 12, 7, 7, tzinfo=pytz.utc
        )
