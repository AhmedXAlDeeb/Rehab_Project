import time
import numpy as np
import mujoco.viewer
from stable_baselines3 import PPO
from env import RehabArmEnv

def visualize():
    print("Loading model...")
    try:
        model = PPO.load("models/rehab_arm_ppo")
    except:
        print("Model file not found. Please train first.")
        return

    env = RehabArmEnv()
    
    with mujoco.viewer.launch_passive(env.model, env.data) as viewer:
        # Cinematic camera setup
        viewer.cam.azimuth = 135
        viewer.cam.elevation = -25
        viewer.cam.distance = 2.0
        viewer.cam.lookat = np.array([0.25, 0, 0.4])

        print("Visualizer active. Observe movement smoothness.")
        
        obs, _ = env.reset()
        
        while viewer.is_running():
            step_start = time.time()

            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, _ = env.step(action)
            
            viewer.sync()
            
            # Match the simulation speed
            elapsed = time.time() - step_start
            if elapsed < env.model.opt.timestep:
                time.sleep(env.model.opt.timestep - elapsed)
            
            if terminated or truncated:
                time.sleep(1.0) # Highlight the success point
                obs, _ = env.reset()

if __name__ == "__main__":
    visualize()