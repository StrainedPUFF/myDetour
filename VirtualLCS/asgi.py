"""
ASGI config for VirtualLCS project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""
# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# from Coordinator.routing import websocket_urlpatterns

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VirtualLCS.settings')
# print(f'DJANGO_SETTINGS_MODULE is set to: {os.getenv("DJANGO_SETTINGS_MODULE")}')

# application = ProtocolTypeRouter({
#     'http': get_asgi_application(),
#     'websocket': AuthMiddlewareStack(
#         URLRouter(websocket_urlpatterns)
#     ),
# })

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from Coordinator.routing import websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'VirtualLCS.settings')

async def lifespan(scope, receive, send):
    if scope['type'] == 'lifespan':
        # Startup logic
        await send({"type": "lifespan.startup.complete"})
        try:
            print("Performing startup tasks...")
            # Add any startup tasks here
        except Exception as e:
            print(f"Error during startup: {e}")
        await receive()
        # Shutdown logic
        try:
            print("Performing shutdown tasks...")
            # Add any cleanup tasks here
        except Exception as e:
            print(f"Error during shutdown: {e}")
        await send({"type": "lifespan.shutdown.complete"})

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
    'lifespan': lifespan,  # Add this to support lifespan
})
