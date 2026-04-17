from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import httpx
import websockets
import json
import uvicorn

app = FastAPI(title="Gesture Integration Service", description="Bridges the AI service and WebSocket server.")

# URLs for your existing services
AI_SERVICE_URL = "http://localhost:8000/predict"
WS_SERVER_URL = "ws://localhost:8765"

# --- 1. Define Label Mapping (ID to String) ---
ID_TO_GESTURE = {
    0: "rest",
    # Exercise B 
    1: "b1_thumb_up", 2: "b2_index_middle_ext", 3: "b3_ring_little_flex", 4: "b4_thumb_opp_little",
    5: "b5_all_abduction", 6: "b6_fist", 7: "b7_pointing", 8: "b8_adduction_extended",
    9: "b9_wrist_sup_mid", 10: "b10_wrist_pro_mid", 11: "b11_wrist_sup_little", 12: "b12_wrist_pro_little",
    13: "b13_wrist_flexion", 14: "b14_wrist_extension", 15: "b15_wrist_radial", 16: "b16_wrist_ulnar",
    17: "b17_wrist_ext_closed",
    # Exercise C 
    18: "c1_large_diameter", 19: "c2_small_diameter", 20: "c3_fixed_hook", 21: "c4_index_ext_grasp",
    22: "c5_medium_wrap", 23: "c6_ring_grasp", 24: "c7_prismatic_four", 25: "c8_stick_grasp",
    26: "c9_writing_tripod", 27: "c10_power_sphere", 28: "c11_three_finger_sphere", 29: "c12_precision_sphere",
    30: "c13_tripod", 31: "c14_prismatic_pinch", 32: "c15_tip_pinch", 33: "c16_quadpod",
    34: "c17_lateral", 35: "c18_parallel_ext", 36: "c19_extension_type", 37: "c20_power_disk",
    38: "c21_bottle_tripod", 39: "c22_screw_stick", 40: "c23_cut_knife",
    # Exercise D 
    41: "d1_little_flex", 42: "d2_ring_flex", 43: "d3_middle_flex", 44: "d4_index_flex",
    45: "d5_thumb_abd", 46: "d6_thumb_flex", 47: "d7_index_little_flex", 48: "d8_ring_middle_flex",
    49: "d9_index_thumb_flex",
}

# --- 2. Input Schema ---
class SignalInput(BaseModel):
    signal: List[List[float]] = Field(..., description="A 2D array representing EMG data [12 channels, 400 timesteps]")

# --- 3. WebSocket Sender ---
async def send_to_websocket(gesture_name: str):
    try:
        async with websockets.connect(WS_SERVER_URL, ping_interval=None) as ws:
            # Using your example format with hardcoded confidence: 1.0
            msg = {"gesture": gesture_name, "confidence": 1.0}
            await ws.send(json.dumps(msg))
            
            raw = await ws.recv()
            resp = json.loads(raw)
            status = resp.get("status", "?")
            
            if status != "ok":
                print(f" !! Server error: {resp}")
            return status
            
    except ConnectionRefusedError:
        print(f" !! WebSocket connection refused at {WS_SERVER_URL}")
        return "connection_refused"
    except Exception as e:
        print(f" !! WebSocket error: {e}")
        return f"error: {str(e)}"

# --- 4. Main Endpoint ---
@app.post("/forward_signal")
async def process_and_forward(data: SignalInput):
    # Step 1: Call your original, untouched AI service
    try:
        async with httpx.AsyncClient() as client:
            # We send the exact JSON structure your AI service expects
            response = await client.post(AI_SERVICE_URL, json=data.model_dump(), timeout=10.0)
            
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code, 
                detail=f"AI Service failed: {response.text}"
            )
            
        # Extract the integer from your AI service's original output format
        ai_result = response.json()
        predicted_class_id = ai_result.get("predicted_class")
        
        if predicted_class_id is None:
            raise HTTPException(status_code=500, detail="AI Service did not return 'predicted_class'")
            
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Could not reach AI Service at {AI_SERVICE_URL}. Is it running?")

    # Step 2: Map the integer to the exact string name
    gesture_name = ID_TO_GESTURE.get(predicted_class_id, "unknown_gesture")

    # Step 3: Send the string to the WebSocket server
    ws_status = await send_to_websocket(gesture_name)

    # Step 4: Return a summary to whoever triggered this pipeline
    return {
        "status": "success",
        "pipeline_result": {
            "ai_predicted_id": predicted_class_id,
            "mapped_gesture": gesture_name,
            "websocket_delivery": ws_status
        }
    }

if __name__ == "__main__":
    # Run this integration service on port 8001 so it doesn't clash with your AI service
    uvicorn.run("integration_service:app", host="0.0.0.0", port=8001, reload=True)