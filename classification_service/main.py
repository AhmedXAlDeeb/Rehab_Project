from pathlib import Path
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import torch
import torch.nn as nn
import torch.nn.functional as F
import uvicorn


N_CHANNELS = 12
N_TIMESTEPS = 400
N_CLASSES = 53
DEFAULT_CHECKPOINT_PATH = Path(__file__).parent / "emg_model_epoch_7.pt"


class EMGCNN(nn.Module):
    def __init__(self, num_classes: int = N_CLASSES):
        super().__init__()
        self.conv1 = nn.Conv1d(in_channels=N_CHANNELS, out_channels=64, kernel_size=3)
        self.pool1 = nn.MaxPool1d(kernel_size=2)
        self.conv2 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=3)
        self.pool2 = nn.MaxPool1d(kernel_size=2)
        self.conv3 = nn.Conv1d(in_channels=128, out_channels=64, kernel_size=3)
        self.dropout = nn.Dropout(0.5)
        self.fc1 = nn.Linear(64 * 96, 128)
        self.fc2 = nn.Linear(128, num_classes)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
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


class SignalInput(BaseModel):
    signal: List[List[float]] = Field(
        ...,
        description="A 2D EMG matrix with shape [12, 400] or [400, 12].",
    )


class SyntheticSample(BaseModel):
    signal: List[List[float]] = Field(..., description="Synthetic EMG signal with shape [12, 400] or [400, 12].")
    label: int = Field(..., ge=0, lt=N_CLASSES)


class FineTuneRequest(BaseModel):
    samples: List[SyntheticSample] = Field(..., min_length=1, max_length=3000)
    epochs: int = Field(default=3, ge=1, le=50)
    batch_size: int = Field(default=32, ge=1, le=256)
    learning_rate: float = Field(default=1e-4, gt=0.0, le=1.0)
    checkpoint_out: str | None = Field(default=None)


def _normalize_signal_shape(signal: List[List[float]]) -> torch.Tensor:
    tensor = torch.tensor(signal, dtype=torch.float32)
    if tensor.shape == (N_CHANNELS, N_TIMESTEPS):
        return tensor
    if tensor.shape == (N_TIMESTEPS, N_CHANNELS):
        return tensor.transpose(0, 1)
    raise ValueError(f"Invalid input shape. Expected (12, 400) or (400, 12), but got {tuple(tensor.shape)}")


app = FastAPI(
    title="Ninapro DB2 EMG Classifier",
    description="Classifies 12-channel EMG signals and supports synthetic-data fine-tuning.",
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = EMGCNN(num_classes=N_CLASSES).to(device)
checkpoint_path = DEFAULT_CHECKPOINT_PATH

if checkpoint_path.exists():
    model.load_state_dict(torch.load(checkpoint_path, map_location=device))
    print(f"Successfully loaded model weights from {checkpoint_path}")
else:
    print(f"WARNING: Checkpoint {checkpoint_path} not found. Running with untrained weights for demonstration.")

model.eval()


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "device": str(device),
        "checkpoint": str(checkpoint_path),
        "checkpoint_exists": checkpoint_path.exists(),
    }


@app.post("/predict")
async def predict_emg(data: SignalInput) -> dict:
    try:
        input_tensor = _normalize_signal_shape(data.signal).unsqueeze(0).to(device)
        with torch.no_grad():
            outputs = model(input_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted_class = torch.max(probabilities, 1)
        return {
            "predicted_class": int(predicted_class.item()),
            "confidence": float(confidence.item()),
            "status": "success",
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/finetune_on_synthetic")
async def finetune_on_synthetic(body: FineTuneRequest) -> dict:
    try:
        x_list: list[torch.Tensor] = []
        y_list: list[int] = []
        for sample in body.samples:
            x_list.append(_normalize_signal_shape(sample.signal))
            y_list.append(sample.label)

        x_tensor = torch.stack(x_list, dim=0).to(device)
        y_tensor = torch.tensor(y_list, dtype=torch.long, device=device)

        criterion = nn.CrossEntropyLoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=body.learning_rate)

        model.train()
        total = x_tensor.shape[0]
        first_epoch_loss = None
        last_epoch_loss = None

        for _ in range(body.epochs):
            perm = torch.randperm(total, device=device)
            running_loss = 0.0
            batches = 0
            for start in range(0, total, body.batch_size):
                idx = perm[start : start + body.batch_size]
                xb = x_tensor[idx]
                yb = y_tensor[idx]

                optimizer.zero_grad()
                logits = model(xb)
                loss = criterion(logits, yb)
                loss.backward()
                optimizer.step()

                running_loss += float(loss.detach().item())
                batches += 1

            epoch_loss = running_loss / max(batches, 1)
            if first_epoch_loss is None:
                first_epoch_loss = epoch_loss
            last_epoch_loss = epoch_loss

        model.eval()

        out_path = Path(body.checkpoint_out) if body.checkpoint_out else checkpoint_path
        torch.save(model.state_dict(), out_path)

        return {
            "status": "success",
            "samples_used": total,
            "epochs": body.epochs,
            "initial_loss": first_epoch_loss,
            "final_loss": last_epoch_loss,
            "checkpoint_saved_to": str(out_path),
        }
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)