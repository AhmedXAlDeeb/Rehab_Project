from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from config import settings
from monitoring.metrics import metrics
from schemas import DriftEvent
from storage.filesystem import FileStore


@dataclass
class ADWINLike:
    window: list[float]
    baseline_mean: float

    def update(self, val: float) -> float | None:
        self.window.append(val)
        if len(self.window) < 20:
            return None
        if len(self.window) > 100:
            self.window = self.window[-100:]
        half = len(self.window) // 2
        left = np.array(self.window[:half], dtype=np.float32)
        right = np.array(self.window[half:], dtype=np.float32)
        diff = float(abs(left.mean() - right.mean()))
        n = len(self.window)
        eps = math.sqrt(math.log(2 / 0.05) / (2 * n))
        if diff > eps:
            self.window = self.window[half:]
            self.baseline_mean = float(np.mean(self.window))
            return diff
        return None


async def detect_drift(
    patient_id: str,
    session_id: str,
    timestamp_ms: int,
    confidence: float,
    spectrogram_path: str,
    features_path: str,
    store: FileStore,
) -> list[DriftEvent]:

    drift_dir = store.session_dir(patient_id, session_id) / "drift_state"
    adwin_path = drift_dir / "adwin_state.json"
    cusum_path = drift_dir / "cusum_state.json"
    mmd_path = drift_dir / "mmd_state.json"

    conf = float(confidence)
    ad_state = store.load_json_dict(adwin_path) or {"window": [], "baseline_mean": conf}
    ad = ADWINLike(window=ad_state.get("window", []), baseline_mean=float(ad_state.get("baseline_mean", conf)))
    ad_score = ad.update(conf)
    store.save_json_dict(adwin_path, {"window": ad.window, "baseline_mean": ad.baseline_mean})

    spec = store.load_npy(spectrogram_path) if spectrogram_path else None
    stats = store.load_session_stats(patient_id, session_id)
    ref_freq = np.array(stats.channel_median_freq, dtype=np.float32) if stats else np.zeros((settings.N_CHANNELS,), dtype=np.float32)
    cur_freq = np.median(spec, axis=(1, 2)) if spec is not None else np.zeros((settings.N_CHANNELS,), dtype=np.float32)

    c_state = store.load_json_dict(cusum_path) or {
        "cumsum_pos": [0.0] * settings.N_CHANNELS,
        "cumsum_neg": [0.0] * settings.N_CHANNELS,
    }
    s_pos = np.array(c_state.get("cumsum_pos", [0.0] * settings.N_CHANNELS), dtype=np.float32)
    s_neg = np.array(c_state.get("cumsum_neg", [0.0] * settings.N_CHANNELS), dtype=np.float32)
    s_pos = np.maximum(0, s_pos + (ref_freq - cur_freq) - settings.CUSUM_K)
    s_neg = np.maximum(0, s_neg + (cur_freq - ref_freq) - settings.CUSUM_K)
    cusum_score = float(max(np.max(s_pos), np.max(s_neg)))
    store.save_json_dict(cusum_path, {"cumsum_pos": s_pos.tolist(), "cumsum_neg": s_neg.tolist(), "reference_freq": ref_freq.tolist()})

    emb = store.load_npy(features_path) if features_path else None
    m_state = store.load_json_dict(mmd_path) or {"reference_embeddings": [], "test_ring_buffer": []}
    ref = m_state.get("reference_embeddings", [])
    test = m_state.get("test_ring_buffer", [])
    if emb is not None:
        emb_l = np.asarray(emb, dtype=np.float32).tolist()
        if len(ref) < 50:
            ref.append(emb_l)
        else:
            test.append(emb_l)
            test = test[-50:]
    mmd_score = 0.0
    if len(ref) >= 10 and len(test) >= 10:
        ref_a = np.asarray(ref, dtype=np.float32)
        tst_a = np.asarray(test, dtype=np.float32)
        mmd_score = float(abs(ref_a.mean() - tst_a.mean()))
    store.save_json_dict(mmd_path, {"reference_embeddings": ref, "test_ring_buffer": test})

    events: list[DriftEvent] = []
    if ad_score is not None and ad_score > settings.CONFIDENCE_DROP_PCT:
        events.append(DriftEvent(patient_id=patient_id, session_id=session_id, timestamp_ms=timestamp_ms, drift_type="confidence", drift_score=ad_score, severity="warning"))
    if cusum_score > settings.CUSUM_H:
        events.append(DriftEvent(patient_id=patient_id, session_id=session_id, timestamp_ms=timestamp_ms, drift_type="spectral", drift_score=cusum_score, severity="critical"))
    if mmd_score > settings.MMD_THRESHOLD:
        events.append(DriftEvent(patient_id=patient_id, session_id=session_id, timestamp_ms=timestamp_ms, drift_type="embedding", drift_score=mmd_score, severity="warning"))

    for drift_event in events:
        store.save_drift_event(drift_event)
        metrics.inc("drift_events_total")
    return events
