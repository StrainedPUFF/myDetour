from django.urls import re_path
from Coordinator.consumers import SessionConsumer
# from channels.routing import ProtocolTypeRouter, URLRouter
# from django.core.asgi import get_asgi_application

websocket_urlpatterns = [
    re_path(r'ws/session/(?P<session_id>[-\w]+)/$', SessionConsumer.as_asgi()),
]

# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),  # Handles standard HTTP requests
#     "websocket": URLRouter(websocket_urlpatterns),  # Handles WebSocket connections
# })
