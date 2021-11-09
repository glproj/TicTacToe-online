from asgiref.sync import sync_to_async
from channels.testing.websocket import WebsocketCommunicator
from room.models import Room
import pytest
from config.asgi import application
from rest_framework.test import APIClient


@pytest.mark.django_db
class TestRoomConsumer:
    async def simulate_game(self, player1, player2, moves):
        """Simulate a game where player1 starts and returns
        the message received from both players when the game ends

        :param player1: player that goes first
        :type player1: WebsocketsCommunicator
        :param player2: player that goes second
        :type player2: WebsocketsCommunicator
        :param moves: game moves, like '1234567' (player1 wins in this example)
        :type moves: string
        """
        playing = player1
        for position in moves:
            await playing.send_json_to({"position": position})
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

    @pytest.mark.django_db
    @pytest.mark.asyncio
    def test_room_generated_by_lobby(self, connect_players):
        """Checks if Room is generated correctly after players connect"""
        room_queryset = Room.objects.all()
        assert room_queryset.count() == 1
        assert room_queryset[0].name == "lobby"
        assert room_queryset[0].nb_of_players == 2
