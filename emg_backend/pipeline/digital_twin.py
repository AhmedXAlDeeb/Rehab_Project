from __future__ import annotations

import time
import uuid

import numpy as np

from config import settings
from engines.classifier_engine import ClassifierEngine
from engines.vae_engine import VAEEngine
from monitoring.metrics import metrics
from schemas import FailureCase
from storage.filesystem import FileStore


def _now_ms() -> int:
    return int(time.time() * 1000)


def _cells_for_drift(drift_type: str) -> list[dict]:
    gestures = list(range(settings.N_GESTURES))
    cells: list[dict] = []
    if drift_type == "confidence":
        fatigue_levels = [0.7, 0.9]
        eq_levels = [1.0]
    elif drift_type == "spectral":
        fatigue_levels = [0.0]
        eq_levels = [0.4, 0.7]
    else:
        fatigue_levels = settings.FATIGUE_LEVELS
        eq_levels = settings.ELECTRODE_Q_LEVELS
    for g in gestures:
        for f in fatigue_levels:
            for eq in eq_levels:
                cells.append({"gesture": g, "flags": {"fatigue": f, "electrode_quality": eq, "session_idx_norm": 0.5, "amputation": 0.0}})
    return cells


async def run_stress_test(patient_id: str, store: FileStore, vae_engine: VAEEngine, classifier_engine: ClassifierEngine) -> dict:
    job_id = str(uuid.uuid4())
    return await _run_job(job_id, patient_id, "embedding", store, vae_engine, classifier_engine)


async def _run_job(job_id: str, patient_id: str, drift_type: str, store: FileStore, vae_engine: VAEEngine, classifier_engine: ClassifierEngine) -> dict:
    job_dir = store.synthetic_job_dir(patient_id, job_id)
    meta_path = job_dir / "meta.json"
    store.save_json_dict(meta_path, {"job_id": job_id, "status": "running", "created_at": _now_ms()})

    failure_map: dict = {}
    idx = 0
    for cell in _cells_for_drift(drift_type):
        gesture = cell["gesture"]
        flags = cell["flags"]
        cond_key = f"fatigue_{flags['fatigue']}_eq_{flags['electrode_quality']}"
        outputs = vae_engine.generate(patient_id, patient_idx=0, gesture=gesture, condition_flags=flags, n_samples=settings.N_SYNTHETIC_PER_CELL)
        failures = 0
        for signal in outputs:
            idx += 1
            store.save_synthetic_sample(patient_id, job_id, idx, signal)
            feat = np.concatenate([
                np.sqrt(np.mean(signal**2, axis=0)),
                np.mean(np.abs(signal), axis=0),
                np.sum(np.abs(np.diff(signal, axis=0)), axis=0),
                np.sum(np.diff(np.signbit(signal), axis=0).astype(np.float32), axis=0),
                np.sum(np.abs(signal), axis=0),
                np.median(np.abs(np.fft.rfft(signal, axis=0)), axis=0),
            ]).astype(np.float32)
            pred, conf, _ = await classifier_engine.predict(feat)
            metrics.inc("synthetic_samples_generated")
            if conf < 0.5 or pred != gesture:
                failures += 1
                spec = np.resize(np.abs(np.fft.rfft(signal, axis=0)).T, (settings.N_CHANNELS, 128, 50))
                spec_path = store.synthetic_job_dir(patient_id, job_id) / "samples" / f"{idx}_spec.npy"
                store._atomic_write_npy(spec_path, spec)
                case = FailureCase(
                    patient_id=patient_id,
                    session_id=None,
                    timestamp_ms=_now_ms(),
                    gesture_true=gesture,
                    gesture_predicted=pred,
                    confidence=conf,
                    condition_flags=flags,
                    spectrogram_path=str(spec_path.relative_to(settings.DATA_ROOT)),
                    source="synthetic",
                )
                store.save_failure_case(case)
                metrics.inc("failures_stored")
        rate = failures / max(len(outputs), 1)
        failure_map.setdefault(str(gesture), {})[cond_key] = rate

    store.save_json_dict(meta_path, {"job_id": job_id, "status": "completed", "failure_map": failure_map, "completed_at": _now_ms()})

    return failure_map


async def run_twin_job(
    patient_id: str,
    drift_type: str,
    store: FileStore,
    vae_engine: VAEEngine,
    classifier_engine: ClassifierEngine,
    job_id: str | None = None,
) -> tuple[str, dict]:
    if drift_type == "electrode_disconnect":
        return ("skipped", {})
    resolved_job_id = job_id or str(uuid.uuid4())
    failure_map = await _run_job(resolved_job_id, patient_id, drift_type, store, vae_engine, classifier_engine)
    return resolved_job_id, failure_map
