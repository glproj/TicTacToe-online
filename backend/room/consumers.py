from django.utils import timezone
import json
from channels.generic.websocket import JsonWebsocketConsumer
from .models import Room
from asgiref.sync import async_to_sync
from django.contrib.auth import get_user_model
from history.models import Game

User = get_user_model()

winning_positions = [
    "123",
    "456",
    "789",
    "147",
    "258",
    "369",
    "159",
    "357",
]


class RoomConsumer(JsonWebsocketConsumer):
    def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "game_" + self.room_name
        try:
            room = Room.objects.get(name=self.room_name)
            self.player = 2
            room.nb_of_players += 1
        except Room.DoesNotExist:
            room = Room.objects.create(name=self.room_name, nb_of_players=1)
            self.player = 1

        player_number = room.nb_of_players
        if player_number == 3:
            self.close("room_full")
        else:
            user = self.scope["user"]
            if self.scope["user"].id == None:
                user = User.objects.get(username="anonymous1")
                if user in room.players.all():
                    user = User.objects.get(username="anonymous2")
            room.players.add(user)
            self.players = room.players.all()
            room.save()
            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name, self.channel_name
            )

            self.accept()

    def disconnect(self, close_code):
        if close_code == "room_full":
            return
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "close"}
        )
        try:
            room = Room.objects.get(name=self.room_name)
            room.delete()
        except Room.DoesNotExist:
            return

    def receive(self, text_data):
        data_json = json.loads(text_data)
        position = str(data_json["position"])
        if not (len(position) == 1 and position in "123456789"):
            return self.send_json({"error": "invalid position"})
        try:
            self.played
        except AttributeError:
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name, {"type": "position_played", "position": position}
            )
            return
        # I'm not modifying self.played here because it is
        # already modified in the position_played method.
        played = self.played + position

        current_player = 1 if len(played) % 2 == 1 else 2
        if self.player != current_player:
            return self.send_json({'error': 'not your turn'})
        played_by_current_player = ""
        # this block will pick only the moves
        # of the player that made the last move
        for i in range(len(played)):
            if i % 2 != len(played) % 2:
                played_by_current_player += played[i]
        for win in winning_positions:
            if set(win).issubset(set(played_by_current_player)):
                game = Game.objects.create(
                    winner=self.players[current_player - 1],
                    loser=self.players[0 if current_player == 2 else 1],
                    started=self.started
                    # finish have auto_add_now set to True
                )
                game.played_by.set(self.players)
                game.save()
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        "type": "position_played",
                        "position": position,
                        "result": f"player{current_player}_win",
                    },
                )
                return
            elif len(played) == 9:
                game = Game.objects.create(
                    winner=None,
                    loser=None,
                    started=self.started
                    # finish have auto_add_now set to True
                )
                game.played_by.set(self.players)
                game.save()
                async_to_sync(self.channel_layer.group_send)(
                    self.room_group_name,
                    {
                        "type": "position_played",
                        "position": position,
                        "result": "draw",
                    },
                )
                return
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "position_played", "position": position}
        )

    def position_played(self, event):
        try:
            self.played += event["position"]
        except AttributeError:
            self.played = event["position"]
            self.started = timezone.now()
        try:
            send = {"position": event["position"], "result": event["result"]}
        except KeyError:
            send = {"position": event["position"]}
        self.send_json(send)
