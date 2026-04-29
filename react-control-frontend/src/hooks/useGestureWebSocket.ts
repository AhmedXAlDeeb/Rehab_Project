import { useCallback, useEffect, useRef, useState } from "react";

import type { GestureEvent } from "../types/api";

const DEFAULT_WS_URL = "ws://localhost:8765";
const MAX_EVENTS = 30;
const RECONNECT_DELAY_MS = 1500;
const MAX_RECONNECT_ATTEMPTS = 100;

function parseGestureEvent(raw: unknown): GestureEvent | null {
  if (!raw || typeof raw !== "object") {
    return null;
  }

  const payload = raw as Record<string, unknown>;
  if (typeof payload.gesture !== "string") {
    return null;
  }

  const confidence =
    typeof payload.confidence === "number" && Number.isFinite(payload.confidence)
      ? payload.confidence
      : 1.0;
  const timestamp =
    typeof payload.timestamp === "number" && Number.isFinite(payload.timestamp)
      ? payload.timestamp
      : Date.now();

  return {
    type: "gesture",
    gesture: payload.gesture,
    confidence,
    timestamp,
    source: typeof payload.source === "string" ? payload.source : undefined,
  };
}

export function useGestureWebSocket() {
  const socketUrl = import.meta.env.VITE_WS_URL ?? DEFAULT_WS_URL;
  const [events, setEvents] = useState<GestureEvent[]>([]);
  const [videoFrame, setVideoFrame] = useState<string | null>(null);
  const [lastSystemMessage, setLastSystemMessage] = useState<string | null>(null);
  const [connectionLabel, setConnectionLabel] = useState<"idle" | "connecting" | "connected" | "closed">("idle");

  const socketRef = useRef<WebSocket | null>(null);
  const reconnectTimerRef = useRef<number | null>(null);
  const reconnectCountRef = useRef(0);

  useEffect(() => {
    let isActive = true;

    const connect = () => {
      if (!isActive) {
        return;
      }

      setConnectionLabel("connecting");
      const socket = new WebSocket(socketUrl);
      socketRef.current = socket;

      socket.onopen = () => {
        if (!isActive) {
          return;
        }
        reconnectCountRef.current = 0;
        setConnectionLabel("connected");
        setLastSystemMessage(`Connected to ${socketUrl}`);
        console.log("WebSocket connected to", socketUrl);
      };

      socket.onmessage = (event) => {
        if (!isActive) {
          return;
        }

        try {
          const payload = JSON.parse(String(event.data));
          
          if (payload && payload.type === "video_frame") {
            console.log("Video frame received, size:", payload.image?.length);
            setVideoFrame(payload.image);
            return;
          }

          const parsedEvent = parseGestureEvent(payload);
          if (parsedEvent) {
            setEvents((previous) => [parsedEvent, ...previous].slice(0, MAX_EVENTS));
            return;
          }

          if (payload && typeof payload === "object" && "status" in payload) {
            setLastSystemMessage(String((payload as { status: unknown }).status));
          } else {
            setLastSystemMessage("non-gesture message received");
          }
        } catch {
          setLastSystemMessage("invalid JSON message from socket");
        }
      };

      socket.onerror = (event) => {
        if (!isActive) {
          return;
        }
        console.error("WebSocket error:", event);
        setLastSystemMessage("socket error - check console for details");
      };

      socket.onclose = (event) => {
        if (!isActive) {
          return;
        }

        console.log("WebSocket closed:", event.code, event.reason);
        setConnectionLabel("closed");
        setLastSystemMessage(`Connection closed: ${event.code}`);
        reconnectCountRef.current += 1;

        if (reconnectCountRef.current <= MAX_RECONNECT_ATTEMPTS) {
          reconnectTimerRef.current = window.setTimeout(connect, RECONNECT_DELAY_MS);
        }
      };
    };

    connect();

    return () => {
      isActive = false;

      if (reconnectTimerRef.current !== null) {
        window.clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }

      if (socketRef.current) {
        socketRef.current.close();
        socketRef.current = null;
      }
    };
  }, [socketUrl]);

  const clearEvents = useCallback(() => {
    setEvents([]);
  }, []);

  return {
    socketUrl,
    events,
    videoFrame,
    connectionLabel,
    clearEvents,
    lastSystemMessage,
  };
}
