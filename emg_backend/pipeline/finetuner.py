from __future__ import annotations

import time
from collections import Counter

import numpy as np
import torch
from torch import nn
from torch.optim import AdamW

from config import Settings, settings
from engines.classifier_engine import ClassifierEngine
from ml_models.classifier import ClassifierCNN
from monitoring.metrics import metrics
from schemas import FineTuneRecord
from storage.filesystem import FileStore


def _now_ms() -> int:
    return int(time.time() * 1000)


def _parse_version(version: str) -> tuple[int, int]:
    if not version.startswith("v"):
        return 1, 0
    try:
        major, minor = version[1:].split(".")
        return int(major), int(minor)
    except Exception:
        return 1, 0


def _next_version(version: str) -> str:
    major, minor = _parse_version(version)
    return f"v{major}.{minor + 1}"


def _train_epoch(model: ClassifierCNN, x: torch.Tensor, y: torch.Tensor, opt: AdamW) -> float:
    model.train()
    logits = model(x)
    loss = nn.CrossEntropyLoss()(logits, y)
    opt.zero_grad()
    loss.backward()
    opt.step()
    return float(loss.detach().cpu().item())


def _evaluate(model: ClassifierCNN, x: torch.Tensor, y: torch.Tensor) -> float:
    model.eval()
    with torch.no_grad():
        pred = torch.argmax(model(x), dim=1)
        return float((pred == y).float().mean().item())


def _finetune_sync(patient_id: str, store: FileStore, config: Settings, trigger: str = "manual") -> FineTuneRecord:
    t0 = time.time()
    failures = store.load_all_failures(patient_id, unused_only=True)
    failures = sorted(failures, key=lambda x: x.confidence)[:500]

    feature_list: list[np.ndarray] = []
    label_list: list[int] = []
    used_paths = []

    failure_dir = store.patient_dir(patient_id) / "failures"
    for f in failures:
        spec = store.load_npy(f.spectrogram_path)
        if spec is None:
            continue
        feat = np.concatenate([spec.mean(axis=(1, 2)), spec.std(axis=(1, 2)), spec.max(axis=(1, 2)), spec.min(axis=(1, 2)), np.median(spec, axis=(1, 2)), np.percentile(spec, 90, axis=(1, 2))]).astype(np.float32)
        feature_list.append(feat[:84])
        label_list.append(int(f.gesture_true))
        used_paths.append(failure_dir / f"{f.timestamp_ms}.json")

    sessions_root = store.patient_dir(patient_id) / "sessions"
    sessions = [s for s in sessions_root.iterdir() if s.is_dir()] if sessions_root.exists() else []
    sessions = sorted(sessions, key=lambda p: p.name, reverse=True)[:3]
    for sess in sessions:
        for fp in sorted((sess / "features").glob("*.npy")):
            arr = store.load_npy(fp)
            if arr is None:
                continue
            feature_list.append(arr.astype(np.float32).reshape(-1)[:84])
            label_list.append(0)

    if len(feature_list) < 10:
        before = store.get_model_version(patient_id)
        return FineTuneRecord(
            patient_id=patient_id,
            timestamp_ms=_now_ms(),
            trigger=trigger,
            model_version_before=before,
            model_version_after=before,
            accuracy_before=0.0,
            accuracy_after=0.0,
            n_failure_cases=len(failures),
            n_real_samples=0,
            duration_seconds=time.time() - t0,
        )

    x = torch.tensor(np.stack(feature_list, axis=0), dtype=torch.float32)
    y = torch.tensor(np.array(label_list, dtype=np.int64), dtype=torch.long)

    model = ClassifierCNN(in_dim=84, embedding_dim=128, n_classes=config.N_GESTURES)
    state, old_version = store.load_model_checkpoint(patient_id)
    if state is None and config.CLASSIFIER_PT.exists():
        state = torch.load(config.CLASSIFIER_PT, map_location="cpu")
    if isinstance(state, dict):
        if "state_dict" in state:
            state = state["state_dict"]
        model.load_state_dict(state, strict=False)

    acc_before = _evaluate(model, x, y)
    opt = AdamW([
        {"params": model.backbone.parameters(), "lr": config.FINETUNE_LR_BACKBONE},
        {"params": model.head.parameters(), "lr": config.FINETUNE_LR_HEAD},
    ])
    for _ in range(config.FINETUNE_EPOCHS):
        _train_epoch(model, x, y, opt)
    acc_after = _evaluate(model, x, y)

    new_version = old_version if acc_after < (acc_before - 0.05) else _next_version(old_version)
    if new_version != old_version:
        store.save_model_checkpoint(patient_id, new_version, model.state_dict())
    store.mark_failures_used(patient_id, used_paths)

    record = FineTuneRecord(
        patient_id=patient_id,
        timestamp_ms=_now_ms(),
        trigger=trigger,
        model_version_before=old_version,
        model_version_after=new_version,
        accuracy_before=acc_before,
        accuracy_after=acc_after,
        n_failure_cases=len(failures),
        n_real_samples=int((np.array(label_list) == 0).sum()),
        duration_seconds=time.time() - t0,
    )
    store.save_finetune_record(record)
    metrics.inc("finetune_jobs_total")
    return record


async def finetune_patient(patient_id: str, store: FileStore, classifier_engine: ClassifierEngine, trigger: str = "manual") -> None:
    loop = __import__("asyncio").get_running_loop()
    await loop.run_in_executor(None, _finetune_sync, patient_id, store, settings, trigger)
