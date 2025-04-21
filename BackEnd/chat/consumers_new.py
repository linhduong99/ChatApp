import json
import logging
import jwt
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.apps import apps

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            # Get room name from URL
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f'chat_{self.room_name}'

            # Get token from query string
            query_string = self.scope.get('query_string', b'').decode()
            query_params = dict(param.split('=') for param in query_string.split('&') if param)
            token = query_params.get('token')

            if not token:
                logger.warning("No token provided")
                await self.close(code=1008)  # Policy violation
                return

            # Verify token and get user
            try:
                logger.info(f"Decoding token: {token[:20]}...")
                # Decode token without verification first to get the user_id
                decoded_token = jwt.decode(token, options={"verify_signature": False})
                user_id = decoded_token.get('user_id')
                
                if not user_id:
                    logger.warning("No user_id in token")
                    await self.close(code=1008)  # Policy violation
                    return

                self.user = await self.get_user(user_id)
                if not self.user:
                    logger.warning(f"User not found for id: {user_id}")
                    await self.close(code=1008)  # Policy violation
                    return
                logger.info(f"Found user: {self.user.username}")
            except Exception as e:
                logger.error(f"Error validating token: {str(e)}", exc_info=True)
                await self.close(code=1008)  # Policy violation
                return

            # Get or create room
            room_created = await self.get_or_create_room()
            if not room_created:
                logger.error("Failed to create/get room")
                await self.close(code=1011)  # Internal error
                return

            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            await self.accept()
            logger.info(f'WebSocket connected: {self.user.username} to {self.room_name}')

        except Exception as e:
            logger.error(f"Error in connect: {str(e)}", exc_info=True)
            await self.close(code=1011)  # Internal error
            return

    async def disconnect(self, close_code):
        try:
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f'WebSocket disconnected: {self.user.username} from {self.room_name} with code {close_code}')
        except Exception as e:
            logger.error(f'Error in disconnect: {str(e)}')

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type', 'chat_message')
            
            if message_type == 'chat_message':
                content = data.get('content', '').strip()
                if not content:
                    return

                # Save message to database
                message = await self.save_message(content)
                
                # Send message to room group
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'chat_message',
                        'message': {
                            'id': message.id,
                            'content': message.content,
                            'user': {
                                'id': message.user.id,
                                'username': message.user.username
                            },
                            'timestamp': message.timestamp.isoformat()
                        }
                    }
                )
        except Exception as e:
            logger.error(f'Error in receive: {str(e)}')

    async def chat_message(self, event):
        try:
            # Send message to WebSocket
            await self.send(text_data=json.dumps(event['message']))
        except Exception as e:
            logger.error(f'Error in chat_message: {str(e)}')

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            User = get_user_model()
            return User.objects.get(id=user_id)
        except Exception as e:
            logger.warning(f'User not found for id: {user_id}: {str(e)}')
            return None

    @database_sync_to_async
    def get_or_create_room(self):
        try:
            Room = apps.get_model('chat', 'Room')
            room, created = Room.objects.get_or_create(name=self.room_name)
            return True
        except Exception as e:
            logger.error(f"Error getting/creating room: {str(e)}")
            return False

    @database_sync_to_async
    def save_message(self, content):
        Room = apps.get_model('chat', 'Room')
        Message = apps.get_model('chat', 'Message')
        room = Room.objects.get(name=self.room_name)
        return Message.objects.create(
            room=room,
            user=self.user,
            content=content
        ) 