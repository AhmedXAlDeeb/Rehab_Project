from __future__ import annotations

import asyncio

import numpy as np

from config import settings
from schemas import SessionStats
from storage.filesystem import FileStore


class WelfordStats:
    def __init__(self, patient_id: str, session_id: str, store: FileStore):
        self.patient_id = patient_id
        self.session_id = session_id
        self.store = store
        self._lock = asyncio.Lock()
        loaded = self.store.load_session_stats(patient_id, session_id)
        if loaded is None:
            loaded = SessionStats(
                patient_id=patient_id,
                session_id=session_id,
                n_samples=0,
                channel_mean=[0.0] * settings.N_CHANNELS,
                channel_m2=[0.0] * settings.N_CHANNELS,
                channel_median_freq=[0.0] * settings.N_CHANNELS,
            )
            self.store.save_session_stats(loaded)
        self._stats = loaded

    async def update(self, frame: np.ndarray) -> None:
        async with self._lock:
            n = self._stats.n_samples
            mean = np.array(self._stats.channel_mean, dtype=np.float64)
            m2 = np.array(self._stats.channel_m2, dtype=np.float64)
            for sample in frame:
                n += 1
                delta = sample - mean
                mean = mean + delta / n
                delta2 = sample - mean
                m2 = m2 + delta * delta2

            med = np.array(self._stats.channel_median_freq, dtype=np.float64)
            current = np.median(np.abs(np.fft.rfft(frame, axis=0)), axis=0)
            alpha = 0.05
            if np.all(med == 0):
                med = current
            else:
                med = (1 - alpha) * med + alpha * current

            self._stats = SessionStats(
                patient_id=self.patient_id,
                session_id=self.session_id,
                n_samples=n,
                channel_mean=mean.tolist(),
                channel_m2=m2.tolist(),
                channel_median_freq=med.tolist(),
            )
            self.store.save_session_stats(self._stats)

    async def get_stats(self) -> tuple[np.ndarray, np.ndarray]:
        async with self._lock:
            mean = np.array(self._stats.channel_mean, dtype=np.float64)
            m2 = np.array(self._stats.channel_m2, dtype=np.float64)
            n = max(self._stats.n_samples - 1, 1)
            std = np.sqrt(m2 / n)
            std[std == 0] = 1.0
            return mean, std

    async def get_median_freq(self) -> np.ndarray:
        async with self._lock:
            return np.array(self._stats.channel_median_freq, dtype=np.float64)
