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
DEFAULT_CHECKPOINT_PATH = Path(__file__).parent / "emg_model_finetuned.pt"
FALLBACK_CHECKPOINT_PATH = Path(__file__).parent / "emg_model_epoch_7"


class EMGCNN(nn.Module):
    def __init__(self, num_classes=53): 
        super(EMGCNN, self).__init__()
        # Larger kernel size initially to capture wider temporal features
        self.conv1 = nn.Conv1d(in_channels=12, out_channels=64, kernel_size=5, padding=2)
        self.bn1 = nn.BatchNorm1d(64) 
        self.pool1 = nn.MaxPool1d(kernel_size=2)
        
        self.conv2 = nn.Conv1d(in_channels=64, out_channels=128, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm1d(128) 
        self.pool2 = nn.MaxPool1d(kernel_size=2)
        
        self.conv3 = nn.Conv1d(in_channels=128, out_channels=256, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm1d(256) 
        self.pool3 = nn.MaxPool1d(kernel_size=2)
        
        self.conv4 = nn.Conv1d(in_channels=256, out_channels=128, kernel_size=3, padding=1)
        self.bn4 = nn.BatchNorm1d(128) 
        self.pool4 = nn.MaxPool1d(kernel_size=2)
        
        self.dropout = nn.Dropout(0.5)
        
        # 400 window / (2*2*2*2 pooling) = 25
        self.fc1 = nn.Linear(128 * 25, 256)
        self.fc2 = nn.Linear(256, num_classes)

    def forward(self, x):
        x = self.pool1(F.relu(self.bn1(self.conv1(x))))
        x = self.pool2(F.relu(self.bn2(self.conv2(x))))
        x = self.pool3(F.relu(self.bn3(self.conv3(x))))
        x = self.pool4(F.relu(self.bn4(self.conv4(x))))
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
    if tensor.shape == (N_TIMESTEPS, N_CHANNELS):
        tensor = tensor.transpose(0, 1)
    
    if tensor.shape == (N_CHANNELS, N_TIMESTEPS):
        # Normalize per channel (Instance Normalization)
        mean = tensor.mean(dim=1, keepdim=True)
        std = tensor.std(dim=1, keepdim=True) + 1e-8
        return (tensor - mean) / std
        
    raise ValueError(f"Invalid input shape. Expected (12, 400) or (400, 12), but got {tuple(tensor.shape)}")


app = FastAPI(
    title="Ninapro DB2 EMG Classifier",
    description="Classifies 12-channel EMG signals and supports synthetic-data fine-tuning.",
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = EMGCNN(num_classes=N_CLASSES).to(device)
checkpoint_path = DEFAULT_CHECKPOINT_PATH

# Try primary checkpoint first (directory format = full model saved with torch.save(model, ...))
if checkpoint_path.exists():
    try:
        loaded = torch.load(checkpoint_path, map_location=device)
        # Directory format saves the full model object, not just state_dict
        if isinstance(loaded, nn.Module):
            model = loaded.to(device)
            print(f"[INIT] ✅ Full model loaded (torch.save(model)) from: {checkpoint_path}")
        elif isinstance(loaded, dict):
            model.load_state_dict(loaded)
            print(f"[INIT] ✅ State-dict loaded from: {checkpoint_path}")
        else:
            print(f"[INIT] ⚠️  Unknown checkpoint format: {type(loaded)}. Trying as state_dict.")
            model.load_state_dict(loaded)
        print(f"[INIT]    Device : {device}")
        print(f"[INIT]    Classes: {N_CLASSES}  |  Channels: {N_CHANNELS}  |  Timesteps: {N_TIMESTEPS}")
    except Exception as e:
        print(f"[INIT] ❌ Failed to load primary checkpoint '{checkpoint_path}': {e}")
        # Try fallback .pt file
        if FALLBACK_CHECKPOINT_PATH.exists():
            try:
                model.load_state_dict(torch.load(FALLBACK_CHECKPOINT_PATH, map_location=device))
                checkpoint_path = FALLBACK_CHECKPOINT_PATH
                print(f"[INIT] ✅ Fallback checkpoint loaded from: {checkpoint_path}")
                print(f"[INIT]    Device : {device}")
                print(f"[INIT]    Classes: {N_CLASSES}  |  Channels: {N_CHANNELS}  |  Timesteps: {N_TIMESTEPS}")
            except Exception as e2:
                print(f"[INIT] ❌ Fallback also failed: {e2}")
                print(f"[INIT]    Running with UNTRAINED weights — predictions will be random!")
        else:
            print(f"[INIT] ⚠️  Fallback checkpoint also NOT FOUND: {FALLBACK_CHECKPOINT_PATH}")
            print(f"[INIT]    Running with UNTRAINED weights — predictions will be random!")
else:
    print(f"[INIT] ⚠️  Primary checkpoint NOT FOUND at: {checkpoint_path}")
    if FALLBACK_CHECKPOINT_PATH.exists():
        try:
            model.load_state_dict(torch.load(FALLBACK_CHECKPOINT_PATH, map_location=device))
            checkpoint_path = FALLBACK_CHECKPOINT_PATH
            print(f"[INIT] ✅ Fallback checkpoint loaded from: {checkpoint_path}")
            print(f"[INIT]    Device : {device}")
            print(f"[INIT]    Classes: {N_CLASSES}  |  Channels: {N_CHANNELS}  |  Timesteps: {N_TIMESTEPS}")
        except Exception as e:
            print(f"[INIT] ❌ Fallback also failed: {e}")
            print(f"[INIT]    Running with UNTRAINED weights — predictions will be random!")
    else:
        print(f"[INIT] ⚠️  Fallback checkpoint also NOT FOUND: {FALLBACK_CHECKPOINT_PATH}")
        print(f"[INIT]    Running with UNTRAINED weights — predictions will be random!")

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
        # --- DIAGNOSTIC: RAW INPUT ---
        raw_rows = len(data.signal)
        raw_cols = len(data.signal[0]) if data.signal else 0
        print(f"\n[PREDICT] ── Incoming Signal ──────────────────────────")
        print(f"[PREDICT]   Raw list shape  : [{raw_rows}, {raw_cols}]")

        # Normalize shape to (12, 400)
        normalized = _normalize_signal_shape(data.signal)
        print(f"[PREDICT]   Normalized shape: {tuple(normalized.shape)}  (expected: ({N_CHANNELS}, {N_TIMESTEPS}))")

        # Add batch dim → (1, 12, 400)
        input_tensor = normalized.unsqueeze(0).to(device)
        print(f"[PREDICT]   Tensor to model : {tuple(input_tensor.shape)}  (expected: (1, {N_CHANNELS}, {N_TIMESTEPS}))")
        print(f"[PREDICT]   Value range     : min={input_tensor.min().item():.4f}  max={input_tensor.max().item():.4f}")

        with torch.no_grad():
            outputs = model(input_tensor)          # raw logits: (1, 53)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted_class = torch.max(probabilities, 1)

        # --- DIAGNOSTIC: MODEL OUTPUT ---
        pred_id   = int(predicted_class.item())
        conf_val  = float(confidence.item())
        top5_vals, top5_idxs = torch.topk(probabilities, k=5, dim=1)

        print(f"[PREDICT] ── Model Output ───────────────────────────────")
        print(f"[PREDICT]   Logits shape    : {tuple(outputs.shape)}")
        print(f"[PREDICT]   Logit range     : min={outputs.min().item():.4f}  max={outputs.max().item():.4f}")
        print(f"[PREDICT]   Top-5 classes   : {top5_idxs[0].tolist()}")
        print(f"[PREDICT]   Top-5 confidences: {[f'{v:.4f}' for v in top5_vals[0].tolist()]}")
        print(f"[PREDICT]   ✅ Predicted class: {pred_id}  |  Confidence: {conf_val:.4f} ({conf_val*100:.1f}%)")
        print(f"[PREDICT] ─────────────────────────────────────────────")

        return {
            "predicted_class": pred_id,
            "confidence": conf_val,
            "status": "success",
        }
    except ValueError as exc:
        print(f"[PREDICT] ❌ ValueError: {exc}")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        print(f"[PREDICT] ❌ Exception: {exc}")
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