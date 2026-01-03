import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import Match
import chess

@database_sync_to_async
def get_match_state(match_id):
    match = (
        Match.objects
        .select_related("player_white", "player_black")
        .get(id=match_id)
    )

    return {
        "fen": match.current_fen,
        "move_history": match.move_history,
        "status": match.status,
        "result": match.result,
        "white_player": match.player_white.username if match.player_white else None,
        "black_player": match.player_black.username if match.player_black else None,
        "white_connected": match.white_connected,
        "black_connected": match.black_connected,
    }


class MatchConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.match_id = self.scope['url_route']['kwargs']['match_id']
        self.room_group_name = f'match_{self.match_id}'
        self.user = self.scope.get('user')
        
        
        self.match = await self.get_match()
        if not self.match:
            await self.close()
            return
        
        
        self.player_color = await self.assign_player()
        
        if not self.player_color:
            
            self.player_color = 'spectator'
        
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        
        await self.update_connection_status(True)
        
        
        await self.send_game_state()
        
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'player_connected',
                'color': self.player_color,
                'username': self.user.username if self.user.is_authenticated else 'Anonymous'
            }
        )

    async def disconnect(self, close_code):
        
        await self.update_connection_status(False)
        
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'player_disconnected',
                'color': self.player_color,
                'username': self.user.username if self.user.is_authenticated else 'Anonymous'
            }
        )
        
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'move':
                await self.handle_move(data)
            elif message_type == 'offer_draw':
                await self.handle_draw_offer()
            elif message_type == 'respond_draw':
                await self.handle_draw_response(data.get('accept', False))
            elif message_type == 'resign':
                await self.handle_resign()
            elif message_type == 'request_sync':
                await self.send_game_state()
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))

    async def handle_move(self, data):
        move_from = data.get('from')
        move_to = data.get('to')
        promotion = data.get('promotion')
        
        
        match = await self.get_match()
        current_turn = 'white' if 'w' in match.current_fen.split()[1] else 'black'
        
        if self.player_color != current_turn:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Not your turn'
            }))
            return
        
        
        is_valid, new_fen, move_uci = await self.validate_move(
            match.current_fen, move_from, move_to, promotion
        )
        
        if not is_valid:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid move'
            }))
            return
        
        
        await self.save_move(move_uci, move_from, move_to, new_fen)
        
        
        game_status = await self.check_game_end(new_fen)
        
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_move',
                'move': {
                    'from': move_from,
                    'to': move_to,
                    'uci': move_uci,
                    'promotion': promotion
                },
                'fen': new_fen,
                'game_status': game_status
            }
        )

    async def handle_draw_offer(self):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'draw_offered',
                'by': self.player_color
            }
        )

    async def handle_draw_response(self, accept):
        if accept:
            await self.end_game('1/2-1/2', 'Draw by agreement')
        else:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'draw_declined',
                    'by': self.player_color
                }
            )

    async def handle_resign(self):
        result = '0-1' if self.player_color == 'white' else '1-0'
        winner = 'Black' if self.player_color == 'white' else 'White'
        await self.end_game(result, f'{winner} wins by resignation')

    async def end_game(self, result, reason):
        await self.save_game_result(result)
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_ended',
                'result': result,
                'reason': reason
            }
        )

    
    async def send_move(self, event):
        await self.send(text_data=json.dumps({
            'type': 'move',
            'move': event['move'],
            'fen': event['fen'],
            'game_status': event.get('game_status')
        }))

    async def player_connected(self, event):
        await self.send(text_data=json.dumps({
            'type': 'player_connected',
            'color': event['color'],
            'username': event['username']
        }))

    async def player_disconnected(self, event):
        await self.send(text_data=json.dumps({
            'type': 'player_disconnected',
            'color': event['color'],
            'username': event['username']
        }))

    async def draw_offered(self, event):
        await self.send(text_data=json.dumps({
            'type': 'draw_offered',
            'by': event['by']
        }))

    async def draw_declined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'draw_declined',
            'by': event['by']
        }))

    async def game_ended(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_ended',
            'result': event['result'],
            'reason': event['reason']
        }))

    
    @database_sync_to_async
    def get_match(self):
        try:
            return Match.objects.get(id=self.match_id)
        except Match.DoesNotExist:
            return None

    @database_sync_to_async
    def assign_player(self):
        match = Match.objects.get(id=self.match_id)
        
        if not self.user.is_authenticated:
            return None
        
        
        if match.player_white == self.user:
            return 'white'
        elif match.player_black == self.user:
            return 'black'
        
        
        if match.status == 'WAIT':
            if not match.player_white:
                match.player_white = self.user
                match.save()
                return 'white'
            elif not match.player_black:
                match.player_black = self.user
                match.status = 'LIVE'
                match.save()
                return 'black'
        
        
        return None

    @database_sync_to_async
    def update_connection_status(self, connected):
        match = Match.objects.get(id=self.match_id)
        
        if self.player_color == 'white':
            match.white_connected = connected
        elif self.player_color == 'black':
            match.black_connected = connected
        
        match.save()

    @database_sync_to_async
    def validate_move(self, fen, move_from, move_to, promotion):
        try:
            board = chess.Board(fen)
            
            
            move_uci = move_from + move_to + (promotion if promotion else '')
            move = chess.Move.from_uci(move_uci)
            
            if move in board.legal_moves:
                board.push(move)
                new_fen = board.fen()
                move_uci = board.uci(move)
                return True, new_fen, move_uci
            else:
                return False, None, None
                
        except Exception as e:
            print(f"Move validation error: {e}")
            return False, None, None

    @database_sync_to_async
    def save_move(self, move_uci, move_from, move_to, new_fen):
        match = Match.objects.get(id=self.match_id)
        match.add_move(move_uci, move_from, move_to, new_fen)

    @database_sync_to_async
    def check_game_end(self, fen):
        try:
            board = chess.Board(fen)
            
            if board.is_checkmate():
                winner = 'Black' if board.turn == chess.WHITE else 'White'
                result = '0-1' if board.turn == chess.WHITE else '1-0'
                Match.objects.filter(id=self.match_id).update(
                    status='END',
                    result=result
                )
                return {
                    'game_over': True,
                    'result': result,
                    'reason': f'{winner} wins by checkmate'
                }
            elif board.is_stalemate():
                Match.objects.filter(id=self.match_id).update(
                    status='END',
                    result='1/2-1/2'
                )
                return {
                    'game_over': True,
                    'result': '1/2-1/2',
                    'reason': 'Draw by stalemate'
                }
            elif board.is_insufficient_material():
                Match.objects.filter(id=self.match_id).update(
                    status='END',
                    result='1/2-1/2'
                )
                return {
                    'game_over': True,
                    'result': '1/2-1/2',
                    'reason': 'Draw by insufficient material'
                }
            elif board.is_fifty_moves():
                Match.objects.filter(id=self.match_id).update(
                    status='END',
                    result='1/2-1/2'
                )
                return {
                    'game_over': True,
                    'result': '1/2-1/2',
                    'reason': 'Draw by fifty-move rule'
                }
            elif board.is_repetition():
                Match.objects.filter(id=self.match_id).update(
                    status='END',
                    result='1/2-1/2'
                )
                return {
                    'game_over': True,
                    'result': '1/2-1/2',
                    'reason': 'Draw by repetition'
                }
            
            return {'game_over': False}
            
        except Exception as e:
            print(f"Game end check error: {e}")
            return {'game_over': False}

    @database_sync_to_async
    def save_game_result(self, result):
        from django.utils import timezone
        Match.objects.filter(id=self.match_id).update(
            status='END',
            result=result,
            end_time=timezone.now()
        )

    async def send_game_state(self):
        state = await get_match_state(self.match_id)

        await self.send(text_data=json.dumps({
            "type": "game_state",
            "player_color": self.player_color,
            **state
        }))
