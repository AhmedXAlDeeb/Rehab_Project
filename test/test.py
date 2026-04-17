import scipy.io as sio
import numpy as np
import os

# Get the exact folder where test.py is located
current_dir = os.path.dirname(os.path.abspath(__file__))

# Build the absolute path to the s1 folder
folder_path = os.path.join(current_dir, 's1')

files = ['S1_A1_E1.mat', 'S1_A1_E2.mat', 'S1_A1_E3.mat']

all_labels = set()

print(f"Looking for files in: {folder_path}\n")

for file_name in files:
    file_path = os.path.join(folder_path, file_name)
    
    try:
        # Load the .mat file
        mat_data = sio.loadmat(file_path)
        
        # NinaPro guidelines state labels are in 'restimulus' (refined) or 'stimulus'
        if 'restimulus' in mat_data:
            labels = mat_data['restimulus'].flatten()
        elif 'stimulus' in mat_data:
            labels = mat_data['stimulus'].flatten()
        else:
            print(f"Could not find label arrays in {file_name}")
            continue
            
        # Get unique labels in this specific exercise
        unique_labels = np.unique(labels)
        print(f"{file_name} contains {len(unique_labels)} unique labels: {unique_labels}")
        
        # Add to our global set for this subject
        all_labels.update(unique_labels)
        
    except FileNotFoundError:
        print(f"Error: Could not find {file_path}")

# Convert set to sorted list for analysis
sorted_all_labels = sorted(list(all_labels))

print("\n" + "="*50)
print("FINAL LABEL ANALYSIS")
print("="*50)

# 1. Total number of actual classes found
total_classes = len(sorted_all_labels)
print(f"Total unique classes found (including rest): {total_classes}")

# 2. The highest label ID
max_label = max(sorted_all_labels) if sorted_all_labels else 0
print(f"Highest label ID found: {max_label}")

# 3. Find the gaps (the phantom classes)
expected_labels = set(range(max_label + 1))
missing_labels = expected_labels - all_labels

print(f"\nMissing label IDs between 0 and {max_label}: {sorted(list(missing_labels))}")
print("="*50)