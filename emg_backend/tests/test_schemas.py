from schemas import EMGFrame


def test_schema_roundtrip():
    frame = EMGFrame(patient_id="p1", session_id="s1", timestamp_ms=1, channels=[[0.0] * 14])
    payload = frame.model_dump_json()
    loaded = EMGFrame.model_validate_json(payload)
    assert loaded.patient_id == "p1"
