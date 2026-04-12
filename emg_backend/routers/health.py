import time

from fastapi import APIRouter, Response

from monitoring.metrics import metrics

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(request):
    app = request.app
    data_root = app.state.config.DATA_ROOT
    writable = data_root.exists() and data_root.is_dir()
    return {
        "status": "ok" if writable else "degraded",
        "data_root_writable": writable,
        "classifier_loaded": True,
        "vae_loaded": app.state.vae_engine is not None,
        "uptime_seconds": time.time() - app.state.started_at,
    }


@router.get("/metrics")
async def metrics_endpoint(request):
    text = metrics.render_prometheus()
    return Response(content=text, media_type="text/plain; version=0.0.4")
