from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from schemas import PatientProfile

router = APIRouter(tags=["patient"])


class RegisterBody(BaseModel):
    patient_id: str
    age: int
    gender: str
    amputation_type: str = "none"
    forearm_circumference: float
    forearm_length: float


@router.post("/register", status_code=201)
async def register_patient(body: RegisterBody, request: Request):
    store = request.app.state.store
    if store.patient_exists(body.patient_id):
        raise HTTPException(status_code=400, detail="patient already exists")
    profile = PatientProfile(
        patient_id=body.patient_id,
        age=body.age,
        gender=body.gender,
        amputation_type=body.amputation_type,
        forearm_circumference=body.forearm_circumference,
        forearm_length=body.forearm_length,
        created_at=datetime.now(timezone.utc).isoformat(),
        model_version="base",
    )
    store.save_profile(profile)
    store.model_dir(body.patient_id)
    return profile.model_dump()


@router.get("/{patient_id}")
async def get_patient(patient_id: str, request: Request):
    store = request.app.state.store
    profile = store.load_profile(patient_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="patient not found")

    sessions_root = store.patient_dir(patient_id) / "sessions"
    session_ids = sorted([p.name for p in sessions_root.iterdir() if p.is_dir()], reverse=True) if sessions_root.exists() else []
    finetune = store.load_finetune_history(patient_id)
    return {
        **profile.model_dump(),
        "model_version": store.get_model_version(patient_id),
        "n_sessions": len(session_ids),
        "last_session_id": session_ids[0] if session_ids else None,
        "n_unused_failures": store.count_unused_failures(patient_id),
        "last_finetune_accuracy": finetune[0].accuracy_after if finetune else None,
    }


@router.get("/{patient_id}/sessions")
async def list_sessions(patient_id: str, request: Request):
    store = request.app.state.store
    sessions_root = store.patient_dir(patient_id) / "sessions"
    if not sessions_root.exists():
        return []
    metas = []
    for s in sessions_root.iterdir():
        if s.is_dir():
            m = store.load_session_meta(patient_id, s.name)
            if m is not None:
                metas.append(m)
    metas = sorted(metas, key=lambda x: x.started_at, reverse=True)
    return [m.model_dump() for m in metas]


@router.get("/{patient_id}/sessions/{session_id}")
async def session_details(patient_id: str, session_id: str, request: Request):
    store = request.app.state.store
    meta = store.load_session_meta(patient_id, session_id)
    if meta is None:
        raise HTTPException(status_code=404, detail="session not found")

    classifications = store.load_all_classifications(patient_id, session_id)
    drift = store.load_drift_events(patient_id, session_id)
    gt_map = {}
    for gt in store.session_dir(patient_id, session_id).glob("classifications/*_gt.json"):
        data = store.load_json_dict(gt)
        if data:
            gt_map[gt.stem.replace("_gt", "")] = int(data.get("true_gesture", -1))
    per_gesture = {}
    counts = {}
    for c in classifications:
        key = str(c.predicted_gesture)
        counts[key] = counts.get(key, 0) + 1
        if str(c.timestamp_ms) in gt_map:
            ok = int(gt_map[str(c.timestamp_ms)] == c.predicted_gesture)
            per_gesture[key] = per_gesture.get(key, 0) + ok
    acc = {k: per_gesture.get(k, 0) / v for k, v in counts.items() if v > 0}

    return {
        **meta.model_dump(),
        "n_classifications": len(classifications),
        "mean_confidence": (sum(x.confidence for x in classifications) / len(classifications)) if classifications else None,
        "drift_events": [d.model_dump() for d in drift],
        "accuracy_by_gesture": acc,
    }


@router.get("/{patient_id}/finetune_history")
async def finetune_history(patient_id: str, request: Request):
    store = request.app.state.store
    return [x.model_dump() for x in store.load_finetune_history(patient_id)]
