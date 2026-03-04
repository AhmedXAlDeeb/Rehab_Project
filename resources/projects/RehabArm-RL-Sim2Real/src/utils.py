import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

def plot_learning_curve(csv_path="logs/progress.csv", save_path="learning_curve.png"):
    """
    Creates an academic-style reward plot from training logs.
    """
    if not os.path.exists(csv_path):
        # Check if maybe it's in the root or named slightly differently
        print(f"Error: {csv_path} not found.")
        print("Available files in logs/ folder:", os.listdir(os.path.dirname(csv_path)) if os.path.exists(os.path.dirname(csv_path)) else "None")
        return

    try:
        # SB3 Monitor files have a comment on the first line, so we skip it
        df = pd.read_csv(csv_path, skiprows=1)
        
        if df.empty:
            print("The log file is empty. Training might have been too short.")
            return

        # 'r' is reward, 'l' is episode length
        rewards = df['r'].values
        steps = np.cumsum(df['l'].values)
        
        window = 20
        plt.figure(figsize=(10, 5))
        
        # Plot raw data
        plt.plot(steps, rewards, color='cyan', alpha=0.2, label='Raw Reward')
        
        # Plot smoothed moving average
        if len(rewards) > window:
            smoothed = np.convolve(rewards, np.ones(window)/window, mode='valid')
            smoothed_steps = steps[window-1:]
            plt.plot(smoothed_steps, smoothed, color='blue', linewidth=2, label=f'Smoothed (MA-{window})')
        else:
            plt.plot(steps, rewards, color='blue', linewidth=2, label='Reward')
        
        plt.title("Rehabilitation Robotic Arm: RL Training Curve", fontsize=14)
        plt.xlabel("Total Environment Steps", fontsize=12)
        plt.ylabel("Episode Reward", fontsize=12)
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Successfully saved plot to {save_path}")
        # plt.show() # Optional: opens the window on your PC
        
    except Exception as e:
        print(f"An error occurred while plotting: {e}")

if __name__ == "__main__":
    plot_learning_curve()