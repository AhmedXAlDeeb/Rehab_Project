# bridge/ws_server.py
import asyncio
import json
import os
import logging
from websockets.server import serve

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ws_server")

_env = None

def set_env(env):
    global _env
    _env = env

async def handle(websocket):
    log.info("Client connected: %s", websocket.remote_address)
    async for raw in websocket:
        try:
            msg = json.loads(raw)
            gesture = msg.get("gesture", "rest")
            log.info("Received gesture: %s", gesture)

            if _env is not None:
                # Only enqueue — never call mj_step from here
                _env.request_gesture(gesture)
                await websocket.send(json.dumps({"status": "ok", "gesture": gesture}))
            else:
                await websocket.send(json.dumps({"status": "env_not_ready"}))

        except json.JSONDecodeError:
            await websocket.send(json.dumps({"status": "error", "msg": "invalid JSON"}))
        except Exception as e:
            log.error("Error: %s", e)
            await websocket.send(json.dumps({"status": "error", "msg": str(e)}))

async def run_server():
    host = os.getenv("WS_HOST", "localhost")
    port = int(os.getenv("WS_PORT", 8765))
    log.info("WebSocket server listening on ws://%s:%d", host, port)
    async with serve(handle, host, port):
        await asyncio.get_running_loop().create_future()