import requests
import numpy as np

# Create dummy data perfectly matching the required [12, 400] shape
dummy_signal = np.random.rand(12, 400).tolist()

payload = {
    "signal": dummy_signal
}

response = requests.post("http://localhost:8000/predict", json=payload)
print(response.json())
# Expected Output: {'predicted_class': 24, 'status': 'success'}