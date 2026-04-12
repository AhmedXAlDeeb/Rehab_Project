from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter(tags=["classify"])


@router.get("/{patient_id}/latest")
async def latest_classifications(patient_id: str, request: Request, n: int = 50, session_id: str | None = None):
    store = request.app.state.store
    sessions_root = store.patient_dir(patient_id) / "sessions"
    sessions = [session_id] if session_id else sorted([s.name for s in sessions_root.iterdir() if s.is_dir()], reverse=True)
    out = []
    for sid in sessions:
        out.extend(store.load_all_classifications(patient_id, sid))
    out = sorted(out, key=lambda x: x.timestamp_ms, reverse=True)[:n]
    return [x.model_dump() for x in out]


@router.get("/{patient_id}/accuracy")
async def accuracy(patient_id: str, request: Request, session_id: str | None = None):
    store = request.app.state.store
    sessions_root = store.patient_dir(patient_id) / "sessions"
    if session_id is None:
        session_ids = sorted([s.name for s in sessions_root.iterdir() if s.is_dir()], reverse=True) if sessions_root.exists() else []
        if not session_ids:
            return {"overall_accuracy": None, "per_gesture": {}, "n_uncertain": 0, "mean_confidence": None}
        session_id = session_ids[0]

    classifications = store.load_all_classifications(patient_id, session_id)
    gt_map = {}
    for gt in store.session_dir(patient_id, session_id).glob("classifications/*_gt.json"):
        data = store.load_json_dict(gt)
        if data:
            gt_map[gt.stem.replace("_gt", "")] = int(data.get("true_gesture", -1))

    correct = 0
    total = 0
    per_total = {}
    per_ok = {}
    uncertain = 0
    for c in classifications:
        if c.is_uncertain:
            uncertain += 1
        key = str(c.timestamp_ms)
        if key in gt_map:
            total += 1
            g = str(gt_map[key])
            per_total[g] = per_total.get(g, 0) + 1
            if c.predicted_gesture == gt_map[key]:
                correct += 1
                per_ok[g] = per_ok.get(g, 0) + 1

    per_gesture = {k: per_ok.get(k, 0) / v for k, v in per_total.items() if v > 0}
    mean_conf = sum(c.confidence for c in classifications) / max(len(classifications), 1)
    return {
        "overall_accuracy": (correct / total) if total else None,
        "per_gesture": per_gesture,
        "n_uncertain": uncertain,
        "mean_confidence": mean_conf,
    }
