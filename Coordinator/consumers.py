import json
from channels.generic.websocket import AsyncWebsocketConsumer
import logging
from asgiref.sync import sync_to_async


logger = logging.getLogger(__name__)

class SessionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs'].get('session_id')
        self.session_group_name = f'session_{self.session_id}'
        self.user = self.scope['user']

        logger.info(f"Connection attempt for session_id: {self.session_id} by user: {self.user}")

        if not self.user.is_authenticated:
            await self.close()
            return

        # Fetch session details and determine if the user is the host
        self.is_host = await self.check_if_host(self.user, self.session_id)

        await self.channel_layer.group_add(
            self.session_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.session_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')

            # Only allow the host to perform certain actions
            if message_type == 'draw' or message_type == 'audio':
                if not self.is_host:
                    await self.send(text_data=json.dumps({
                        'error': 'Permission denied: Only the host can perform this action.'
                    }))
                    return

                payload = text_data_json.get('payload', {})
                await self.channel_layer.group_send(
                    self.session_group_name,
                    {
                        'type': f'session_{message_type}',
                        'payload': payload
                    }
                )

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'error': 'Invalid JSON format'
            }))
        except Exception as e:
            logger.error(f"Error in receive method: {str(e)}")
            await self.send(text_data=json.dumps({
                'error': f'Unexpected error: {str(e)}'
            }))

    async def session_draw(self, event):
        draw_data = event['payload']
        await self.send(text_data=json.dumps({
            'type': 'draw',
            'payload': draw_data
        }))

    async def session_audio(self, event):
        audio_data = event['payload']
        logger.debug(f"Audio data being sent: {audio_data}")  # Add logging here
        await self.send(text_data=json.dumps({
            'type': 'audio',
            'payload': audio_data
    }))


    @sync_to_async
    def check_if_host(self, user, session_id):
        from Discussion.models import Session
        try:
            session = Session.objects.get(id=session_id)
            return session.host == user
        except Session.DoesNotExist:
            return False
