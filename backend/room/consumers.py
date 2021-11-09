# chat/consumers.py
import json
from channels.generic.websocket import WebsocketConsumer
from .models import Room
from asgiref.sync import async_to_sync


class RoomConsumer(WebsocketConsumer):
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
        self.send(json.dumps({"position": event["position"]}))
