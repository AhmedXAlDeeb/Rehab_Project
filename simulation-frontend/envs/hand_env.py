# envs/hand_env.py
import mujoco
import mujoco.viewer
import numpy as np
import queue
import threading
from pathlib import Path
from envs.gestures import get_action

MODEL_PATH = Path(__file__).parent.parent / "models" / "myo_sim" / "hand" / "myohand.xml"

class HandEnv:
    def __init__(self, render_mode=None):
        self.model = mujoco.MjModel.from_xml_path(str(MODEL_PATH))
        self.data = mujoco.MjData(self.model)
        self.current_gesture = "rest"
        self.gesture_queue = queue.Queue()
        self.render_mode = render_mode
        self.renderer = None
        self.lock = threading.Lock()
        
        self.camera = mujoco.MjvCamera()
        mujoco.mjv_defaultFreeCamera(self.model, self.camera)
        
        # Calculate kinematics to get correct body positions
        mujoco.mj_forward(self.model, self.data)
        
        # Focus on the center of the hand (the 3rd metacarpal)
        body_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, "thirdmc")
        if body_id >= 0:
            hand_pos = self.data.xpos[body_id]
        else:
            hand_pos = np.array([0.0, -0.5, 1.4])
            
        # Zoom in on the hand
        self.camera.distance = 0.5  # Zoomed in closely
        self.camera.azimuth = 140.0
        self.camera.elevation = -20.0
        self.camera.lookat[:] = hand_pos
        
        if render_mode == "rgb_array":
            self.renderer = mujoco.Renderer(self.model, 480, 640)
        print(f"Model loaded: {self.model.nu} actuators, {self.model.nq} DOF")

    def get_frame(self):
        with self.lock:
            if self.renderer:
                self.renderer.update_scene(self.data, camera=self.camera)
                return self.renderer.render()
        return None

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
            with self.lock:
                self.data.ctrl[:] = action
                self.current_gesture = gesture_name
        except queue.Empty:
            pass
        
        with self.lock:
            mujoco.mj_step(self.model, self.data)

    def close(self):
        pass