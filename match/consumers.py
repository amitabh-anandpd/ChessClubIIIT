import json
from channels.generic.websocket import AsyncWebsocketConsumer

class MatchConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.room_group_name = f'match_{self.match_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        move = data['move']
        fen = data['fen']

        # Broadcast the move to everyone in the room
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_move',
                'move': move,
                'fen': fen
            }
        )

    # Receive message from room group
    async def send_move(self, event):
        move = event['move']
        fen = event['fen']

        # Send to WebSocket
        await self.send(text_data=json.dumps({
            'move': move,
            'fen': fen
        }))
