from __future__ import annotations

import uuid

from fastapi import APIRouter, Request
from pydantic import BaseModel

from pipeline.digital_twin import run_twin_job

router = APIRouter(tags=["twin"])


class TwinGenerateBody(BaseModel):
    patient_id: str
    gesture: int = 0
    fatigue: float = 0.0
    electrode_quality: float = 1.0
    n_samples: int = 50


@router.post("/generate")
async def generate_twin(body: TwinGenerateBody, request: Request):
    store = request.app.state.store
    engine = request.app.state.get_classifier(body.patient_id)
    job_id, _ = await run_twin_job(
        patient_id=body.patient_id,
        drift_type="embedding",
        store=store,
        vae_engine=request.app.state.vae_engine,
        classifier_engine=engine,
        job_id=str(uuid.uuid4()),
    )
    return {"job_id": job_id, "status": "completed"}


@router.get("/job/{job_id}")
async def get_job(job_id: str, patient_id: str, request: Request):
    store = request.app.state.store
    meta = store.load_json_dict(store.synthetic_job_dir(patient_id, job_id) / "meta.json")
    return meta or {"job_id": job_id, "status": "not_found"}


@router.get("/stress_test/{patient_id}")
async def latest_stress_test(patient_id: str, request: Request):
    store = request.app.state.store
    syn_root = store.patient_dir(patient_id) / "synthetic"
    if not syn_root.exists():
        return {}
    jobs = sorted([p for p in syn_root.iterdir() if p.is_dir()], key=lambda p: p.name, reverse=True)
    if not jobs:
        return {}
    meta = store.load_json_dict(jobs[0] / "meta.json") or {}
    return meta.get("failure_map", {})


@router.post("/stress_test/{patient_id}")
async def queue_stress_test(patient_id: str, request: Request):
    store = request.app.state.store
    engine = request.app.state.get_classifier(patient_id)
    await run_twin_job(
        patient_id=patient_id,
        drift_type="embedding",
        store=store,
        vae_engine=request.app.state.vae_engine,
        classifier_engine=engine,
    )
    return {"status": "stress_test_completed"}
