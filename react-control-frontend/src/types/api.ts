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

export interface GestureEvent {
  type: "gesture";
  gesture: string;
  confidence: number;
  timestamp: number;
  source?: string;
}
