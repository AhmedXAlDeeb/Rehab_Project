import { useMemo, useState } from "react";

import { InferenceApiError, sendSignalForInference } from "../services/inferenceApi";
import type { InferenceMode, UnifiedInferenceResult } from "../types/api";
import { createMockSignal, SIGNAL_CHANNELS, SIGNAL_TIMESTEPS } from "../utils/signal";

interface SignalSenderCardProps {
  onInferenceComplete: (result: UnifiedInferenceResult) => void;
}

function prettyMode(mode: InferenceMode): string {
  return mode === "integration" ? "Integration Service :8001" : "Direct Classifier :8000";
}

export function SignalSenderCard({ onInferenceComplete }: SignalSenderCardProps) {
  const [mode, setMode] = useState<InferenceMode>("integration");
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastLatencyMs, setLastLatencyMs] = useState<number | null>(null);
  const [lastResult, setLastResult] = useState<UnifiedInferenceResult | null>(null);

  const samplePreview = useMemo(() => createMockSignal(2026)[0].slice(0, 8), []);

  const handleSend = async () => {
    const startedAt = performance.now();
    setIsSending(true);
    setError(null);

    try {
      const result = await sendSignalForInference({
        mode,
        signal: createMockSignal(Date.now()),
      });
      setLastResult(result);
      onInferenceComplete(result);
      setLastLatencyMs(Math.round(performance.now() - startedAt));
    } catch (caughtError) {
      const normalized =
        caughtError instanceof InferenceApiError
          ? caughtError
          : new InferenceApiError("failed to send signal");
      const statusPrefix = normalized.statusCode ? `[${normalized.statusCode}] ` : "";
      setError(`${statusPrefix}${normalized.message}`);
    } finally {
      setIsSending(false);
    }
  };

  return (
    <section className="card signal-card">
      <div className="row-between">
        <h2>Signal Control</h2>
        <span className="chip chip-secondary">
          {SIGNAL_CHANNELS}x{SIGNAL_TIMESTEPS} mock signal
        </span>
      </div>

      <p className="muted">
        Send a manual single-shot EMG payload to your backend. Choose integration mode to forward into the simulator
        bridge, or direct mode to call the classifier only.
      </p>

      <div className="mode-tabs">
        <button
          type="button"
          className={`mode-btn ${mode === "integration" ? "active" : ""}`}
          onClick={() => setMode("integration")}
        >
          Integration Mode
        </button>
        <button
          type="button"
          className={`mode-btn ${mode === "direct" ? "active" : ""}`}
          onClick={() => setMode("direct")}
        >
          Direct Mode
        </button>
      </div>

      <div className="preview-box">
        <small>Channel[0] preview</small>
        <pre>[{samplePreview.join(", ")} ...]</pre>
      </div>

      <button type="button" className="primary-button" disabled={isSending} onClick={handleSend}>
        {isSending ? "Sending..." : `Send Single Shot (${prettyMode(mode)})`}
      </button>

      {error && <div className="alert alert-error">{error}</div>}

      {lastResult && (
        <div className="result-box">
          <h3>Last inference result</h3>
          <div className="chip-row">
            <span className="chip chip-primary">Class ID: {lastResult.predictedClass}</span>
            {lastResult.mappedGesture && <span className="chip chip-secondary">Gesture: {lastResult.mappedGesture}</span>}
            {lastResult.websocketDelivery && <span className="chip">WS: {lastResult.websocketDelivery}</span>}
            {lastLatencyMs !== null && <span className="chip">Latency: {lastLatencyMs} ms</span>}
          </div>
        </div>
      )}
    </section>
  );
}
