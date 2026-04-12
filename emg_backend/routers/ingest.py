from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from monitoring.metrics import metrics
from pipeline.classify import classify_and_store
from pipeline.drift import detect_drift
from pipeline.ingest import handle_ingest
from pipeline.preprocess import preprocess_and_store
from schemas import ClassificationResult, EMGFrame, FailureCase
from storage.session_stats import WelfordStats

router = APIRouter(tags=["ingest"])


class FeedbackBody(BaseModel):
    session_id: str
    timestamp_ms: int
    true_gesture: int
    source: str = "user"


@router.post("/emg")
async def ingest_emg(frame: EMGFrame, request: Request):
    store = request.app.state.store
    if not store.patient_exists(frame.patient_id):
        raise HTTPException(status_code=404, detail="patient not registered")

    key = (frame.patient_id, frame.session_id)
    welford_map = request.app.state.welford_map
    if key not in welford_map:
        welford_map[key] = WelfordStats(frame.patient_id, frame.session_id, store)

    await handle_ingest(frame, store, welford_map[key])
    processed = preprocess_and_store(frame.patient_id, frame.session_id, frame.timestamp_ms, store)

    classification = None
    drift_events = []
    if processed is not None:
        engine = request.app.state.get_classifier(frame.patient_id)
        classification = await classify_and_store(
            patient_id=frame.patient_id,
            session_id=frame.session_id,
            timestamp_ms=frame.timestamp_ms,
            features_path=processed["features_path"],
            spectrogram_path=processed["spectrogram_path"],
            store=store,
            engine=engine,
        )
        if classification is not None:
            drift_events = await detect_drift(
                patient_id=frame.patient_id,
                session_id=frame.session_id,
                timestamp_ms=frame.timestamp_ms,
                confidence=classification.confidence,
                spectrogram_path=processed["spectrogram_path"],
                features_path=processed["features_path"],
                store=store,
            )

    metrics.inc("frames_received")
    return {
        "status": "accepted",
        "session_id": frame.session_id,
        "timestamp_ms": frame.timestamp_ms,
        "classified": classification is not None,
        "n_drift_events": len(drift_events),
    }


@router.post("/feedback")
async def ingest_feedback(body: FeedbackBody, request: Request, patient_id: str):
    store = request.app.state.store
    if not store.patient_exists(patient_id):
        raise HTTPException(status_code=404, detail="patient not registered")

    cls_path = store.session_dir(patient_id, body.session_id) / "classifications" / f"{body.timestamp_ms}.json"
    cls = store._load_json_model(cls_path, ClassificationResult)
    if cls is None:
        raise HTTPException(status_code=404, detail="classification not found")

    if cls.predicted_gesture != body.true_gesture:
        case = FailureCase(
            patient_id=patient_id,
            session_id=body.session_id,
            timestamp_ms=body.timestamp_ms,
            gesture_true=body.true_gesture,
            gesture_predicted=cls.predicted_gesture,
            confidence=cls.confidence,
            condition_flags={"source": body.source},
            spectrogram_path=str(
                store.session_dir(patient_id, body.session_id) / "spectrograms" / f"{body.timestamp_ms}.npy"
            ),
            source="real",
        )
        store.save_failure_case(case)

    gt_path = store.session_dir(patient_id, body.session_id) / "classifications" / f"{body.timestamp_ms}_gt.json"
    store.save_json_dict(gt_path, {"true_gesture": body.true_gesture, "source": body.source})
    return {"recorded": True}
