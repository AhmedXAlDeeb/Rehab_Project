"""Record a video of a gesture sequence without opening a viewer window.

Run with:
    uv run python viz/record_video.py
"""
import numpy as np
import imageio
from envs.hand_env import HandEnv
from envs.gestures import KNOWN_GESTURES
import os

os.environ["MUJOCO_GL"] = "osmesa"  # headless rendering


def record(output_path: str = "output.mp4", fps: int = 30, hold_frames: int = 60):
    env = HandEnv(render_mode="rgb_array")
    frames = []

    for gesture in KNOWN_GESTURES:
        print(f"Recording: {gesture}")
        for _ in range(hold_frames):
            env.set_gesture(gesture)
            frame = env.env.render()
            if frame is not None:
                frames.append(frame)

    env.close()
    imageio.mimsave(output_path, frames, fps=fps)
    print(f"Saved {len(frames)} frames to {output_path}")


if __name__ == "__main__":
    record()