import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from channels.testing import WebsocketCommunicator
from config.asgi import application

User = get_user_model()


@pytest.fixture(scope="session")
def create_users_and_tokens(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        anonymous = User.objects.create_user(
            email="anonymous@anonymous.com",
            username="anonymous",
            password="v157894375n87189437r89ieuwionrc¨#&*¨*@!(*&#",
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
    player1 = WebsocketCommunicator(application, "ws/game/lobby/")
    player2 = WebsocketCommunicator(application, "ws/game/lobby/")
    await player1.connect()
    await player2.connect()
    yield (player1, player2)
    await player1.disconnect()
    await player2.disconnect()
