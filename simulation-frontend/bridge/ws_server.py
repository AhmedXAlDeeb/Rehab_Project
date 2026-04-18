# bridge/ws_server.py
import asyncio
import json
import os
import logging
import time
from websockets.server import serve

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ws_server")

_env = None
_clients = set()

def set_env(env):
    global _env
    _env = env


async def broadcast(payload):
    if not _clients:
        return

    body = json.dumps(payload)
    disconnected = []
    for client in list(_clients):
        try:
            await client.send(body)
        except Exception:
            disconnected.append(client)

    for client in disconnected:
        _clients.discard(client)

async def handle(websocket):
    _clients.add(websocket)
    log.info("Client connected: %s (total=%d)", websocket.remote_address, len(_clients))

    try:
        async for raw in websocket:
            try:
                msg = json.loads(raw)
                gesture = msg.get("gesture", "rest")
                confidence = float(msg.get("confidence", 1.0))
                log.info("Received gesture: %s", gesture)

                if _env is not None:
                    # Only enqueue — never call mj_step from here
                    _env.request_gesture(gesture)
                    await broadcast(
                        {
                            "type": "gesture",
                            "gesture": gesture,
                            "confidence": confidence,
                            "source": "ws_bridge",
                            "timestamp": int(time.time() * 1000),
                        }
                    )
                    await websocket.send(json.dumps({"status": "ok", "gesture": gesture}))
                else:
                    await websocket.send(json.dumps({"status": "env_not_ready"}))

            except json.JSONDecodeError:
                await websocket.send(json.dumps({"status": "error", "msg": "invalid JSON"}))
            except Exception as e:
                log.error("Error: %s", e)
                await websocket.send(json.dumps({"status": "error", "msg": str(e)}))
    finally:
        _clients.discard(websocket)
        log.info("Client disconnected: %s (total=%d)", websocket.remote_address, len(_clients))

async def run_server():
    host = os.getenv("WS_HOST", "localhost")
    port = int(os.getenv("WS_PORT", 8765))
    log.info("WebSocket server listening on ws://%s:%d", host, port)
    async with serve(handle, host, port):
        await asyncio.get_running_loop().create_future()