from __future__ import annotations

import numpy as np
from scipy import signal

from config import Settings, settings
from storage.filesystem import FileStore


def _extract_features(segment: np.ndarray) -> np.ndarray:
    feats = []
    for ch in range(segment.shape[1]):
        x = segment[:, ch]
        rms = np.sqrt(np.mean(x**2))
        mav = np.mean(np.abs(x))
        wl = np.sum(np.abs(np.diff(x)))
        zc = np.sum(np.diff(np.signbit(x)).astype(np.float32))
        d = np.diff(x)
        ssc = np.sum(np.diff(np.signbit(d)).astype(np.float32))
        iemg = np.sum(np.abs(x))
        feats.extend([rms, mav, wl, zc, ssc, iemg])
    return np.array(feats, dtype=np.float32)


def preprocess_frame(raw: np.ndarray, mean: np.ndarray, std: np.ndarray, config: Settings) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    fs = config.FS
    low = config.BANDPASS_LOW / (fs / 2)
    high = config.BANDPASS_HIGH / (fs / 2)
    sos_bp = signal.butter(4, [low, high], btype="bandpass", output="sos")
    b_notch, a_notch = signal.iirnotch(config.NOTCH_FREQ / (fs / 2), Q=30)
    sos_notch = signal.tf2sos(b_notch, a_notch)

    filt = signal.sosfiltfilt(sos_bp, raw, axis=0)
    filt = signal.sosfiltfilt(sos_notch, filt, axis=0)
    rect = np.abs(filt)
    std_safe = std.copy()
    std_safe[std_safe == 0] = 1.0
    norm = (rect - mean.reshape(1, -1)) / std_safe.reshape(1, -1)

    win = int(config.WINDOW_MS * fs / 1000)
    step = int(config.STEP_MS * fs / 1000)
    if norm.shape[0] < win:
        segment = np.pad(norm, ((0, win - norm.shape[0]), (0, 0)))
    else:
        segment = norm[:win]

    feature_acc = []
    for start in range(0, max(norm.shape[0] - win + 1, 1), max(step, 1)):
        wnd = norm[start : start + win]
        if wnd.shape[0] < win:
            break
        feature_acc.append(_extract_features(wnd))
    features = np.mean(feature_acc, axis=0) if feature_acc else _extract_features(segment)

    spec_channels = []
    for ch in range(config.N_CHANNELS):
        f, t, z = signal.stft(segment[:, ch], fs=fs, nperseg=min(64, segment.shape[0]))
        mag = np.abs(z)
        mag = np.resize(mag, (128, 50))
        spec_channels.append(mag)
    spectrogram = np.stack(spec_channels, axis=0).astype(np.float32)
    return segment.astype(np.float32), features.astype(np.float32), spectrogram


def preprocess_and_store(patient_id: str, session_id: str, timestamp_ms: int, store: FileStore) -> dict[str, str] | None:

    seg_path = store.session_dir(patient_id, session_id) / "segments" / f"{timestamp_ms}.npy"
    if seg_path.exists():
        return

    raw_path = store.session_dir(patient_id, session_id) / "raw" / f"{timestamp_ms}.npy"
    raw = store.load_npy(raw_path)
    if raw is None:
        return None

    stats = store.load_session_stats(patient_id, session_id)
    if stats is None:
        mean = np.zeros((settings.N_CHANNELS,), dtype=np.float32)
        std = np.ones((settings.N_CHANNELS,), dtype=np.float32)
    else:
        mean = np.asarray(stats.channel_mean, dtype=np.float32)
        std = np.sqrt(np.asarray(stats.channel_m2, dtype=np.float32) / max(stats.n_samples - 1, 1))
        std[std == 0] = 1.0

    segment, features, spectrogram = preprocess_frame(raw, mean, std, settings)
    seg_p = store.save_segment(patient_id, session_id, timestamp_ms, segment)
    feat_p = store.save_features(patient_id, session_id, timestamp_ms, features)
    spec_p = store.save_spectrogram(patient_id, session_id, timestamp_ms, spectrogram)

    rel_seg = str(seg_p.relative_to(settings.DATA_ROOT))
    rel_feat = str(feat_p.relative_to(settings.DATA_ROOT))
    rel_spec = str(spec_p.relative_to(settings.DATA_ROOT))

    return {
        "segment_path": rel_seg,
        "features_path": rel_feat,
        "spectrogram_path": rel_spec,
    }
