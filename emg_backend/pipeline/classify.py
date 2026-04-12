from __future__ import annotations

from config import settings
from engines.classifier_engine import ClassifierEngine
from monitoring.metrics import metrics
from schemas import ClassificationResult
from storage.filesystem import FileStore


async def classify_and_store(
    patient_id: str,
    session_id: str,
    timestamp_ms: int,
    features_path: str,
    spectrogram_path: str,
    store: FileStore,
    engine: ClassifierEngine,
) -> ClassificationResult | None:

    cls_path = store.session_dir(patient_id, session_id) / "classifications" / f"{timestamp_ms}.json"
    if cls_path.exists():
        return

    features = store.load_npy(features_path)
    if features is None:
        return None

    pred, conf, probs = await engine.predict(features)
    result = ClassificationResult(
        patient_id=patient_id,
        session_id=session_id,
        timestamp_ms=timestamp_ms,
        predicted_gesture=pred,
        confidence=conf,
        probabilities=probs.tolist(),
        model_version=engine.version,
        is_uncertain=conf < settings.CONFIDENCE_THRESHOLD,
    )
    store.save_classification(result)

    session_dir = store.session_dir(patient_id, session_id)
    buf_path = session_dir / "confidence_buffer.json"
    buf = store.load_json_dict(buf_path) or {"values": []}
    values = buf.get("values", [])
    values.append(conf)
    values = values[-100:]
    store.save_json_dict(buf_path, {"values": values})

    metrics.inc("classifications_total")
    metrics.set_gauge(f"mean_confidence_{patient_id}", sum(values) / max(len(values), 1))
    return result
