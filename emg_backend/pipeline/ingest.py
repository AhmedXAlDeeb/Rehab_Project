from __future__ import annotations

from datetime import datetime, timezone

import numpy as np
from fastapi import HTTPException

from schemas import DriftEvent, EMGFrame, SessionMeta
from storage.filesystem import FileStore
from storage.session_stats import WelfordStats


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def handle_ingest(frame: EMGFrame, store: FileStore, welford: WelfordStats):
    if not frame.channels or len(frame.channels[0]) != 14:
        raise HTTPException(status_code=422, detail="channels must be shape (N,14)")
    if frame.sample_rate != 2000:
        raise HTTPException(status_code=422, detail="sample_rate must be 2000")

    arr = np.asarray(frame.channels, dtype=np.float32)
    if arr.ndim != 2 or arr.shape[1] != 14:
        raise HTTPException(status_code=422, detail="invalid EMG frame shape")

    zeros_ratio = (arr == 0).sum(axis=0) / max(arr.shape[0], 1)
    if np.any(zeros_ratio > 0.8):
        drift = DriftEvent(
            patient_id=frame.patient_id,
            session_id=frame.session_id,
            timestamp_ms=frame.timestamp_ms,
            drift_type="electrode_disconnect",
            drift_score=float(zeros_ratio.max()),
            severity="critical",
        )
        store.save_drift_event(drift)
        raise HTTPException(status_code=422, detail="electrode disconnection detected")

    meta = store.load_session_meta(frame.patient_id, frame.session_id)
    if meta is None:
        meta = SessionMeta(
            session_id=frame.session_id,
            patient_id=frame.patient_id,
            day_index=0,
            time_index=0,
            started_at=_now_iso(),
        )
        store.save_session_meta(meta)

    await welford.update(arr)
    raw_path = store.save_raw_frame(frame.patient_id, frame.session_id, frame.timestamp_ms, arr)

    store.update_session_meta(frame.patient_id, frame.session_id, n_frames=meta.n_frames + 1)
    return raw_path
