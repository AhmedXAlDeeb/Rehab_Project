import os
import time
import numpy as np
import mujoco
from envs.hand_env import HandEnv
import imageio

def test_camera():
    env = HandEnv(render_mode="rgb_array")
    
    # Do a few steps
    for _ in range(10):
        env.apply_pending()
        
    cam = mujoco.MjvCamera()
    mujoco.mjv_defaultFreeCamera(env.model, cam)
    
    print(f"Default camera distance: {cam.distance}")
    print(f"Default camera azimuth: {cam.azimuth}")
    print(f"Default camera elevation: {cam.elevation}")
    print(f"Default camera lookat: {cam.lookat}")

    # Zoom in
    cam.distance = 0.8
    cam.azimuth = 180
    cam.elevation = -10
    
    # We can render and save to test
    env.renderer.update_scene(env.data, camera=cam)
    frame = env.renderer.render()
    imageio.imwrite("test_frame_zoom.jpg", frame)
    print("Saved test_frame_zoom.jpg")

if __name__ == "__main__":
    test_camera()
