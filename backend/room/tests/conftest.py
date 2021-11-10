import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from channels.testing import WebsocketCommunicator
from config.asgi import application

User = get_user_model()


@pytest.fixture(scope="function")
def create_users_and_tokens(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        User.objects.create_user(
            email="anonymous1@anonymous.com",
            username="anonymous1",
            password="v157894375n87189437r89ieuwionrc¨#&*¨*@!(*&#",
            is_active=True,
        )
        User.objects.create_user(
            email="anonymous2@anonymous.com",
            username="anonymous2",
            password="4MXRU1980YR8XY09%¨%¨%¨%¨%#¨*fdskaflajfkdsla",
            is_active=True,
        )
        example1 = User.objects.create_user(
            email="example1@email.com",
            username="example1",
            password="example123",
            is_active=True,
        )
        example2 = User.objects.create_user(
            email="example2@email.com",
            username="example2",
            password="example123",
            is_active=True,
        )
        client = APIClient()
        example1_tokens = client.post(
            "/api/v1/auth/jwt/create/",
            {"email": "example1@email.com", "password": "example123"},
        ).data
        example2_tokens = client.post(
            "/api/v1/auth/jwt/create/",
            {"email": "example2@email.com", "password": "example123"},
        ).data
        return example1_tokens["access"], example2_tokens["access"]


@pytest.fixture
async def connect_players(create_users_and_tokens, db):
    """
    Connects player1 and player2 to the lobby room.
    After the test is run, it disconnects the players.
    """
    players_tokens = create_users_and_tokens
    player1 = WebsocketCommunicator(
        application,
        "ws/game/lobby/?token=" + players_tokens[0],
    )
    player2 = WebsocketCommunicator(
        application,
        "ws/game/lobby/?token=" + players_tokens[1],
    )
    await player1.connect()
    await player2.connect()
    yield (player1, player2)
    await player1.disconnect()
    await player2.disconnect()

@pytest.fixture
async def connect_players_without_auth(create_users_and_tokens, db):    
    player1 = WebsocketCommunicator(application, "ws/game/lobby/")
    player2 = WebsocketCommunicator(application, "ws/game/lobby/")
    await player1.connect()
    await player2.connect()
    yield (player1, player2)
    await player1.disconnect()
    await player2.disconnect()