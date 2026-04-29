import os
import time
import numpy as np
from envs.hand_env import HandEnv

def test_render():
    env = HandEnv(render_mode="rgb_array")
    
    # Do a few steps
    for _ in range(10):
        env.apply_pending()
        
    frame = env.get_frame()
    if frame is not None:
        print(f"Frame shape: {frame.shape}, dtype: {frame.dtype}")
        print(f"Max value: {frame.max()}, Min value: {frame.min()}, Mean: {frame.mean()}")
        import imageio
        imageio.imwrite("test_frame.jpg", frame)
        print("Saved test_frame.jpg")
    else:
        print("Frame is None")

if __name__ == "__main__":
    test_render()
