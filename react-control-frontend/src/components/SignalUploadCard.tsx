import { useState, useRef } from "react";
import { sendSignalForInference, InferenceApiError } from "../services/inferenceApi";
import type { InferenceMode, UnifiedInferenceResult } from "../types/api";
import { SignalPreview } from "./SignalPreview";

interface SignalUploadCardProps {
  onClassificationComplete: (result: UnifiedInferenceResult) => void;
}

export function SignalUploadCard({ onClassificationComplete }: SignalUploadCardProps) {
  const [mode, setMode] = useState<InferenceMode>("integration");
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadedSignal, setUploadedSignal] = useState<number[][] | null>(null);
  const [fileName, setFileName] = useState<string>("");
  const [classificationResult, setClassificationResult] = useState<UnifiedInferenceResult | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setFileName(file.name);
    setError(null);
    setClassificationResult(null);

    try {
      let signalData: number[][];

      if (file.name.endsWith(".json")) {
        const text = await file.text();
        const parsed = JSON.parse(text);
        if (Array.isArray(parsed) && Array.isArray(parsed[0])) {
          signalData = parsed;
        } else {
          throw new Error("Invalid JSON format: expected 2D array");
        }
      } else if (file.name.endsWith(".npy")) {
        const arrayBuffer = await file.arrayBuffer();
        const uint8Array = new Uint8Array(arrayBuffer);
        signalData = parseNpy(uint8Array);
      } else if (file.name.endsWith(".csv")) {
        const text = await file.text();
        signalData = parseCSV(text);
      } else {
        throw new Error("Unsupported file format. Use .json, .npy, or .csv");
      }

      if (!signalData || signalData.length === 0) {
        throw new Error("Empty signal data");
      }

      setUploadedSignal(signalData);
    } catch (err) {
      setError(`Failed to parse file: ${err instanceof Error ? err.message : "Unknown error"}`);
      setUploadedSignal(null);
    }
  };

  const parseCSV = (text: string): number[][] => {
    const lines = text.trim().split("\n");
    return lines.map((line) =>
      line.split(",").map((val) => parseFloat(val.trim()) || 0)
    );
  };

  const parseNpy = <T extends Uint8Array>(data: T): number[][] => {
    const headerLen = parseInt(String.fromCharCode(data[6]) + String.fromCharCode(data[7])) + 8;
    const dtype = String.fromCharCode(...data.slice(8, 16)).includes("float") ? "float32" : "uint8";
    const shapeLen = data[9] === 3 ? 3 : 1;
    const shape: number[] = [];
    for (let i = 10; i < 10 + shapeLen; i++) {
      shape.push(data[i]);
    }
    const flatData = data.slice(headerLen);
    const result: number[][] = [];
    const numChannels = shape[0] || 1;
    const numTimesteps = Math.floor(flatData.length / (dtype === "float32" ? 4 : 1) / numChannels);
    for (let ch = 0; ch < numChannels; ch++) {
      const channelData: number[] = [];
      for (let t = 0; t < numTimesteps; t++) {
        if (dtype === "float32") {
          const offset = (ch * numTimesteps + t) * 4;
          channelData.push(new Float32Array(flatData.buffer, flatData.byteOffset + offset, 1)[0]);
        } else {
          channelData.push(flatData[ch * numTimesteps + t] / 255);
        }
      }
      result.push(channelData);
    }
    return result;
  };

  const handleClassify = async () => {
    if (!uploadedSignal) return;

    setIsProcessing(true);
    setError(null);

    try {
      const result = await sendSignalForInference({
        mode,
        signal: uploadedSignal,
      });
      setClassificationResult(result);
      onClassificationComplete(result);
    } catch (caughtError) {
      const normalized = caughtError instanceof InferenceApiError
        ? caughtError
        : new InferenceApiError("Failed to classify signal");
      const statusPrefix = normalized.statusCode ? `[${normalized.statusCode}] ` : "";
      setError(`${statusPrefix}${normalized.message}`);
    } finally {
      setIsProcessing(false);
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current?.click();
  };

  return (
    <section className="card signal-card">
      <div className="row-between">
        <h2>Signal Upload</h2>
        <span className="chip chip-secondary">Classification</span>
      </div>

      <p className="muted">
        Upload an EMG signal file (.json, .npy, .csv) for gesture classification. 
        The signal should be a 2D array [channels x timesteps].
      </p>

      <div className="upload-zone" onClick={triggerFileInput}>
        <input
          ref={fileInputRef}
          type="file"
          accept=".json,.npy,.csv"
          onChange={handleFileUpload}
          style={{ display: "none" }}
        />
        <div className="upload-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
            <polyline points="17 8 12 3 7 8" />
            <line x1="12" y1="3" x2="12" y2="15" />
          </svg>
        </div>
        <p>{fileName || "Click to upload or drag and drop"}</p>
        <small className="muted">Supported: .json, .npy, .csv</small>
      </div>

      {uploadedSignal && (
        <div className="preview-box">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
            <small>Signal Preview ({uploadedSignal.length} channels, {uploadedSignal[0]?.length || 0} timesteps)</small>
          </div>
          <SignalPreview signal={uploadedSignal} width={800} height={180} />
        </div>
      )}

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

      <button
        type="button"
        className="primary-button"
        disabled={!uploadedSignal || isProcessing}
        onClick={handleClassify}
      >
        {isProcessing ? "Classifying..." : "Classify Signal"}
      </button>

      {error && <div className="alert alert-error">{error}</div>}

      {classificationResult && (
        <div className="result-box">
          <h3>Classification Result</h3>
          <div className="chip-row">
            <span className="chip chip-primary">Class ID: {classificationResult.predictedClass}</span>
            {classificationResult.mappedGesture && (
              <span className="chip chip-secondary">Gesture: {classificationResult.mappedGesture}</span>
            )}
            {classificationResult.websocketDelivery && (
              <span className="chip">WS: {classificationResult.websocketDelivery}</span>
            )}
          </div>
        </div>
      )}
    </section>
  );
}