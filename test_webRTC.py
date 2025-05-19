from channels.testing import WebsocketCommunicator
from VirtualLCS.asgi import application
import asyncio

async def test_websocket():
    communicator = WebsocketCommunicator(application, "/ws/session/0947015a-c19d-4060-ad25-59c6c6715e13/")
    connected, _ = await communicator.connect()
    assert connected, "WebSocket failed to connect!"  # Error handling

    await communicator.send_to(text_data='{"type": "createTransport"}')
    response = await communicator.receive_from()
    print("Received:", response)

    await communicator.disconnect()

asyncio.run(test_websocket())
