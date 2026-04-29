import os
import asyncio
import json
import logging
import threading
import time
import base64
from io import BytesIO
import imageio

from dotenv import load_dotenv

import numpy as np

# ensure headless rendering
os.environ["MUJOCO_GL"] = "osmesa"
# Load environment before any other modules if needed, though mostly standard
load_dotenv()

from envs.hand_env import HandEnv
from bridge.ws_server import run_server, set_env, _clients

import bridge.ws_server as ws_server

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ws_streamer")

async def video_broadcast():
    """Streams MJPEG frames to all connected websocket clients."""
    target_fps = 30
    frame_interval = 1.0 / target_fps
    
    while True:
        start_time = time.time()
        
        # Only render and encode if we have connected clients
        env = ws_server._env
        if _clients and env is not None:
            frame = env.get_frame()
            if frame is not None:
                bio = BytesIO()
                imageio.imwrite(bio, frame, extension=".jpg")
                b64 = base64.b64encode(bio.getvalue()).decode('utf-8')
                
                payload = json.dumps({
                    "type": "video_frame",
                    "image": "data:image/jpeg;base64," + b64
                })
                
                # Broadcast sequentially to avoid thread safety issues
                disconnected = []
                for client in list(_clients):
                    try:
                        await client.send(payload)
                    except Exception:
                        disconnected.append(client)
                for client in disconnected:
                    _clients.discard(client)
        
        elapsed = time.time() - start_time
        sleep_time = max(0, frame_interval - elapsed)
        await asyncio.sleep(sleep_time)

async def wrapper(env):
    # Run the server and broadcasting concurrently
    await asyncio.gather(
        run_server(),
        video_broadcast()
    )

def start_network(env):
    asyncio.run(wrapper(env))

def main():
    # render_mode must be set for get_frame to work
    env = HandEnv(render_mode="rgb_array")
    set_env(env)

    # Start network tasks in separate thread
    net_thread = threading.Thread(target=start_network, args=(env,), daemon=True)
    net_thread.start()

    print("Headless Viewer & Streamer running. Connect React App to ws://localhost:8765")
    
    try:
        # Simulation loop runs on main thread for stability
        while True:
            env.apply_pending()  # Steps simulation physics
            time.sleep(0.002)    # 500 Hz physics step
    except KeyboardInterrupt:
        print("Shutting down streamer...")
        env.close()

if __name__ == "__main__":
    main()