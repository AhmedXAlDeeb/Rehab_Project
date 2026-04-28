import { useMemo, useState } from "react";

import {
  generateAndFineTuneClassifier,
  generateSyntheticSamples,
  InferenceApiError,
  sendSignalForInference,
} from "../services/inferenceApi";
import type { GenerationFlags, InferenceMode, UnifiedInferenceResult } from "../types/api";
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
  const [isGenerating, setIsGenerating] = useState(false);
  const [isFineTuning, setIsFineTuning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastLatencyMs, setLastLatencyMs] = useState<number | null>(null);
  const [lastResult, setLastResult] = useState<UnifiedInferenceResult | null>(null);
  const [vaeInfo, setVaeInfo] = useState<string | null>(null);

  const [subjectIdx, setSubjectIdx] = useState(0);
  const [gestureIdx, setGestureIdx] = useState(5);
  const [nSamples, setNSamples] = useState(30);
  const [seed, setSeed] = useState(42);
  const [flags, setFlags] = useState<GenerationFlags>({
    fatigue: 0,
    electrode_quality: 1,
    session_idx_norm: 0,
    amputation: 0,
  });

  const [ftEpochs, setFtEpochs] = useState(3);
  const [ftBatchSize, setFtBatchSize] = useState(32);
  const [ftLearningRate, setFtLearningRate] = useState(1e-4);

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

  const handleGenerateOnly = async () => {
    setIsGenerating(true);
    setError(null);
    setVaeInfo(null);
    try {
      const response = await generateSyntheticSamples({
        subject_idx_0based: subjectIdx,
        gesture_0based: gestureIdx,
        flags,
        n_samples: nSamples,
        seed,
      });
      const preview = response.samples[0]?.[0]?.slice(0, 5).map((v) => v.toFixed(3)).join(", ") ?? "n/a";
      setVaeInfo(
        `Generated ${response.n_samples} samples (${response.shape[0]}x${response.shape[1]}), ` +
          `gesture=${response.gesture_label}, modelLoaded=${response.model_loaded}. ch0 preview: [${preview}]`,
      );
    } catch (caughtError) {
      const normalized =
        caughtError instanceof InferenceApiError
          ? caughtError
          : new InferenceApiError("failed to generate synthetic samples");
      const statusPrefix = normalized.statusCode ? `[${normalized.statusCode}] ` : "";
      setError(`${statusPrefix}${normalized.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleGenerateAndFinetune = async () => {
    setIsFineTuning(true);
    setError(null);
    setVaeInfo(null);
    try {
      const response = await generateAndFineTuneClassifier({
        subject_idx_0based: subjectIdx,
        gesture_0based: gestureIdx,
        flags,
        n_samples: nSamples,
        seed,
        finetune_epochs: ftEpochs,
        finetune_batch_size: ftBatchSize,
        finetune_learning_rate: ftLearningRate,
      });
      setVaeInfo(
        `Generated ${response.generation.n_samples} samples and fine-tuned classifier: ` +
          `${response.finetune.status}, loss ${response.finetune.initial_loss?.toFixed(4) ?? "n/a"} -> ` +
          `${response.finetune.final_loss?.toFixed(4) ?? "n/a"}.`,
      );
    } catch (caughtError) {
      const normalized =
        caughtError instanceof InferenceApiError ? caughtError : new InferenceApiError("failed to fine-tune model");
      const statusPrefix = normalized.statusCode ? `[${normalized.statusCode}] ` : "";
      setError(`${statusPrefix}${normalized.message}`);
    } finally {
      setIsFineTuning(false);
    }
  };

  const onFlagChange = (key: keyof GenerationFlags, value: number) => {
    setFlags((prev) => ({ ...prev, [key]: value }));
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

      <div className="result-box">
        <h3>VAE Synthetic Data</h3>
        <p className="muted">Notebook-style call: subject_idx_0based, gesture_0based, and drift flags.</p>

        <div className="control-grid">
          <label>
            Subject
            <input
              type="number"
              min={0}
              value={subjectIdx}
              onChange={(e) => setSubjectIdx(Number(e.target.value))}
            />
          </label>
          <label>
            Gesture
            <input
              type="number"
              min={0}
              max={52}
              value={gestureIdx}
              onChange={(e) => setGestureIdx(Number(e.target.value))}
            />
          </label>
          <label>
            Samples
            <input
              type="number"
              min={1}
              max={500}
              value={nSamples}
              onChange={(e) => setNSamples(Number(e.target.value))}
            />
          </label>
          <label>
            Seed
            <input type="number" value={seed} onChange={(e) => setSeed(Number(e.target.value))} />
          </label>
        </div>

        <div className="control-grid">
          <label>
            Fatigue
            <input
              type="number"
              step={0.05}
              min={0}
              max={1}
              value={flags.fatigue}
              onChange={(e) => onFlagChange("fatigue", Number(e.target.value))}
            />
          </label>
          <label>
            Electrode quality
            <input
              type="number"
              step={0.05}
              min={0}
              max={1}
              value={flags.electrode_quality}
              onChange={(e) => onFlagChange("electrode_quality", Number(e.target.value))}
            />
          </label>
          <label>
            Session idx norm
            <input
              type="number"
              step={0.05}
              min={0}
              max={1}
              value={flags.session_idx_norm}
              onChange={(e) => onFlagChange("session_idx_norm", Number(e.target.value))}
            />
          </label>
          <label>
            Amputation
            <input
              type="number"
              step={0.05}
              min={0}
              max={1}
              value={flags.amputation}
              onChange={(e) => onFlagChange("amputation", Number(e.target.value))}
            />
          </label>
        </div>

        <div className="control-grid">
          <label>
            Fine-tune epochs
            <input
              type="number"
              min={1}
              max={50}
              value={ftEpochs}
              onChange={(e) => setFtEpochs(Number(e.target.value))}
            />
          </label>
          <label>
            Fine-tune batch size
            <input
              type="number"
              min={1}
              max={256}
              value={ftBatchSize}
              onChange={(e) => setFtBatchSize(Number(e.target.value))}
            />
          </label>
          <label>
            Fine-tune learning rate
            <input
              type="number"
              min={0.000001}
              max={1}
              step={0.00001}
              value={ftLearningRate}
              onChange={(e) => setFtLearningRate(Number(e.target.value))}
            />
          </label>
          <div className="button-group-inline">
            <button type="button" className="ghost-button" disabled={isGenerating} onClick={handleGenerateOnly}>
              {isGenerating ? "Generating..." : "Generate Synthetic"}
            </button>
            <button
              type="button"
              className="primary-button"
              disabled={isFineTuning}
              onClick={handleGenerateAndFinetune}
            >
              {isFineTuning ? "Fine-tuning..." : "Generate + Fine-tune"}
            </button>
          </div>
        </div>

        {vaeInfo && <div className="alert alert-warn">{vaeInfo}</div>}
      </div>

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
