import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from channels.exceptions import StopConsumer
from asgiref.sync import sync_to_async
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.room_name = self.scope['url_route']['kwargs']['room_name']
            self.room_group_name = f'chat_{self.room_name}'
            
            logger.info(f"Attempting to connect to room: {self.room_name}")
            logger.debug(f"Channel layer: {self.channel_layer}")
            
            # Create room if it doesn't exist
            await self.create_room_if_not_exists()
            
            # Join room group
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            await self.accept()
            logger.info(f"Successfully connected to room: {self.room_name}")
        except Exception as e:
            logger.error(f"Error in connect: {str(e)}", exc_info=True)
            await self.close()
            raise StopConsumer()

    @sync_to_async
    def create_room_if_not_exists(self):
        try:
            from .models import Room
            Room.objects.get_or_create(name=self.room_name)
            return True
        except Exception as e:
            logger.error(f"Error creating room: {str(e)}")
            return False

    async def disconnect(self, close_code):
        try:
            logger.info(f"Disconnecting from room: {self.room_name} with code: {close_code}")
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
            logger.info(f"Successfully disconnected from room: {self.room_name}")
        except Exception as e:
            logger.error(f"Error in disconnect: {str(e)}", exc_info=True)
        finally:
            raise StopConsumer()

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message = text_data_json['message']
            username = text_data_json['username']

            if not message or not username:
                logger.warning(f"Invalid message data received: {text_data}")
                return

            logger.info(f"Received message from {username} in room {self.room_name}")

            # Save message to database
            saved_message = await self.save_message(username, message)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'id': saved_message.id,
                    'content': saved_message.content,
                    'username': saved_message.username,
                    'timestamp': saved_message.timestamp.isoformat()
                }
            )
            logger.info(f"Message sent to room group: {self.room_group_name}")
        except json.JSONDecodeError:
            logger.error("Invalid JSON received", exc_info=True)
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}", exc_info=True)

    async def chat_message(self, event):
        try:
            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'id': event['id'],
                'content': event['content'],
                'username': event['username'],
                'timestamp': event['timestamp']
            }))
            logger.info(f"Message sent to WebSocket: {event['content']}")
        except Exception as e:
            logger.error(f"Error in chat_message: {str(e)}", exc_info=True)

    @database_sync_to_async
    def save_message(self, username, content):
        from .models import Room, Message
        try:
            room = Room.objects.get(name=self.room_name)
            message = Message.objects.create(
                room=room,
                content=content,
                username=username
            )
            logger.info(f"Message saved to database: {content}")
            return message
        except ObjectDoesNotExist:
            logger.error(f"Room not found: room={self.room_name}")
            raise
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}", exc_info=True)
            raise 