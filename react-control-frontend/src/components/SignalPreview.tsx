import { useEffect, useRef } from "react";
import type { SignalMatrix } from "../types/api";
import { SIGNAL_CHANNELS, SIGNAL_TIMESTEPS } from "../utils/signal";

interface SignalPreviewProps {
  signal: SignalMatrix;
  width?: number;
  height?: number;
}

export function SignalPreview({ signal, width = 800, height = 300 }: SignalPreviewProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas || !signal || signal.length !== SIGNAL_CHANNELS) return;

    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Clear canvas
    ctx.clearRect(0, 0, width, height);
    
    // Draw background
    ctx.fillStyle = "#1e1e1e";
    ctx.fillRect(0, 0, width, height);

    // Compute dynamic min/max bounds based on the signal data
    let maxVal = -Infinity;
    let minVal = Infinity;
    for (const channel of signal) {
      for (const val of channel) {
        if (val > maxVal) maxVal = val;
        if (val < minVal) minVal = val;
      }
    }
    
    // Ensure a minimum visual range so absolute silence isn't blown up into massive noise
    if (maxVal - minVal < 0.0001) {
      const mid = (maxVal + minVal) / 2 || 0;
      maxVal = mid + 0.0005;
      minVal = mid - 0.0005;
    }

    const padding = (maxVal - minVal) * 0.1;
    const maxValue = maxVal + padding; 
    const minValue = minVal - padding;
    const valueRange = maxValue - minValue;

    const channelHeight = height / SIGNAL_CHANNELS;

    ctx.lineWidth = 1.5;

    // Draw channels
    signal.forEach((channel, i) => {
      // Different color for each channel
      const hue = (i * 360) / SIGNAL_CHANNELS;
      ctx.strokeStyle = `hsl(${hue}, 80%, 65%)`;

      const yOffset = i * channelHeight;
      const centerY = yOffset + channelHeight / 2;

      ctx.beginPath();
      // Draw 0-line for reference
      ctx.moveTo(0, centerY);
      ctx.lineTo(width, centerY);
      ctx.strokeStyle = "rgba(255, 255, 255, 0.1)";
      ctx.stroke();

      // Start actual signal path
      ctx.strokeStyle = `hsl(${hue}, 80%, 65%)`;
      ctx.beginPath();
      
      channel.forEach((value, t) => {
        const x = (t / SIGNAL_TIMESTEPS) * width;
        // Map value to local channel box [-1, 1] goes to [yOffset, yOffset + channelHeight]
        const normalized = (value - minValue) / valueRange; // 0..1
        // Invert Y axis
        const y = yOffset + channelHeight * (1 - normalized);

        if (t === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      });
      ctx.stroke();
      
      // Label
      ctx.fillStyle = "rgba(255, 255, 255, 0.6)";
      ctx.font = "10px monospace";
      ctx.fillText(`CH${i}`, 5, yOffset + 12);
    });
  }, [signal, width, height]);

  return (
    <div style={{ overflowX: "auto", border: "1px solid var(--border-color)", borderRadius: "var(--radius)" }}>
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        style={{ display: "block", backgroundColor: "#1e1e1e", maxWidth: '100%', height: "auto" }}
      />
    </div>
  );
}
