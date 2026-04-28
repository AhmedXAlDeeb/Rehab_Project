import asyncio
import numpy as np
from main import predict_emg, SignalInput

async def test():
    try:
        data = np.load(r"d:\Eng\SBE\4th\rehab\project\Rehab_Project\integration_service\data\scenario_2.npy")
        chunk = data[:, :400].tolist()
        inp = SignalInput(signal=chunk)
        print("Testing scenario 2, chunk 0...")
        res = await predict_emg(inp)
        print("Result:", res)
    except Exception as e:
        print("EXCEPTION OCCURRED:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
