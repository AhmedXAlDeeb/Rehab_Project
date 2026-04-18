import { AxiosError } from "axios";
import { z } from "zod";

import { directApiClient, integrationApiClient } from "./httpClients";
import { hasValidSignalShape } from "../utils/signal";
import type {
  ForwardSignalResponse,
  InferenceMode,
  PredictResponse,
  SignalMatrix,
  UnifiedInferenceResult,
} from "../types/api";

const forwardSignalResponseSchema = z.object({
  status: z.string(),
  pipeline_result: z.object({
    ai_predicted_id: z.number(),
    mapped_gesture: z.string(),
    websocket_delivery: z.string(),
  }),
});

const predictResponseSchema = z.object({
  predicted_class: z.number(),
  status: z.string(),
});

export class InferenceApiError extends Error {
  statusCode?: number;

  constructor(message: string, statusCode?: number) {
    super(message);
    this.name = "InferenceApiError";
    this.statusCode = statusCode;
  }
}

function getErrorMessage(detail: unknown): string {
  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((entry) => {
        if (typeof entry === "string") {
          return entry;
        }
        if (entry && typeof entry === "object" && "msg" in entry) {
          return String((entry as { msg?: unknown }).msg);
        }
        return "invalid request payload";
      })
      .join("; ");
  }

  if (detail && typeof detail === "object" && "detail" in detail) {
    return getErrorMessage((detail as { detail: unknown }).detail);
  }

  return "unexpected backend error";
}

function normalizeApiError(error: unknown): InferenceApiError {
  if (error instanceof InferenceApiError) {
    return error;
  }

  if (error instanceof AxiosError) {
    const statusCode = error.response?.status;
    const detail = error.response?.data;
    const message = getErrorMessage(detail ?? error.message);
    return new InferenceApiError(message, statusCode);
  }

  if (error instanceof z.ZodError) {
    return new InferenceApiError(`Response parsing failed: ${error.issues.map((i) => i.message).join(", ")}`);
  }

  if (error instanceof Error) {
    return new InferenceApiError(error.message);
  }

  return new InferenceApiError("Unknown error during inference request");
}

interface SendSignalArgs {
  mode: InferenceMode;
  signal: SignalMatrix;
}

export async function sendSignalForInference(args: SendSignalArgs): Promise<UnifiedInferenceResult> {
  if (!hasValidSignalShape(args.signal)) {
    throw new InferenceApiError("Signal must be a 12x400 matrix");
  }

  try {
    if (args.mode === "integration") {
      const response = await integrationApiClient.post<ForwardSignalResponse>("/forward_signal", {
        signal: args.signal,
      });
      const parsed = forwardSignalResponseSchema.parse(response.data);
      return {
        mode: "integration",
        predictedClass: parsed.pipeline_result.ai_predicted_id,
        mappedGesture: parsed.pipeline_result.mapped_gesture,
        websocketDelivery: parsed.pipeline_result.websocket_delivery,
        raw: parsed,
      };
    }

    const response = await directApiClient.post<PredictResponse>("/predict", {
      signal: args.signal,
    });
    const parsed = predictResponseSchema.parse(response.data);
    return {
      mode: "direct",
      predictedClass: parsed.predicted_class,
      raw: parsed,
    };
  } catch (error) {
    throw normalizeApiError(error);
  }
}
