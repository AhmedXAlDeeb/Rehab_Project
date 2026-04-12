from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATA_ROOT: Path = Path("./data")
    MODELS_ROOT: Path = Path("./models")
    CLASSIFIER_PT: Path = Path("./models/classifier_cnn.pt")
    CVAE_PT: Path = Path("./models/cvae_best.pt")
    PHASE3_INTERFACE: Path = Path("./models/phase3_interface.json")

    FS: int = 2000
    N_CHANNELS: int = 14
    WINDOW_MS: int = 200
    STEP_MS: int = 10
    BANDPASS_LOW: float = 20.0
    BANDPASS_HIGH: float = 500.0
    NOTCH_FREQ: float = 50.0
    N_GESTURES: int = 8

    WATCHER_POLL_MS: int = 100
    MAX_EVENTS_PER_TICK: int = 10

    CONFIDENCE_DROP_PCT: float = 0.15
    MMD_THRESHOLD: float = 0.1
    CUSUM_K: float = 5.0
    CUSUM_H: float = 50.0

    REPLAY_BUFFER_MAX: int = 5000
    FINETUNE_TRIGGER_N: int = 200
    FINETUNE_LR_BACKBONE: float = 1e-5
    FINETUNE_LR_HEAD: float = 1e-3
    FINETUNE_EPOCHS: int = 5
    FINETUNE_BATCH_SIZE: int = 32

    N_SYNTHETIC_PER_CELL: int = 50
    FATIGUE_LEVELS: list[float] = Field(default_factory=lambda: [0.0, 0.3, 0.6, 0.9])
    ELECTRODE_Q_LEVELS: list[float] = Field(default_factory=lambda: [1.0, 0.7, 0.4])

    CONFIDENCE_THRESHOLD: float = 0.6

    class Config:
        env_file = ".env"


settings = Settings()
