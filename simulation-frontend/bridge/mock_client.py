"""Interactive mock client — step through all 62 gestures manually.

Controls:
  Enter      → next gesture
  p + Enter  → previous gesture
  r + Enter  → jump to rest
  q + Enter  → quit
  <number> + Enter → jump to that gesture index

Run with:
    uv run python bridge/mock_client.py
"""
import asyncio
import json
import sys
import websockets
from envs.gestures import KNOWN_GESTURES


def print_status(idx: int):
    gesture = KNOWN_GESTURES[idx]
    total = len(KNOWN_GESTURES)
    bar = "█" * (idx + 1) + "░" * (total - idx - 1)
    print(f"\n[{idx + 1:02d}/{total}] {gesture}")
    print(f"  {bar[:50]}  {(idx+1)/total*100:.0f}%")
    print("  Enter=next  p=prev  r=rest  <n>=jump  q=quit")


async def main():
    uri = "ws://localhost:8765"
    print(f"Connecting to {uri} ...")

    async with websockets.connect(uri) as ws:
        print(f"Connected. {len(KNOWN_GESTURES)} gestures loaded.\n")

        idx = 0

        async def send_gesture(name: str):
            msg = {"gesture": name, "confidence": 1.0}
            await ws.send(json.dumps(msg))
            raw = await ws.recv()
            resp = json.loads(raw)
            status = resp.get("status", "?")
            if status != "ok":
                print(f"  !! Server error: {resp}")

        # Send initial gesture
        await send_gesture(KNOWN_GESTURES[idx])
        print_status(idx)

        loop = asyncio.get_event_loop()

        while True:
            # Read input without blocking the event loop
            raw = await loop.run_in_executor(None, sys.stdin.readline)
            cmd = raw.strip().lower()

            if cmd == "q":
                print("Bye.")
                break
            elif cmd == "r":
                idx = KNOWN_GESTURES.index("rest")
            elif cmd == "p":
                idx = max(0, idx - 1)
            elif cmd.isdigit():
                n = int(cmd) - 1
                if 0 <= n < len(KNOWN_GESTURES):
                    idx = n
                else:
                    print(f"  Out of range (1–{len(KNOWN_GESTURES)})")
                    continue
            else:
                # Default: next
                idx = (idx + 1) % len(KNOWN_GESTURES)

            await send_gesture(KNOWN_GESTURES[idx])
            print_status(idx)


if __name__ == "__main__":
    asyncio.run(main())