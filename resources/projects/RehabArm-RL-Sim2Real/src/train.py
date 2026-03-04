import os
import time
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor
from env import RehabArmEnv
from utils import plot_learning_curve

def train():
    # Folder setup
    os.makedirs("models", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    log_file = "logs/progress.csv"
    
    # Initialize environment and wrap with Monitor
    env = RehabArmEnv()
    env = Monitor(env, log_file)

    # PPO configuration
    model = PPO(
        "MlpPolicy", 
        env, 
        verbose=1, 
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        gamma=0.99,
        device="cpu"
    )

    print("--- Training Started ---")
    model.learn(total_timesteps=150000, progress_bar=True)
    
    # Save the model
    model.save("models/rehab_arm_ppo")
    print("Model saved to models/rehab_arm_ppo.zip")

    # IMPORTANT: Close the environment to flush the Monitor logs to disk
    env.close()
    
    # Small delay for Windows file system synchronization
    print("Finalizing logs...")
    time.sleep(2)

    # Generate Learning Curve
    print("Attempting to plot results...")
    plot_learning_curve(csv_path=log_file, save_path="learning_curve.png")

if __name__ == "__main__":
    train()