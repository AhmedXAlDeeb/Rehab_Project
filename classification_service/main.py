from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import torch
import torch.nn as nn
import torch.nn.functional as F
import uvicorn

# --- 1. Define the Model Architecture (From Notebook) ---
class EMGCNN(nn.Module):
    def __init__(self, num_classes=53):
        super(EMGCNN, self).__init__()
        # Input shape: (Batch, 12, 400)
        self.conv1 = nn.Conv1d(in_channels=12, out_channels=64, kernel_size=3)
        self.pool1 = nn.MaxPool1d(kernel_size=2)
        self.conv2 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=3)
        self.pool2 = nn.MaxPool1d(kernel_size=2)
        self.conv3 = nn.Conv1d(in_channels=128, out_channels=64, kernel_size=3)
        self.dropout = nn.Dropout(0.5)
        # Flattened size
        self.fc1 = nn.Linear(64 * 96, 128)
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = self.pool1(x)
        x = F.relu(self.conv2(x))
        x = self.pool2(x)
        x = F.relu(self.conv3(x))
        x = torch.flatten(x, 1)
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        return x

# --- 2. Initialize API and Load Model ---
app = FastAPI(title="Ninapro DB2 EMG Classifier", description="Classifies 12-channel EMG signals into 53 gesture classes.")

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = EMGCNN(num_classes=53).to(device)

# TODO: Update this path to point to your actual downloaded .pt file
CHECKPOINT_PATH = "emg_model_epoch_7.pt" 

try:
    model.load_state_dict(torch.load(CHECKPOINT_PATH, map_location=device))
    print(f"Successfully loaded model weights from {CHECKPOINT_PATH}")
except FileNotFoundError:
    print(f"WARNING: Checkpoint {CHECKPOINT_PATH} not found. Running with untrained weights for demonstration.")

model.eval()

# --- 3. Define Input Schema ---
class SignalInput(BaseModel):
    # Expecting a nested list of floats: 12 lists (channels), each containing 400 floats (time steps)
    signal: List[List[float]] = Field(
        ...,
        description="A 2D array representing EMG data. Expected shape: [12 channels, 400 timesteps]"
    )

# --- 4. Define Prediction Endpoint ---
@app.post("/predict")
async def predict_emg(data: SignalInput):
    try:
        # Convert incoming JSON list to a PyTorch tensor
        input_tensor = torch.tensor(data.signal, dtype=torch.float32)
        
        # Enforce strict shape checking based on notebook requirements
        if input_tensor.shape != (12, 400):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid input shape. Expected (12, 400), but got {tuple(input_tensor.shape)}"
            )
        
        # Add the Batch dimension so shape becomes (1, 12, 400)
        input_tensor = input_tensor.unsqueeze(0).to(device)
        
        # Perform Inference
        with torch.no_grad():
            outputs = model(input_tensor)
            _, predicted_class = torch.max(outputs.data, 1)
            
        return {
            "predicted_class": predicted_class.item(),
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)