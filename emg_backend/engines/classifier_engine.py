from __future__ import annotations

import asyncio
from pathlib import Path

import numpy as np
import torch

from config import Settings, settings
from ml_models.classifier import ClassifierCNN
from storage.filesystem import FileStore


class ClassifierEngine:
    def __init__(self, store: FileStore, patient_id: str, config: Settings = settings):
        self._store = store
        self._patient_id = patient_id
        self._config = config
        self._model = ClassifierCNN(in_dim=84, embedding_dim=128, n_classes=config.N_GESTURES)
        self._model.eval()
        self._version = "base"
        self._version_mtime = 0.0
        self._lock = asyncio.Lock()
        self._load_model()

    def _version_file(self) -> Path:
        return self._store.model_dir(self._patient_id) / "current_version.txt"

    def _load_model(self) -> None:
        ckpt, version = self._store.load_model_checkpoint(self._patient_id)
        if ckpt is None:
            base_path = self._config.CLASSIFIER_PT
            if base_path.exists():
                ckpt = torch.load(base_path, map_location="cpu")
        if ckpt is not None:
            if "state_dict" in ckpt:
                ckpt = ckpt["state_dict"]
            self._model.load_state_dict(ckpt, strict=False)
        self._version = version

    async def _maybe_reload(self) -> None:
        vf = self._version_file()
        if not vf.exists():
            return
        mtime = vf.stat().st_mtime
        if mtime > self._version_mtime:
            self._load_model()
            self._version_mtime = mtime

    async def predict(self, features: np.ndarray) -> tuple[int, float, np.ndarray]:
        async with self._lock:
            await self._maybe_reload()
            x = torch.tensor(features, dtype=torch.float32).view(1, -1)
            logits = self._model(x) / 1.3
            probs = torch.softmax(logits, dim=-1).detach().cpu().numpy()[0]
            pred = int(np.argmax(probs))
            conf = float(np.max(probs))
            return pred, conf, probs

    async def get_embedding(self, features: np.ndarray) -> np.ndarray:
        async with self._lock:
            await self._maybe_reload()
            x = torch.tensor(features, dtype=torch.float32).view(1, -1)
            emb = self._model.get_embedding(x).detach().cpu().numpy()[0]
            return emb

    async def get_probabilities_batch(self, features: np.ndarray) -> np.ndarray:
        async with self._lock:
            await self._maybe_reload()
            x = torch.tensor(features, dtype=torch.float32)
            logits = self._model(x) / 1.3
            return torch.softmax(logits, dim=-1).detach().cpu().numpy()

    @property
    def version(self) -> str:
        return self._version
