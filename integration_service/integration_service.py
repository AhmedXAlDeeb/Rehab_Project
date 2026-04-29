from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware # <-- ADDED for CORS
from pydantic import BaseModel, Field
from typing import Any, List
import httpx
import websockets
import json
import uvicorn
import numpy as np
import torch
import torch.nn as nn
import asyncio # <-- ADDED for real-time sleep simulation

app = FastAPI(title="Gesture Integration Service", description="Bridges the AI service and WebSocket server.")

# --- ADD CORS MIDDLEWARE ---
# This allows your React frontend to communicate with this FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (adjust for production)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods including OPTIONS, POST, GET
    allow_headers=["*"],  # Allows all headers
)

# URLs for your existing services
AI_SERVICE_URL = "http://localhost:8000/predict"
CLASSIFIER_FINETUNE_URL = "http://localhost:8000/finetune_on_synthetic"
WS_SERVER_URL = "ws://localhost:8765"
DEFAULT_VAE_CHECKPOINT = Path("test/cvae_db2_best.pt")
VAE_LATENT_DIM = 64
VAE_CONDITION_DIM = 16
N_CHANNELS = 12
N_TIMESTEPS = 400

# --- 1. Define Label Mapping (ID to String) ---
ID_TO_GESTURE = {
    0: "rest",
    # Exercise B 
    1: "b1_thumb_up", 2: "b2_index_middle_ext", 3: "b3_ring_little_flex", 4: "b4_thumb_opp_little",
    5: "b5_all_abduction", 6: "b6_fist", 7: "b7_pointing", 8: "b8_adduction_extended",
    9: "b9_wrist_sup_mid", 10: "b10_wrist_pro_mid", 11: "b11_wrist_sup_little", 12: "b12_wrist_pro_little",
    13: "b13_wrist_flexion", 14: "b14_wrist_extension", 15: "b15_wrist_radial", 16: "b16_wrist_ulnar",
    17: "b17_wrist_ext_closed",
    # Exercise C 
    18: "c1_large_diameter", 19: "c2_small_diameter", 20: "c3_fixed_hook", 21: "c4_index_ext_grasp",
    22: "c5_medium_wrap", 23: "c6_ring_grasp", 24: "c7_prismatic_four", 25: "c8_stick_grasp",
    26: "c9_writing_tripod", 27: "c10_power_sphere", 28: "c11_three_finger_sphere", 29: "c12_precision_sphere",
    30: "c13_tripod", 31: "c14_prismatic_pinch", 32: "c15_tip_pinch", 33: "c16_quadpod",
    34: "c17_lateral", 35: "c18_parallel_ext", 36: "c19_extension_type", 37: "c20_power_disk",
    38: "c21_bottle_tripod", 39: "c22_screw_stick", 40: "c23_cut_knife",
    # Exercise D 
    41: "d1_little_flex", 42: "d2_ring_flex", 43: "d3_middle_flex", 44: "d4_index_flex",
    45: "d5_thumb_abd", 46: "d6_thumb_flex", 47: "d7_index_little_flex", 48: "d8_ring_middle_flex",
    49: "d9_index_thumb_flex",
}

# --- 2. Input Schema ---
class SignalInput(BaseModel):
    signal: List[List[float]] = Field(..., description="A 2D array representing EMG data [12 channels, 400 timesteps]")


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
    seed: int | None = None


class VAEGenerateAndFineTuneRequest(VAEGenerateRequest):
    finetune_epochs: int = Field(default=3, ge=1, le=50)
    finetune_batch_size: int = Field(default=32, ge=1, le=256)
    finetune_learning_rate: float = Field(default=1e-4, gt=0.0, le=1.0)
    checkpoint_out: str | None = None


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


