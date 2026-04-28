import { useState } from "react";

import { GestureStreamPanel } from "./components/GestureStreamPanel";
import { SignalSenderCard } from "./components/SignalSenderCard";
import { ScenariosSection } from "./components/ScenariosSection";
import type { UnifiedInferenceResult } from "./types/api";

function App() {
  const [lastInference, setLastInference] = useState<UnifiedInferenceResult | null>(null);

  return (
    <div className="app-shell">
      <div className="app-backdrop" aria-hidden />

      <main className="app-main">
        <section className="hero-panel card">
          <h1>Rehab Gesture Control Console</h1>
          <p>
            TypeScript React frontend for manual single-shot EMG dispatch, backend inference mode switching, and
            live simulator gesture monitoring over WebSocket.
          </p>
          <div className="chip-row">
            <span className="chip">/api -&gt; integration_service :8001</span>
            <span className="chip">/directapi -&gt; classification_service :8000</span>
            <span className="chip">ws://localhost:8765</span>
          </div>
        </section>

        {lastInference && (
          <section className="last-result card">
            <div className="chip-row">
              <span className="chip chip-primary">Predicted class {lastInference.predictedClass}</span>
              <span className="chip">Mode: {lastInference.mode}</span>
              {lastInference.mappedGesture && <span className="chip chip-secondary">Gesture: {lastInference.mappedGesture}</span>}
              {lastInference.websocketDelivery && <span className="chip">WS delivery: {lastInference.websocketDelivery}</span>}
            </div>
          </section>
        )}

        <section className="main-grid">
          <SignalSenderCard onInferenceComplete={setLastInference} />
          <GestureStreamPanel />
        </section>

        <ScenariosSection /> {/* <-- Add this line here */}

      </main>
    </div>
  );
}

export default App;
