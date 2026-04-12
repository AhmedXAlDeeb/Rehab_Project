from __future__ import annotations

import asyncio
import logging
import time
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI

from config import settings
from engines.classifier_engine import ClassifierEngine
from engines.vae_engine import VAEEngine
from pipeline.finetuner import finetune_patient
from routers.classify import router as classify_router
from routers.health import router as health_router
from routers.ingest import router as ingest_router
from routers.patient import router as patient_router
from routers.twin import router as twin_router
from storage.filesystem import FileStore


structlog.configure(processors=[structlog.processors.TimeStamper(fmt="iso"), structlog.processors.JSONRenderer()])
logger = structlog.get_logger(__name__)


async def periodic_finetune_check(app: FastAPI):
    store = app.state.store
    while True:
        await asyncio.sleep(1800)
        for patient_id in store.list_patients():
            n = store.count_unused_failures(patient_id)
            if n >= settings.FINETUNE_TRIGGER_N:
                engine = app.state.get_classifier(patient_id)
                await finetune_patient(patient_id, store, engine, trigger="failure_count")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging.INFO)
    settings.DATA_ROOT.mkdir(parents=True, exist_ok=True)

    store = FileStore()
    app.state.store = store
    app.state.config = settings
    app.state.started_at = time.time()
    app.state.welford_map = {}
    app.state.classifier_engines = {}
    app.state.vae_engine = VAEEngine(str(settings.CVAE_PT), settings)

    def get_classifier(patient_id: str) -> ClassifierEngine:
        engines = app.state.classifier_engines
        if patient_id not in engines:
            engines[patient_id] = ClassifierEngine(store=store, patient_id=patient_id, config=settings)
        return engines[patient_id]
    app.state.get_classifier = get_classifier

    app.state.periodic_task = asyncio.create_task(periodic_finetune_check(app))
    logger.info(
        "startup",
        data_root=str(settings.DATA_ROOT),
        n_patients=len(store.list_patients()),
        models_loaded={"classifier": settings.CLASSIFIER_PT.exists(), "vae": settings.CVAE_PT.exists()},
    )

    yield

    app.state.periodic_task.cancel()
    logger.info("shutdown")


app = FastAPI(title="EMG Digital Twin", version="1.0.0", lifespan=lifespan)
app.include_router(ingest_router, prefix="/v1/ingest")
app.include_router(patient_router, prefix="/v1/patient")
app.include_router(classify_router, prefix="/v1/classify")
app.include_router(twin_router, prefix="/v1/twin")
app.include_router(health_router)
