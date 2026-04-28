from pathlib import Path
from typing import List, Optional
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import torch
import torch.nn as nn
import numpy as np
import uvicorn
import httpx

N_CHANNELS = 12
N_TIMESTEPS = 400
VAE_LATENT_DIM = 64
VAE_CONDITION_DIM = 16

DEFAULT_CHECKPOINT_PATH = Path("../test/cvae_db2_best.pt")


class NotebookStyleConditionalVAE(nn.Module):
    def __init__(self):
        super().__init__()
        self.latent_dim = VAE_LATENT_DIM
        self.decoder = nn.Sequential(
            nn.Linear(self.latent_dim + VAE_CONDITION_DIM, 512),
            nn.ReLU(),
            nn.Linear(512, N_CHANNELS * N_TIMESTEPS),
        )

    def decode(self, z: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        out = self.decoder(torch.cat([z, cond], dim=-1))
        out = torch.tanh(out)
        return out.view(z.shape[0], N_CHANNELS, N_TIMESTEPS)


class GenerationFlags(BaseModel):
    fatigue: float = Field(default=0.0, ge=0.0, le=1.0)
    electrode_quality: float = Field(default=1.0, ge=0.0, le=1.0)
    session_idx_norm: float = Field(default=0.0, ge=0.0, le=1.0)
    amputation: float = Field(default=0.0, ge=0.0, le=1.0)


class VAEGenerateRequest(BaseModel):
    subject_idx_0based: int = Field(default=0, ge=0)
    gesture_0based: int = Field(default=0, ge=0, le=52)
    flags: GenerationFlags = Field(default_factory=GenerationFlags)
    n_samples: int = Field(default=10, ge=1, le=500)
    seed: Optional[int] = None


class VAEFinetuneRequest(BaseModel):
    subject_idx_0based: int = Field(default=0, ge=0)
    gesture_0based: int = Field(default=0, ge=0, le=52)
    flags: GenerationFlags = Field(default_factory=GenerationFlags)
    n_samples: int = Field(default=10, ge=1, le=500)
    seed: Optional[int] = None
    finetune_epochs: int = Field(default=3, ge=1, le=50)
    finetune_batch_size: int = Field(default=32, ge=1, le=256)
    finetune_learning_rate: float = Field(default=1e-4, gt=0.0, le=1.0)
    checkpoint_out: Optional[str] = None
    save_samples: bool = Field(
        default=True, description="Whether to save generated samples to file"
    )
    samples_output_dir: str = Field(
        default="./generated_samples", description="Directory to save generated samples"
    )


CLASSIFIER_FINETUNE_URL = "http://localhost:8000/finetune_on_synthetic"


app = FastAPI(
    title="EMG Generation Service",
    description="Generates synthetic EMG signals using a Conditional VAE.",
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = NotebookStyleConditionalVAE().to(device)
checkpoint_path = DEFAULT_CHECKPOINT_PATH

loaded = False
load_error = None
if checkpoint_path.exists():
    try:
        state = torch.load(checkpoint_path, map_location=device)
        if isinstance(state, dict) and "state_dict" in state:
            state = state["state_dict"]
        model.load_state_dict(state, strict=False)
        loaded = True
        print(f"Successfully loaded VAE model weights from {checkpoint_path}")
    except Exception as e:
        load_error = str(e)
        print(f"ERROR: Failed to load VAE model weights: {e}")
else:
    print(
        f"WARNING: Checkpoint {checkpoint_path} not found. Running with untrained weights for demonstration."
    )

model.eval()


def _build_condition(
    subject_idx: int, gesture: int, flags: GenerationFlags
) -> np.ndarray:
    base = np.array(
        [
            float(subject_idx),
            float(gesture),
            float(flags.fatigue),
            float(flags.electrode_quality),
            float(flags.session_idx_norm),
            float(flags.amputation),
        ],
        dtype=np.float32,
    )
    pad = np.zeros(VAE_CONDITION_DIM - base.shape[0], dtype=np.float32)
    return np.concatenate([base, pad], axis=0)


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "device": str(device),
        "checkpoint": str(checkpoint_path),
        "checkpoint_exists": checkpoint_path.exists(),
        "model_loaded": loaded,
        "load_error": load_error,
    }


@app.post("/generate")
async def generate_emg(body: VAEGenerateRequest) -> dict:
    try:
        if body.seed is not None:
            torch.manual_seed(body.seed)
            np.random.seed(body.seed)

        cond = _build_condition(
            body.subject_idx_0based, body.gesture_0based, body.flags
        )
        cond_t = (
            torch.tensor(cond, dtype=torch.float32, device=device)
            .unsqueeze(0)
            .repeat(body.n_samples, 1)
        )
        z = torch.randn(body.n_samples, model.latent_dim, device=device)

        with torch.no_grad():
            out = model.decode(z, cond_t).cpu().numpy()

        payload = [arr.astype(np.float32).tolist() for arr in out]

        return {
            "status": "success",
            "shape": [N_CHANNELS, N_TIMESTEPS],
            "gesture_label": body.gesture_0based,
            "n_samples": body.n_samples,
            "samples": payload,
            "model_loaded": loaded,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/finetune_on_generated")
async def finetune_on_generated(body: VAEFinetuneRequest):
    try:
        cond = _build_condition(body.subject_idx_0based, body.gesture_0based, body.flags)
        cond_t = torch.tensor(cond, dtype=torch.float32, device=device).unsqueeze(0).repeat(body.n_samples, 1)
        z = torch.randn(body.n_samples, model.latent_dim, device=device)

        with torch.no_grad():
            out = model.decode(z, cond_t).cpu().numpy()

        samples_list = [arr.astype(np.float32).tolist() for arr in out]

        samples_output_path = None
        if body.save_samples:
            output_dir = Path(body.samples_output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            
            subject_dir = output_dir / f"subject_{body.subject_idx_0based}"
            subject_dir.mkdir(parents=True, exist_ok=True)
            
            gesture_file = subject_dir / f"gesture_{body.gesture_0based}.npz"
            np.savez(
                gesture_file,
                samples=np.array(samples_list),
                gesture=body.gesture_0based,
                subject=body.subject_idx_0based,
                flags={
                    "fatigue": body.flags.fatigue,
                    "electrode_quality": body.flags.electrode_quality,
                    "session_idx_norm": body.flags.session_idx_norm,
                    "amputation": body.flags.amputation,
                }
            )
            samples_output_path = str(gesture_file)

        finetune_payload = {
            "samples": [
                {"signal": sample, "label": body.gesture_0based}
                for sample in samples_list
            ],
            "epochs": body.finetune_epochs,
            "batch_size": body.finetune_batch_size,
            "learning_rate": body.finetune_learning_rate,
            "checkpoint_out": body.checkpoint_out,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    CLASSIFIER_FINETUNE_URL,
                    json=finetune_payload,
                    timeout=120.0
                )

            if response.status_code != 200:
                return {
                    "status": "partial",
                    "generation": {
                        "status": "success",
                        "n_samples": body.n_samples,
                        "samples_saved_to": samples_output_path,
                    },
                    "finetune_error": f"Classifier returned {response.status_code}: {response.text}",
                }

            finetune_result = response.json()
        except httpx.RequestError as exc:
            return {
                "status": "partial",
                "generation": {
                    "status": "success",
                    "n_samples": body.n_samples,
                    "samples_saved_to": samples_output_path,
                },
                "finetune_error": f"Could not reach classifier service: {str(exc)}",
            }

        return {
            "status": "success",
            "generation": {
                "status": "success",
                "shape": [N_CHANNELS, N_TIMESTEPS],
                "gesture_label": body.gesture_0based,
                "n_samples": body.n_samples,
                "samples_saved_to": samples_output_path,
                "model_loaded": loaded,
            },
            "finetune": finetune_result,
        }

    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)
