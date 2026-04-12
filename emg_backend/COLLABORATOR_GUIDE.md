# EMG Backend Collaborator Guide

This guide explains the backend structure, what each part does, and how to add new code safely.

## 1) What This Backend Is

This backend is a prototype-focused FastAPI service for:
- Receiving EMG frames.
- Preprocessing and classifying each frame.
- Running drift checks.
- Storing all artifacts on disk.
- Running digital twin stress tests.

Important design decision:
- The backend uses direct function calls in request flow (not event-driven architecture).
- There is no auth/token layer in this prototype version.

## 2) Quick Start

From project root:

```powershell
.venv\Scripts\activate
Set-Location emg_backend
pip install -r requirements.txt
```

Run API:

```powershell
uvicorn main:app --reload
```

Run tests:

```powershell
python -m pytest -q
```

## 3) Runtime Flow (High-Level)

Main ingest flow for `POST /v1/ingest/emg`:
1. Validate patient/session/frame inputs.
2. Save raw EMG and update running session stats.
3. Preprocess to segment/features/spectrogram.
4. Classify features using patient-specific classifier engine.
5. Run drift detection from confidence + signal features.
6. Persist outputs in file storage.

Everything above happens in one request path.

## 4) Folder and File Map

## Core app
- `main.py`
- FastAPI app bootstrap, shared app state, router registration.
- Creates and stores singleton services in `app.state`.

- `config.py`
- Global settings (paths, EMG params, drift thresholds, finetune params).

- `schemas.py`
- Pydantic request/response/persistence models.

## API layer
- `routers/ingest.py`
- `POST /v1/ingest/emg` and `POST /v1/ingest/feedback`.
- Orchestrates ingest -> preprocess -> classify -> drift.

- `routers/patient.py`
- Patient registration and profile/session/history endpoints.

- `routers/classify.py`
- Read-only classification accuracy/latest endpoints.

- `routers/twin.py`
- Digital twin generation/stress-test endpoints.

- `routers/health.py`
- Health and metrics endpoints.

## Processing pipeline
- `pipeline/ingest.py`
- Input checks, raw frame persistence, session bootstrap.

- `pipeline/preprocess.py`
- Filtering, normalization, handcrafted feature extraction, spectrogram generation.

- `pipeline/classify.py`
- Inference and classification persistence.

- `pipeline/drift.py`
- ADWIN-like confidence drift + CUSUM spectral + simple embedding drift checks.

- `pipeline/digital_twin.py`
- Synthetic sample generation and stress-test scoring.

- `pipeline/finetuner.py`
- Periodic/adaptive finetuning based on failure data.

## Engines and models
- `engines/classifier_engine.py`
- Model loading/reload and inference helpers.

- `engines/vae_engine.py`
- CVAE synthetic generation wrapper.

- `ml_models/classifier.py`
- Classifier network definition.

- `ml_models/cvae.py`
- CVAE model definition.

## Storage and metrics
- `storage/filesystem.py`
- File-based persistence API for profiles, sessions, artifacts, models, logs.

- `storage/session_stats.py`
- Welford running stats per (patient, session).

- `monitoring/metrics.py`
- In-memory counters/gauges in Prometheus text format.

## Tests
- `tests/test_preprocess.py`
- `tests/test_detectors.py`
- `tests/test_filesystem.py`
- `tests/test_schemas.py`

## 5) API Endpoints Summary

## Ingest
- `POST /v1/ingest/emg`
- Body: `EMGFrame`.
- Performs full direct pipeline and returns status + drift count.

- `POST /v1/ingest/feedback?patient_id=...`
- Body: `FeedbackBody`.
- Saves ground truth and failure cases.

## Patient
- `POST /v1/patient/register`
- `GET /v1/patient/{patient_id}`
- `GET /v1/patient/{patient_id}/sessions`
- `GET /v1/patient/{patient_id}/sessions/{session_id}`
- `GET /v1/patient/{patient_id}/finetune_history`

## Classification
- `GET /v1/classify/{patient_id}/latest`
- `GET /v1/classify/{patient_id}/accuracy`

## Twin
- `POST /v1/twin/generate`
- `GET /v1/twin/job/{job_id}?patient_id=...`
- `GET /v1/twin/stress_test/{patient_id}`
- `POST /v1/twin/stress_test/{patient_id}`

## Health
- `GET /health`
- `GET /metrics`

## 6) Data Layout Under `data/`

Main tree:
- `data/patients/{patient_id}/profile.json`
- `data/patients/{patient_id}/sessions/{session_id}/raw/*.npy`
- `data/patients/{patient_id}/sessions/{session_id}/segments/*.npy`
- `data/patients/{patient_id}/sessions/{session_id}/features/*.npy`
- `data/patients/{patient_id}/sessions/{session_id}/spectrograms/*.npy`
- `data/patients/{patient_id}/sessions/{session_id}/classifications/*.json`
- `data/patients/{patient_id}/sessions/{session_id}/drift/*.json`
- `data/patients/{patient_id}/failures/*.json`
- `data/patients/{patient_id}/model/current.pt`
- `data/patients/{patient_id}/model/history/*.pt`
- `data/patients/{patient_id}/finetune_log/*.json`
- `data/patients/{patient_id}/synthetic/{job_id}/...`

## 7) How To Add New Code

## Add a new endpoint
1. Create or update file in `routers/`.
2. Keep route layer thin: validate request, call pipeline/service functions.
3. Register router in `main.py`.
4. Add tests under `tests/`.

## Add a new processing step in ingest flow
1. Implement function in `pipeline/` with explicit inputs/outputs.
2. Call it from `routers/ingest.py` in the direct sequence.
3. Persist outputs through `FileStore` methods.
4. Add/adjust schema models only if payload contract changes.

## Add new stored artifact type
1. Add save/load methods in `storage/filesystem.py`.
2. Keep naming deterministic (`{timestamp}.json`, `{timestamp}.npy`).
3. Prefer atomic writes (`_atomic_write_text`, `_atomic_write_npy`).

## Add model logic
1. Put model architecture in `ml_models/`.
2. Add runtime wrapper/loading logic in `engines/`.
3. Keep route/pipeline code unaware of low-level tensor details.

## 8) Coding Conventions Used Here

- Use type hints for public functions.
- Keep routers focused on request orchestration.
- Keep math/signal/model logic in pipeline/engines.
- Raise `HTTPException` for invalid client input.
- Avoid side effects outside `FileStore` for persistence.
- Keep file names and data folder layout stable for compatibility.

## 9) Common Pitfalls

- Mismatch in EMG channel shape (must be Nx14).
- Wrong sample rate (must match config defaults).
- Returning absolute paths where relative paths are expected by loaders.
- Saving non-atomic files can produce partial reads.
- Forgetting to patch `settings.DATA_ROOT` in tests using temp dirs.

## 10) Suggested Collaboration Workflow

1. Create a feature branch per component (`router`, `pipeline`, or `storage`).
2. Add or update tests first for changed behavior.
3. Run `python -m pytest -q` before opening PR.
4. In PR description, include:
- Changed endpoints (if any).
- Changed schemas (if any).
- Changed persisted file paths (if any).
- Migration/backward-compatibility notes.

## 11) Ownership Suggestions (Optional)

- API and contracts: `routers/` + `schemas.py`
- Signal processing: `pipeline/preprocess.py`
- ML inference and training: `engines/`, `ml_models/`, `pipeline/finetuner.py`
- Persistence and data layout: `storage/filesystem.py`
- QA and stability: `tests/`

If you keep this separation, collaborators can work in parallel with minimal merge conflicts.
