import os
import sys
import argparse

# Add the src directory to the system path so we can import env.py
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from train import train
from visualize import visualize

def main():
    parser = argparse.ArgumentParser(description="RehabArm RL Sim-to-Real Pipeline")
    parser.add_argument("--mode", type=str, default="visualize", choices=["train", "visualize"],
                        help="Choose 'train' to start training or 'visualize' to see the agent.")
    
    args = parser.parse_args()

    if args.mode == "train":
        print("Starting Training Mode...")
        train()
    elif args.mode == "visualize":
        print("Starting Visualization Mode...")
        visualize()

if __name__ == "__main__":
    main()