class VAEEngine:
    def __init__(self, checkpoint_path: Path):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = NotebookStyleConditionalVAE().to(self.device)
        self.checkpoint_path = checkpoint_path
        self.loaded = False
        self.load_error: str | None = None

        if checkpoint_path.exists():
            try:
                state = torch.load(checkpoint_path, map_location=self.device)
                if isinstance(state, dict) and "state_dict" in state:
                    state = state["state_dict"]
                if isinstance(state, dict):
                    self.model.load_state_dict(state, strict=False)
                    self.loaded = True
            except Exception as exc:
                self.load_error = str(exc)
        self.model.eval()

    @staticmethod
    def _build_condition(subject_idx: int, gesture: int, flags: GenerationFlags) -> np.ndarray:
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

    def generate(self, body: VAEGenerateRequest) -> list[np.ndarray]:
        if body.seed is not None:
            torch.manual_seed(body.seed)
            np.random.seed(body.seed)

        cond = self._build_condition(body.subject_idx_0based, body.gesture_0based, body.flags)
        cond_t = torch.tensor(cond, dtype=torch.float32, device=self.device).unsqueeze(0).repeat(body.n_samples, 1)
        z = torch.randn(body.n_samples, self.model.latent_dim, device=self.device)

        with torch.no_grad():
            out = self.model.decode(z, cond_t).cpu().numpy()
        return [out[i] for i in range(out.shape[0])]


vae_engine = VAEEngine(DEFAULT_VAE_CHECKPOINT)

# --- 3. WebSocket Sender ---
async def send_to_websocket(gesture_name: str):
    try:
        async with websockets.connect(WS_SERVER_URL, ping_interval=None) as ws:
            # Using your example format with hardcoded confidence: 1.0
            msg = {"gesture": gesture_name, "confidence": 1.0}
            await ws.send(json.dumps(msg))
            
            raw = await ws.recv()
            resp = json.loads(raw)
            status = resp.get("status", "?")
            
            if status != "ok":
                print(f" !! Server error: {resp}")
            return status
            
    except ConnectionRefusedError:
        print(f" !! WebSocket connection refused at {WS_SERVER_URL}")
        return "connection_refused"
    except Exception as e:
        print(f" !! WebSocket error: {e}")
        return f"error: {str(e)}"

# --- 4. Main Endpoint ---
@app.post("/forward_signal")
async def process_and_forward(data: SignalInput):
    # Step 1: Call your original, untouched AI service
    try:
        async with httpx.AsyncClient() as client:
            # We send the exact JSON structure your AI service expects
            response = await client.post(AI_SERVICE_URL, json=data.model_dump(), timeout=10.0)
            
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, 
                detail=f"AI Service failed: {response.text}"
            )
            
        # Extract the integer from your AI service's original output format
        ai_result = response.json()
        predicted_class_id = ai_result.get("predicted_class")
        
        if predicted_class_id is None:
            raise HTTPException(status_code=500, detail="AI Service did not return 'predicted_class'")
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Could not reach AI Service at {AI_SERVICE_URL}. Is it running?")

    # Step 2: Map the integer to the exact string name
    gesture_name = ID_TO_GESTURE.get(predicted_class_id, "unknown_gesture")

    # Step 3: Send the string to the WebSocket server
    ws_status = await send_to_websocket(gesture_name)

    # Step 4: Return a summary to whoever triggered this pipeline
    return {
        "status": "success",
        "pipeline_result": {
            "ai_predicted_id": predicted_class_id,
            "mapped_gesture": gesture_name,
            "websocket_delivery": ws_status
        }
    }


