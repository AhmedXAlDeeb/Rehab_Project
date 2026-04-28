import httpx
import json
import numpy as np

BASE_URL = "http://localhost:8003"
CLASSIFIER_URL = "http://localhost:8000"


def test_health():
    response = httpx.get(f"{BASE_URL}/health")
    print("=== Health Check ===")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200


def test_generate_single():
    payload = {
        "subject_idx_0based": 0,
        "gesture_0based": 1,
        "flags": {
            "fatigue": 0.0,
            "electrode_quality": 1.0,
            "session_idx_norm": 0.0,
            "amputation": 0.0,
        },
        "n_samples": 1,
        "seed": 42,
    }
    response = httpx.post(f"{BASE_URL}/generate", json=payload)
    print("\n=== Generate Single Sample ===")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Status: {data.get('status')}")
    print(f"Shape: {data.get('shape')}")
    print(f"Gesture label: {data.get('gesture_label')}")
    print(f"n_samples: {data.get('n_samples')}")
    if "samples" in data:
        sample = data["samples"][0]
        print(f"Sample shape: {len(sample)}x{len(sample[0])}")
    return response.status_code == 200


def test_generate_multiple():
    payload = {
        "subject_idx_0based": 2,
        "gesture_0based": 5,
        "flags": {
            "fatigue": 0.3,
            "electrode_quality": 0.8,
            "session_idx_norm": 0.5,
            "amputation": 0.0,
        },
        "n_samples": 5,
        "seed": 123,
    }
    response = httpx.post(f"{BASE_URL}/generate", json=payload)
    print("\n=== Generate Multiple Samples ===")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Status: {data.get('status')}")
    print(f"n_samples: {data.get('n_samples')}")
    print(f"Samples received: {len(data.get('samples', []))}")
    return response.status_code == 200


def test_generate_different_gestures():
    gestures = [0, 10, 20, 30, 40, 50]
    print("\n=== Generate Different Gestures ===")
    for g in gestures:
        payload = {
            "subject_idx_0based": 0,
            "gesture_0based": g,
            "n_samples": 1,
            "seed": 42,
        }
        response = httpx.post(f"{BASE_URL}/generate", json=payload)
        data = response.json()
        print(
            f"Gesture {g}: status={data.get('status')}, samples={len(data.get('samples', []))}"
        )


def test_without_seed():
    payload = {"subject_idx_0based": 1, "gesture_0based": 3, "n_samples": 3}
    response = httpx.post(f"{BASE_URL}/generate", json=payload)
    print("\n=== Generate Without Seed (should vary each call) ===")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Status: {data.get('status')}")
    return response.status_code == 200


def test_finetune_on_generated():
    payload = {
        "subject_idx_0based": 0,
        "gesture_0based": 5,
        "flags": {
            "fatigue": 0.0,
            "electrode_quality": 1.0,
            "session_idx_norm": 0.0,
            "amputation": 0.0,
        },
        "n_samples": 10,
        "seed": 42,
        "finetune_epochs": 2,
        "finetune_batch_size": 16,
        "finetune_learning_rate": 1e-4,
        "save_samples": True,
        "samples_output_dir": "./generated_samples",
    }
    response = httpx.post(
        f"{BASE_URL}/finetune_on_generated", json=payload, timeout=120.0
    )
    print("\n=== Finetune on Generated ===")
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Status: {data.get('status')}")
    if "generation" in data:
        gen = data["generation"]
        print(f"Generation status: {gen.get('status')}")
        print(f"Samples saved to: {gen.get('samples_saved_to')}")
    if "finetune" in data:
        ft = data["finetune"]
        print(f"Finetune status: {ft.get('status')}")
        print(f"Samples used: {ft.get('samples_used')}")
        print(f"Initial loss: {ft.get('initial_loss')}")
        print(f"Final loss: {ft.get('final_loss')}")
    if "finetune_error" in data:
        print(f"Finetune error: {data.get('finetune_error')}")
    return response.status_code == 200


def test_classifier_available():
    try:
        response = httpx.get(f"{CLASSIFIER_URL}/health", timeout=5.0)
        if response.status_code == 200:
            print("\n=== Classifier Service Available ===")
            print(json.dumps(response.json(), indent=2))
            return True
    except Exception as e:
        print(f"\n=== Classifier Service NOT Available ===")
        print(f"Error: {e}")
        print("Make sure classification_service is running on port 8000")
    return False


def main():
    print("Testing Generation Service API\n")

    if not test_health():
        print("\nERROR: Service not running or not reachable at", BASE_URL)
        print("Make sure to start the service: python main.py")
        return

    test_generate_single()
    test_generate_multiple()
    test_generate_different_gestures()
    test_without_seed()

    classifier_available = test_classifier_available()
    if classifier_available:
        test_finetune_on_generated()
    else:
        print("\nSkipping finetune test - classifier service not available")

    print("\n=== All tests completed ===")


if __name__ == "__main__":
    main()
