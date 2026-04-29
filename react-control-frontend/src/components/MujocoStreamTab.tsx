import { useGestureWebSocket } from "../hooks/useGestureWebSocket";

export function MujocoStreamTab() {
  const { connectionLabel, videoFrame, lastSystemMessage } = useGestureWebSocket();

  const getStatusMessage = () => {
    if (videoFrame) return null;
    
    switch (connectionLabel) {
      case "idle":
        return "Not connected";
      case "connecting":
        return "Connecting to simulator...";
      case "connected":
        return "Waiting for video stream...";
      case "closed":
        return "Connection lost - ensure ws_streamer.py is running";
      default:
        return "Unknown state";
    }
  };

  const statusMessage = getStatusMessage();

  return (
    <section className="card">
      <div className="row-between">
        <h2>MuJoCo Simulator Live View</h2>
        <span className={`chip ${connectionLabel === "connected" ? "chip-primary" : ""}`}>
          {connectionLabel}
        </span>
      </div>
      <p className="muted">
        Headless backend simulator rendering frames and streaming over WebSocket. 
        Run <code>python viz/ws_streamer.py</code> to see the MyoSuite hand simulation live.
      </p>

      {lastSystemMessage && connectionLabel !== "connected" && (
        <div className="alert alert-warn" style={{ marginBottom: "0.5rem" }}>
          {lastSystemMessage}
        </div>
      )}

      <div style={{ display: "flex", justifyContent: "center", minHeight: "480px", backgroundColor: "#000", borderRadius: "8px", overflow: "hidden", marginTop: "1rem" }}>
        {videoFrame ? (
          <img 
            src={videoFrame} 
            alt="MuJoCo Live Stream" 
            style={{ objectFit: "contain", width: "100%", maxHeight: "480px" }} 
          />
        ) : (
          <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", color: "#888", gap: "0.5rem" }}>
            <div className="spinner" style={{ width: "32px", height: "32px", border: "3px solid #333", borderTopColor: "var(--primary)", borderRadius: "50%", animation: "spin 1s linear infinite" }} />
            <span>{statusMessage}</span>
          </div>
        )}
      </div>
    </section>
  );
}
