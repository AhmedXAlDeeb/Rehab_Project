export type SignalMatrix = number[][];

export type InferenceMode = "integration" | "direct";

export interface SignalInput {
  signal: SignalMatrix;
}

export interface IntegrationPipelineResult {
  ai_predicted_id: number;
  mapped_gesture: string;
  websocket_delivery: string;
}

export interface ForwardSignalResponse {
  status: string;
  pipeline_result: IntegrationPipelineResult;
}

export interface PredictResponse {
  predicted_class: number;
  status: string;
}

export interface UnifiedInferenceResult {
  mode: InferenceMode;
  predictedClass: number;
  mappedGesture?: string;
  websocketDelivery?: string;
  raw: ForwardSignalResponse | PredictResponse;
}

export interface GenerationFlags {
  fatigue: number;
  electrode_quality: number;
  session_idx_norm: number;
  amputation: number;
}

export interface VAEGenerateRequest {
  subject_idx_0based: number;
  gesture_0based: number;
  flags: GenerationFlags;
  n_samples: number;
  seed?: number;
}

export interface VAEGenerateResponse {
  status: string;
  shape: [number, number];
  gesture_label: number;
  n_samples: number;
  samples: number[][][];
  model_loaded: boolean;
  model_load_error?: string | null;
}

export interface VAEGenerateAndFineTuneRequest extends VAEGenerateRequest {
  finetune_epochs: number;
  finetune_batch_size: number;
  finetune_learning_rate: number;
  checkpoint_out?: string;
}

export interface VAEGenerateAndFineTuneResponse {
  status: string;
  generation: {
    n_samples: number;
    shape: [number, number];
    gesture_label: number;
    model_loaded: boolean;
    model_load_error?: string | null;
  };
  finetune: {
    status: string;
    samples_used: number;
    epochs: number;
    initial_loss: number | null;
    final_loss: number | null;
    checkpoint_saved_to: string;
  };
}

export interface GestureEvent {
  type: "gesture";
  gesture: string;
  confidence: number;
  timestamp: number;
  source?: string;
}