# --- 5. NEW: SCENARIO PLAYBACK ENDPOINT ---
@app.post("/scenario/{scenario_id}")
async def run_scenario(scenario_id: int):
    """
    Reads a stacked EMG file for a given scenario, chunks it into 400-timestep movements,
    sends each to the AI service, and broadcasts the result via WebSocket.
    
    Expected file format: Numpy array (.npy) of shape (12 channels, N * 400 timesteps)
    Location: A 'data' directory in the same folder as this script, e.g., 'data/scenario_1.npy'.
    """
    file_path = Path(f"data/scenario_{scenario_id}.npy")
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Scenario file not found at {file_path}")

    try:
        # Load data. Expected shape: (12, total_timesteps)
        data = np.load(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load numpy file: {str(e)}")

    if len(data.shape) != 2 or data.shape[0] != N_CHANNELS:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid data shape {data.shape}. Expected ({N_CHANNELS}, N*400)"
        )

    total_timesteps = data.shape[1]
    chunk_size = N_TIMESTEPS
    n_chunks = total_timesteps // chunk_size
    results = []

    # --- DIAGNOSTIC: SCENARIO LOAD ---
    print(f"\n[SCENARIO {scenario_id}] ══════════════════════════════════════════")
    print(f"[SCENARIO {scenario_id}]   File        : {file_path}")
    print(f"[SCENARIO {scenario_id}]   Loaded shape: {data.shape}  (channels x total_timesteps)")
    print(f"[SCENARIO {scenario_id}]   Chunk size  : {chunk_size} timesteps")
    print(f"[SCENARIO {scenario_id}]   Num chunks  : {n_chunks}  (= {total_timesteps} // {chunk_size})")
    print(f"[SCENARIO {scenario_id}]   Value range : min={data.min():.4f}  max={data.max():.4f}")
    print(f"[SCENARIO {scenario_id}] ══════════════════════════════════════════")

    # Iterate through the stacked array in chunks of 400 timesteps
    for i in range(0, total_timesteps, chunk_size):
        chunk = data[:, i:i+chunk_size]
        chunk_idx = i // chunk_size
        
        # Skip trailing incomplete chunks
        if chunk.shape[1] < chunk_size:
            print(f"[SCENARIO {scenario_id}]   Chunk {chunk_idx}: SKIPPED (only {chunk.shape[1]} timesteps, need {chunk_size})")
            break

        signal_list = chunk.tolist()

        # --- DIAGNOSTIC: CHUNK SENT TO AI ---
        print(f"\n[SCENARIO {scenario_id}] ── Chunk {chunk_idx} / {n_chunks - 1} ────────────────────────────")
        print(f"[SCENARIO {scenario_id}]   Chunk shape    : {chunk.shape}  → sending as list [{len(signal_list)}, {len(signal_list[0])}]")
        print(f"[SCENARIO {scenario_id}]   Value range    : min={chunk.min():.4f}  max={chunk.max():.4f}")
        print(f"[SCENARIO {scenario_id}]   Sending to AI  : POST {AI_SERVICE_URL}")

        try:
            async with httpx.AsyncClient() as client:
                ai_payload = {"signal": signal_list}
                response = await client.post(AI_SERVICE_URL, json=ai_payload, timeout=10.0)
                
                if response.status_code == 200:
                    ai_result = response.json()

                    # --- DIAGNOSTIC: AI RESPONSE ---
                    print(f"[SCENARIO {scenario_id}]   AI HTTP status : {response.status_code} OK")
                    print(f"[SCENARIO {scenario_id}]   AI raw response: {ai_result}")

                    predicted_class_id = ai_result.get("predicted_class")
                    ai_confidence      = ai_result.get("confidence", "N/A")
                    
                    if predicted_class_id is not None:
                        # --- DIAGNOSTIC: MAPPING ---
                        gesture_name = ID_TO_GESTURE.get(predicted_class_id, "unknown_gesture")
                        in_map       = predicted_class_id in ID_TO_GESTURE
                        print(f"[SCENARIO {scenario_id}]   Predicted ID   : {predicted_class_id}  |  Confidence: {ai_confidence}")
                        print(f"[SCENARIO {scenario_id}]   ID in map?     : {'✅ YES' if in_map else '❌ NO (ID_TO_GESTURE has keys 0-' + str(max(ID_TO_GESTURE.keys())) + ')'}")
                        print(f"[SCENARIO {scenario_id}]   Mapped gesture : '{gesture_name}'")

                        ws_status = await send_to_websocket(gesture_name)
                        print(f"[SCENARIO {scenario_id}]   WebSocket      : {ws_status}")
                        
                        results.append({
                            "chunk_index": chunk_idx,
                            "predicted_id": predicted_class_id,
                            "confidence": ai_confidence,
                            "gesture": gesture_name,
                            "ws_status": ws_status
                        })
                    else:
                        print(f"[SCENARIO {scenario_id}]   ❌ AI returned no 'predicted_class' key! Response: {ai_result}")
                        results.append({"chunk_index": chunk_idx, "error": "AI returned no class ID"})
                else:
                    print(f"[SCENARIO {scenario_id}]   ❌ AI HTTP error: {response.status_code}  body={response.text[:200]}")
                    results.append({"chunk_index": chunk_idx, "error": f"AI service HTTP {response.status_code}"})
                    
        except Exception as e:
            print(f"[SCENARIO {scenario_id}]   ❌ Exception in chunk {chunk_idx}: {e}")
            results.append({"chunk_index": chunk_idx, "error": str(e)})

        # Wait 1 second before processing the next movement to simulate real-time playback
        await asyncio.sleep(1.0)

    # --- DIAGNOSTIC: FINAL SUMMARY ---
    ok_count  = sum(1 for r in results if "error" not in r)
    err_count = sum(1 for r in results if "error" in r)
    print(f"\n[SCENARIO {scenario_id}] ══ Summary ══════════════════════════════════")
    print(f"[SCENARIO {scenario_id}]   Chunks processed: {len(results)} / {n_chunks}")
    print(f"[SCENARIO {scenario_id}]   ✅ Successful    : {ok_count}")
    print(f"[SCENARIO {scenario_id}]   ❌ Errors        : {err_count}")
    for r in results:
        if "error" not in r:
            print(f"[SCENARIO {scenario_id}]     Chunk {r['chunk_index']}: ID={r['predicted_id']}  conf={r.get('confidence','?')}  gesture='{r['gesture']}'")
        else:
            print(f"[SCENARIO {scenario_id}]     Chunk {r['chunk_index']}: ERROR → {r['error']}")
    print(f"[SCENARIO {scenario_id}] ══════════════════════════════════════════════")

    return {
        "status": "success",
        "scenario_id": scenario_id,
        "movements_processed": len(results),
        "results": results
    }

