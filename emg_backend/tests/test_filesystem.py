import numpy as np
from storage.filesystem import FileStore


def test_atomic_and_missing_load(tmp_path, monkeypatch):
    from config import settings

    monkeypatch.setattr(settings, "DATA_ROOT", tmp_path)
    store = FileStore()

    arr = np.ones((10, 14), dtype=np.float32)
    p = store.save_raw_frame("p", "s", 1, arr)
    assert p.exists()
    loaded = store.load_npy(p)
    assert loaded.shape == (10, 14)

    assert store.load_npy(tmp_path / "missing.npy") is None

