from __future__ import annotations

import numpy as np
import torch

from config import Settings, settings
from ml_models.cvae import ConditionalVAE


class VAEEngine:
    def __init__(self, cvae_path: str, config: Settings = settings):
        self._config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = ConditionalVAE(config).to(self.device)
        path = torch.tensor([])
        try:
            state = torch.load(cvae_path, map_location=self.device)
            if isinstance(state, dict) and "state_dict" in state:
                state = state["state_dict"]
            if isinstance(state, dict):
                self.model.load_state_dict(state, strict=False)
        except Exception:
            pass
        self.model.eval()

    def _cond_vec(self, patient_idx: int, gesture: int, condition_flags: dict) -> np.ndarray:
        fatigue = float(condition_flags.get("fatigue", 0.0))
        eq = float(condition_flags.get("electrode_quality", 1.0))
        sess = float(condition_flags.get("session_idx_norm", 0.0))
        amp = float(condition_flags.get("amputation", 0.0))
        base = np.array([patient_idx, gesture, fatigue, eq, sess, amp], dtype=np.float32)
        pad = np.zeros(10, dtype=np.float32)
        return np.concatenate([base, pad], axis=0)

    def generate(self, patient_id: str, patient_idx: int, gesture: int, condition_flags: dict, n_samples: int, seed: int | None = None) -> list[np.ndarray]:
        if seed is not None:
            torch.manual_seed(seed)
            np.random.seed(seed)
        cond = self._cond_vec(patient_idx, gesture, condition_flags)
        cond_t = torch.tensor(cond, dtype=torch.float32, device=self.device).view(1, -1).repeat(n_samples, 1)
        z = torch.randn(n_samples, self.model.latent_dim, device=self.device)
        with torch.no_grad():
            out = self.model.decode(z, cond_t).detach().cpu().numpy()
        return [out[i] for i in range(out.shape[0])]

    def generate_spectrogram(self, patient_idx: int, gesture: int, condition_flags: dict, n_samples: int) -> np.ndarray:
        sigs = self.generate("na", patient_idx, gesture, condition_flags, n_samples)
        specs = []
        for s in sigs:
            fft = np.abs(np.fft.rfft(s, axis=0)).T
            fft = np.resize(fft, (self._config.N_CHANNELS, 128, 50))
            specs.append(fft)
        return np.stack(specs, axis=0)
