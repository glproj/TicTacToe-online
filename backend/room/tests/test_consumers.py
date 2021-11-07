from channels.testing import WebsocketCommunicator
from config.asgi import application
from room.models import Room
import pytest


@pytest.fixture
async def connect_players():
    """
        Connects player1 and player2 to the lobby room. 
        After the test is run, it disconnects the players.
    """
    player1 = WebsocketCommunicator(application, "ws/game/lobby/")
    player2 = WebsocketCommunicator(application, "ws/game/lobby/")
    await player1.connect()
    await player2.connect()
    yield (player1, player2)
    await player1.disconnect()
    await player2.disconnect()


class TestRoomConsumer:
    @pytest.mark.django_db
    @pytest.mark.asyncio
    async def test_sending_position(self, connect_players):
        """Checks if player2 can receive positions correctly"""
        player1, player2 = connect_players
        await player1.send_json_to({"type": "position_played", "position": 1})
        position_received = await player2.receive_json_from()
        assert {'position': 1} == position_received

    @pytest.mark.django_db
    @pytest.mark.asyncio
    def test_room_generated_by_lobby(self, connect_players):
        """Checks if Room is generated correctly after players connect"""
        room_queryset = Room.objects.all()
        assert room_queryset.count() == 1
        assert room_queryset[0].name == "lobby"
        assert room_queryset[0].nb_of_players == 2
