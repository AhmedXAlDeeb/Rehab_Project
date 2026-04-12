# viz/run_viewer.py
import mujoco
import mujoco.viewer
import threading
import asyncio
from dotenv import load_dotenv

load_dotenv()

from envs.hand_env import HandEnv
from bridge.ws_server import set_env, run_server

def start_ws_server(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_server())

def main():
    env = HandEnv()
    set_env(env)

    loop = asyncio.new_event_loop()
    ws_thread = threading.Thread(target=start_ws_server, args=(loop,), daemon=True)
    ws_thread.start()

    print("Viewer running. Connect to ws://localhost:8765")
    print("Test with: uv run python bridge/mock_client.py")

    with mujoco.viewer.launch_passive(env.model, env.data) as viewer:
        with viewer.lock():
            viewer.opt.geomgroup[0] = 1
            viewer.opt.geomgroup[1] = 1
            viewer.opt.geomgroup[2] = 1
            viewer.opt.geomgroup[3] = 1
            viewer.opt.geomgroup[4] = 1
            viewer.opt.flags[mujoco.mjtVisFlag.mjVIS_SKIN] = 1
        viewer.sync()

        while viewer.is_running():
            env.apply_pending()   # mj_step happens here, on the main thread
            viewer.sync()

if __name__ == "__main__":
    main()