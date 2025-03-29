import websockets
import asyncio
import json

async def test_websocket():
    uri = "ws://localhost:8080/ws/session/66ed361a16fa4742b8c60029d22c8b15/"
 # Replace '1' with the session ID you want to test
    try:
        # Connect to the WebSocket server
        async with websockets.connect(uri) as websocket:
            # Send a test message to the server
            message = {"message": "Hello WebSocket!"}
            await websocket.send(json.dumps(message))
            print(f"Sent: {message}")

            # Receive a response from the server
            response = await websocket.recv()
            print(f"Received: {response}")

    except Exception as e:
        # Handle any connection or data errors
        print(f"Error: {e}")

# Entry point for running the WebSocket test
if __name__ == "__main__":
    asyncio.run(test_websocket())
