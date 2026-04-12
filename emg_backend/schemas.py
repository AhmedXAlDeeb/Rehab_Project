from typing import Optional

from pydantic import BaseModel


class PatientProfile(BaseModel):
    patient_id: str
    age: int
    gender: str
    amputation_type: str = "none"
    forearm_circumference: float
    forearm_length: float
    created_at: str
    model_version: str = "base"


class SessionMeta(BaseModel):
    session_id: str
    patient_id: str
    day_index: int
    time_index: int
    started_at: str
    ended_at: Optional[str] = None
    n_frames: int = 0
    mean_confidence: Optional[float] = None


class SessionStats(BaseModel):
    patient_id: str
    session_id: str
    n_samples: int = 0
    channel_mean: list[float]
    channel_m2: list[float]
    channel_median_freq: list[float]


class EMGFrame(BaseModel):
    patient_id: str
    session_id: str
    timestamp_ms: int
    channels: list[list[float]]
    sample_rate: int = 2000


class ClassificationResult(BaseModel):
    patient_id: str
    session_id: str
    timestamp_ms: int
    predicted_gesture: int
    confidence: float
    probabilities: list[float]
    model_version: str
    is_uncertain: bool


class DriftEvent(BaseModel):
    patient_id: str
    session_id: str
    timestamp_ms: int
    drift_type: str
    drift_score: float
    severity: str


class FailureCase(BaseModel):
    patient_id: str
    session_id: Optional[str] = None
    timestamp_ms: int
    gesture_true: int
    gesture_predicted: int
    confidence: float
    condition_flags: dict
    spectrogram_path: str
    source: str
    used_in_finetune: bool = False


class FineTuneRecord(BaseModel):
    patient_id: str
    timestamp_ms: int
    trigger: str
    model_version_before: str
    model_version_after: str
    accuracy_before: float
    accuracy_after: float
    n_failure_cases: int
    n_real_samples: int
    duration_seconds: float