# --- OTHER ENDPOINTS ---

@app.get("/vae/health")
async def vae_health() -> dict[str, Any]:
    return {
        "status": "ok",
        "checkpoint": str(vae_engine.checkpoint_path),
        "checkpoint_exists": vae_engine.checkpoint_path.exists(),
        "checkpoint_loaded": vae_engine.loaded,
        "load_error": vae_engine.load_error,
        "device": str(vae_engine.device),
    }


@app.post("/vae/generate")
async def vae_generate(body: VAEGenerateRequest):
    try:
        generated = vae_engine.generate(body)
        payload = [arr.astype(np.float32).tolist() for arr in generated]
        return {
            "status": "success",
            "shape": [N_CHANNELS, N_TIMESTEPS],
            "gesture_label": body.gesture_0based,
            "n_samples": len(payload),
            "samples": payload,
            "model_loaded": vae_engine.loaded,
            "model_load_error": vae_engine.load_error,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/vae/generate_and_finetune")
async def vae_generate_and_finetune(body: VAEGenerateAndFineTuneRequest):
    try:
        generated = vae_engine.generate(body)
        finetune_samples = [{"signal": arr.astype(np.float32).tolist(), "label": body.gesture_0based} for arr in generated]
        finetune_payload = {
            "samples": finetune_samples,
            "epochs": body.finetune_epochs,
            "batch_size": body.finetune_batch_size,
            "learning_rate": body.finetune_learning_rate,
            "checkpoint_out": body.checkpoint_out,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(CLASSIFIER_FINETUNE_URL, json=finetune_payload, timeout=120.0)

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Classifier fine-tune failed: {response.text}",
            )

        return {
            "status": "success",
            "generation": {
                "n_samples": len(generated),
                "shape": [N_CHANNELS, N_TIMESTEPS],
                "gesture_label": body.gesture_0based,
                "model_loaded": vae_engine.loaded,
                "model_load_error": vae_engine.load_error,
            },
            "finetune": response.json(),
        }
    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail=f"Could not reach classifier fine-tune endpoint at {CLASSIFIER_FINETUNE_URL}. Is classification_service running?",
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

if __name__ == "__main__":
    # Run this integration service on port 8001 so it doesn't clash with your AI service
    uvicorn.run("integration_service:app", host="0.0.0.0", port=8001, reload=True)