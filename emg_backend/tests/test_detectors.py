import asyncio

from storage.filesystem import FileStore
from pipeline.drift import detect_drift


async def _run(store):
    for i in range(120):
        conf = 0.95 if i < 70 else 0.2
        await detect_drift(
            patient_id="p",
            session_id="s",
            timestamp_ms=i,
            confidence=conf,
            spectrogram_path="",
            features_path="",
            store=store,
        )


def test_drift_detection(tmp_path, monkeypatch):
    from config import settings

    monkeypatch.setattr(settings, "DATA_ROOT", tmp_path)
    store = FileStore()
    asyncio.run(_run(store))
    events = store.load_drift_events("p", "s")
    assert isinstance(events, list)
