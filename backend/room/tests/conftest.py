import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from channels.testing import WebsocketCommunicator
from history.models import Game
from config.asgi import application

@pytest.fixture
async def connect_players(create_users_and_tokens):
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
