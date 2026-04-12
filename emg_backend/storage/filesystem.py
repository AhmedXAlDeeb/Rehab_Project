from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import torch

from config import settings
from schemas import (
    ClassificationResult,
    DriftEvent,
    FailureCase,
    FineTuneRecord,
    PatientProfile,
    SessionMeta,
    SessionStats,
)


class FileStore:
    def _atomic_write_text(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(text, encoding="utf-8")
        tmp.replace(path)

    def _atomic_write_npy(self, path: Path, data: np.ndarray) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        with tmp.open("wb") as f:
            np.save(f, data, allow_pickle=False)
        tmp.replace(path)

    def _load_json_model(self, path: Path, model_cls: Any):
        if not path.exists():
            return None
        return model_cls.model_validate_json(path.read_text(encoding="utf-8"))

    def patient_dir(self, patient_id: str) -> Path:
        p = settings.DATA_ROOT / "patients" / patient_id
        p.mkdir(parents=True, exist_ok=True)
        return p

    def save_profile(self, profile: PatientProfile) -> None:
        path = self.patient_dir(profile.patient_id) / "profile.json"
        self._atomic_write_text(path, profile.model_dump_json(indent=2))

    def load_profile(self, patient_id: str) -> PatientProfile | None:
        return self._load_json_model(self.patient_dir(patient_id) / "profile.json", PatientProfile)

    def patient_exists(self, patient_id: str) -> bool:
        return (settings.DATA_ROOT / "patients" / patient_id / "profile.json").exists()

    def list_patients(self) -> list[str]:
        root = settings.DATA_ROOT / "patients"
        if not root.exists():
            return []
        return sorted([p.name for p in root.iterdir() if p.is_dir()])

    def session_dir(self, patient_id: str, session_id: str) -> Path:
        p = self.patient_dir(patient_id) / "sessions" / session_id
        p.mkdir(parents=True, exist_ok=True)
        for sub in ["raw", "segments", "features", "spectrograms", "classifications", "drift", "drift_state"]:
            (p / sub).mkdir(parents=True, exist_ok=True)
        return p

    def save_session_meta(self, meta: SessionMeta) -> None:
        path = self.session_dir(meta.patient_id, meta.session_id) / "meta.json"
        self._atomic_write_text(path, meta.model_dump_json(indent=2))

    def load_session_meta(self, patient_id: str, session_id: str) -> SessionMeta | None:
        path = self.session_dir(patient_id, session_id) / "meta.json"
        return self._load_json_model(path, SessionMeta)

    def update_session_meta(self, patient_id: str, session_id: str, **kwargs) -> None:
        meta = self.load_session_meta(patient_id, session_id)
        if meta is None:
            return
        updated = meta.model_copy(update=kwargs)
        self.save_session_meta(updated)

    def save_session_stats(self, stats: SessionStats) -> None:
        path = self.session_dir(stats.patient_id, stats.session_id) / "stats.json"
        self._atomic_write_text(path, stats.model_dump_json(indent=2))

    def load_session_stats(self, patient_id: str, session_id: str) -> SessionStats | None:
        path = self.session_dir(patient_id, session_id) / "stats.json"
        return self._load_json_model(path, SessionStats)

    def save_raw_frame(self, patient_id: str, session_id: str, timestamp_ms: int, data: np.ndarray) -> Path:
        path = self.session_dir(patient_id, session_id) / "raw" / f"{timestamp_ms}.npy"
        self._atomic_write_npy(path, data)
        return path

    def save_segment(self, patient_id: str, session_id: str, timestamp_ms: int, data: np.ndarray) -> Path:
        path = self.session_dir(patient_id, session_id) / "segments" / f"{timestamp_ms}.npy"
        self._atomic_write_npy(path, data)
        return path

    def save_features(self, patient_id: str, session_id: str, timestamp_ms: int, data: np.ndarray) -> Path:
        path = self.session_dir(patient_id, session_id) / "features" / f"{timestamp_ms}.npy"
        self._atomic_write_npy(path, data)
        return path

    def save_spectrogram(self, patient_id: str, session_id: str, timestamp_ms: int, data: np.ndarray) -> Path:
        path = self.session_dir(patient_id, session_id) / "spectrograms" / f"{timestamp_ms}.npy"
        self._atomic_write_npy(path, data)
        return path

    def load_npy(self, path: Path | str) -> np.ndarray | None:
        p = Path(path)
        if not p.is_absolute():
            p = settings.DATA_ROOT / p
        if not p.exists():
            return None
        with p.open("rb") as f:
            return np.load(f, allow_pickle=False)

    def list_features(self, patient_id: str, session_id: str) -> list[Path]:
        p = self.session_dir(patient_id, session_id) / "features"
        return sorted(p.glob("*.npy"), key=lambda x: x.name)

    def save_classification(self, result: ClassificationResult) -> Path:
        path = self.session_dir(result.patient_id, result.session_id) / "classifications" / f"{result.timestamp_ms}.json"
        self._atomic_write_text(path, result.model_dump_json(indent=2))
        return path

    def load_all_classifications(self, patient_id: str, session_id: str) -> list[ClassificationResult]:
        p = self.session_dir(patient_id, session_id) / "classifications"
        out: list[ClassificationResult] = []
        for file in sorted(p.glob("*.json")):
            if file.name.endswith("_gt.json"):
                continue
            item = self._load_json_model(file, ClassificationResult)
            if item is not None:
                out.append(item)
        return out

    def save_drift_event(self, event: DriftEvent) -> Path:
        path = self.session_dir(event.patient_id, event.session_id) / "drift" / f"{event.timestamp_ms}.json"
        self._atomic_write_text(path, event.model_dump_json(indent=2))
        return path

    def load_drift_events(self, patient_id: str, session_id: str) -> list[DriftEvent]:
        p = self.session_dir(patient_id, session_id) / "drift"
        out: list[DriftEvent] = []
        for file in sorted(p.glob("*.json")):
            item = self._load_json_model(file, DriftEvent)
            if item is not None:
                out.append(item)
        return out

    def save_failure_case(self, case: FailureCase) -> Path:
        p = self.patient_dir(case.patient_id) / "failures"
        p.mkdir(parents=True, exist_ok=True)
        path = p / f"{case.timestamp_ms}.json"
        self._atomic_write_text(path, case.model_dump_json(indent=2))
        return path

    def load_all_failures(self, patient_id: str, unused_only: bool = True) -> list[FailureCase]:
        p = self.patient_dir(patient_id) / "failures"
        if not p.exists():
            return []
        out: list[FailureCase] = []
        for file in sorted(p.glob("*.json")):
            item = self._load_json_model(file, FailureCase)
            if item is None:
                continue
            if unused_only and item.used_in_finetune:
                continue
            out.append(item)
        return out

    def mark_failures_used(self, patient_id: str, failure_paths: list[Path]) -> None:
        for fp in failure_paths:
            item = self._load_json_model(fp, FailureCase)
            if item is None:
                continue
            updated = item.model_copy(update={"used_in_finetune": True})
            self._atomic_write_text(fp, updated.model_dump_json(indent=2))

    def count_unused_failures(self, patient_id: str) -> int:
        return len(self.load_all_failures(patient_id, unused_only=True))

    def model_dir(self, patient_id: str) -> Path:
        p = self.patient_dir(patient_id) / "model"
        (p / "history").mkdir(parents=True, exist_ok=True)
        return p

    def save_model_checkpoint(self, patient_id: str, version: str, state_dict: dict) -> Path:
        p = self.model_dir(patient_id)
        history_path = p / "history" / f"{version}.pt"
        current = p / "current.pt"
        torch.save(state_dict, history_path)
        torch.save(state_dict, current)
        self._atomic_write_text(p / "current_version.txt", version)
        return current

    def load_model_checkpoint(self, patient_id: str) -> tuple[dict | None, str]:
        p = self.model_dir(patient_id)
        current = p / "current.pt"
        version = self.get_model_version(patient_id)
        if not current.exists():
            return None, version
        return torch.load(current, map_location="cpu"), version

    def get_model_version(self, patient_id: str) -> str:
        p = self.model_dir(patient_id) / "current_version.txt"
        if not p.exists():
            return "base"
        return p.read_text(encoding="utf-8").strip() or "base"

    def save_finetune_record(self, record: FineTuneRecord) -> Path:
        p = self.patient_dir(record.patient_id) / "finetune_log"
        p.mkdir(parents=True, exist_ok=True)
        path = p / f"{record.timestamp_ms}.json"
        self._atomic_write_text(path, record.model_dump_json(indent=2))
        return path

    def load_finetune_history(self, patient_id: str) -> list[FineTuneRecord]:
        p = self.patient_dir(patient_id) / "finetune_log"
        if not p.exists():
            return []
        out: list[FineTuneRecord] = []
        for file in sorted(p.glob("*.json"), reverse=True):
            item = self._load_json_model(file, FineTuneRecord)
            if item is not None:
                out.append(item)
        return out

    def synthetic_job_dir(self, patient_id: str, job_id: str) -> Path:
        p = self.patient_dir(patient_id) / "synthetic" / job_id
        (p / "samples").mkdir(parents=True, exist_ok=True)
        return p

    def save_synthetic_sample(self, patient_id: str, job_id: str, idx: int, signal: np.ndarray) -> Path:
        p = self.synthetic_job_dir(patient_id, job_id) / "samples" / f"{idx}.npy"
        self._atomic_write_npy(p, signal)
        return p

    def load_synthetic_samples(self, patient_id: str, job_id: str) -> list[np.ndarray]:
        p = self.synthetic_job_dir(patient_id, job_id) / "samples"
        out: list[np.ndarray] = []
        for f in sorted(p.glob("*.npy"), key=lambda x: x.name):
            arr = self.load_npy(f)
            if arr is not None:
                out.append(arr)
        return out

    def save_json_dict(self, path: Path, payload: dict) -> None:
        self._atomic_write_text(path, json.dumps(payload, indent=2))

    def load_json_dict(self, path: Path) -> dict | None:
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return None
