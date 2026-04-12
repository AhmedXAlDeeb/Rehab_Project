# envs/hand_env.py
import mujoco
import mujoco.viewer
import numpy as np
import queue
from pathlib import Path
from envs.gestures import get_action

MODEL_PATH = Path(__file__).parent.parent / "models" / "myo_sim" / "hand" / "myohand.xml"

class HandEnv:
    def __init__(self):
        self.model = mujoco.MjModel.from_xml_path(str(MODEL_PATH))
        self.data = mujoco.MjData(self.model)
        self.current_gesture = "rest"
        self.gesture_queue = queue.Queue()
        print(f"Model loaded: {self.model.nu} actuators, {self.model.nq} DOF")

    def request_gesture(self, gesture_name: str):
        """Called from any thread — just enqueues, never touches MuJoCo."""
        self.gesture_queue.put(gesture_name)

    def apply_pending(self):
        """Called only from the main thread inside the render loop."""
        try:
            gesture_name = self.gesture_queue.get_nowait()
            action = get_action(gesture_name)
            n = self.model.nu
            action = np.resize(action, n)
            action = np.clip(action, 0.0, 1.0)
            self.data.ctrl[:] = action
            self.current_gesture = gesture_name
        except queue.Empty:
            pass
        mujoco.mj_step(self.model, self.data)

    def close(self):
        pass