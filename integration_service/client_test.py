import requests
import random

# URL of your Integration Service (Port 8001)
INTEGRATION_URL = "http://localhost:8001/forward_signal"

print("1. Generating fake EMG signal (12 channels, 400 timesteps)...")
# Create a 12x400 array of random floats between -1.0 and 1.0
fake_signal = [
    [random.uniform(-1.0, 1.0) for _ in range(400)] 
    for _ in range(12)
]

payload = {
    "signal": fake_signal
}

print(f"2. Sending request to Integration Service at {INTEGRATION_URL}...")

try:
    response = requests.post(INTEGRATION_URL, json=payload)
    
    print("\n3. Received Response:")
    print("-" * 30)
    # Pretty print the JSON response
    import json
    print(json.dumps(response.json(), indent=4))
    print("-" * 30)
    
except requests.exceptions.ConnectionError:
    print(f"\n[!] Error: Could not connect to {INTEGRATION_URL}.")
    print("Is the Integration Service running?")