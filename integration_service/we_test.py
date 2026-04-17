import asyncio
import websockets
import json

async def handler(websocket):
    print(" [✓] Client connected!")
    try:
        async for message in websocket:
            data = json.loads(message)
            print(f"\n [>] Received Gesture Data: {data}")
            
            # Send back the expected 'ok' status
            response = {"status": "ok"}
            await websocket.send(json.dumps(response))
            print(" [<] Sent confirmation 'ok'")
            
    except websockets.exceptions.ConnectionClosed:
        print(" [x] Client disconnected.")

async def main():
    print("Starting WebSocket server on ws://localhost:8765 ...")
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())