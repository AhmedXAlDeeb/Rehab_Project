# bridge/ws_server.py
import asyncio
import json
import os
import logging
import time
import base64
import threading
from io import BytesIO
import imageio
import sys
from pathlib import Path
from websockets.server import serve

# Add the parent directory to sys.path so we can import envs
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))

from envs.hand_env import HandEnv

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ws_server")

_env = None
_clients = set()
_current_frame = None

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

async def video_broadcast():
    """Streams MJPEG frames to all connected websocket clients."""
    target_fps = 30
    frame_interval = 1.0 / target_fps
    
    while True:
        start_time = time.time()
        
        if _clients and _current_frame is not None:
            try:
                # Encode the frame in the background thread
                frame = _current_frame
                bio = BytesIO()
                imageio.imwrite(bio, frame, format="JPEG")
                b64 = base64.b64encode(bio.getvalue()).decode('utf-8')
                    
                payload = {
                    "type": "video_frame",
                    "image": "data:image/jpeg;base64," + b64
                }
                await broadcast(payload)
            except Exception as e:
                log.error(f"Error generating/sending frame: {e}")
                
        elapsed = time.time() - start_time
        sleep_time = max(0, frame_interval - elapsed)
        await asyncio.sleep(sleep_time)

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
                    payload = {
                        "type": "gesture",
                        "gesture": gesture,
                        "confidence": confidence,
                        "source": "ws_bridge",
                        "timestamp": int(time.time() * 1000),
                    }
                    if "signal" in msg:
                        payload["signal"] = msg["signal"]
                    await broadcast(payload)
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

async def wrapper():
    host = os.getenv("WS_HOST", "localhost")
    port = int(os.getenv("WS_PORT", 8765))
    log.info("WebSocket server listening on ws://%s:%d", host, port)
    
    server = serve(handle, host, port)
    
    await asyncio.gather(
        server,
        video_broadcast()
    )

def start_network():
    asyncio.run(wrapper())

def main():
    env = HandEnv(render_mode="rgb_array")
    set_env(env)

    # Start network tasks in separate thread
    net_thread = threading.Thread(target=start_network, daemon=True)
    net_thread.start()

    log.info("Standalone WebSocket Server running. Connect React App to ws://localhost:8765")
    
    target_fps = 30
    frame_interval = 1.0 / target_fps
    last_render_time = time.time()
    
    try:
        # Simulation loop runs on main thread for stability
        while True:
            env.apply_pending()  # Steps simulation physics
            
            # Render on the main thread where the OpenGL context was created
            now = time.time()
            if now - last_render_time >= frame_interval:
                global _current_frame
                _current_frame = env.get_frame()
                last_render_time = now

            time.sleep(0.002)    # 500 Hz physics step
    except KeyboardInterrupt:
        log.info("Shutting down streamer...")
        env.close()

if __name__ == "__main__":
    main()