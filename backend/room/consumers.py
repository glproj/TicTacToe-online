# chat/consumers.py
import json
from channels.generic.websocket import JsonWebsocketConsumer
from .models import Room
from asgiref.sync import async_to_sync

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
            player_number = room.nb_of_players
            if player_number == 2:
                self.close("room_full")
            else:
                room.nb_of_players += 1
                room.save()
                async_to_sync(self.channel_layer.group_add)(
                    self.room_group_name, self.channel_name
                )

                self.accept()
        except Room.DoesNotExist:
            room = Room.objects.create(name=self.room_name, nb_of_players=1)
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
        position = data_json["position"]
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {"type": "position_played", "position": position}
        )

    def position_played(self, event):
        try:
            self.played += event["position"]
        except AttributeError:
            self.played = event["position"]

        current_player = 1 if len(self.played) % 2 == 1 else 2
        played_by_current_player = ""
        # this block will pick only the moves
        # of the player that made the last move
        for i in range(len(self.played)):
            if i % 2 != len(self.played) % 2:
                played_by_current_player += self.played[i]

        for win in winning_positions:
            if set(win).issubset(set(played_by_current_player)):
                self.send_json(
                    {
                        "position": event["position"],
                        "result": f"player{current_player}_win",
                    }
                )
            elif len(self.played) == 9:
                self.send_json(
                    {
                        "position": event["position"],
                        "result": "draw",
                    }
                )
        self.send_json({"position": event["position"]})
