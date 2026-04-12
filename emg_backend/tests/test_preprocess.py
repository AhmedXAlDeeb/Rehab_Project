import numpy as np

from pipeline.preprocess import preprocess_frame


class Cfg:
    FS = 2000
    BANDPASS_LOW = 20.0
    BANDPASS_HIGH = 500.0
    NOTCH_FREQ = 50.0
    WINDOW_MS = 200
    STEP_MS = 10
    N_CHANNELS = 14


def test_preprocess_shapes():
    raw = np.random.randn(500, 14).astype(np.float32)
    mean = np.zeros((14,), dtype=np.float32)
    std = np.ones((14,), dtype=np.float32)
    seg, feat, spec = preprocess_frame(raw, mean, std, Cfg())
    assert seg.shape[1] == 14
    assert feat.shape == (84,)
    assert spec.shape == (14, 128, 50)
