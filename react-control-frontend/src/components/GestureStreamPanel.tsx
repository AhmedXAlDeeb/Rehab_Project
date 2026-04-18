import { useGestureWebSocket } from "../hooks/useGestureWebSocket";

export function GestureStreamPanel() {
  const { events, socketUrl, connectionLabel, clearEvents, lastSystemMessage } = useGestureWebSocket();

  return (
    <section className="card stream-card">
      <div className="row-between">
        <h2>Gesture Stream</h2>
        <span className={`status-badge ${connectionLabel}`}>{connectionLabel}</span>
      </div>

      <p className="muted">Listening on {socketUrl}. This panel updates when the simulator bridge broadcasts gestures.</p>

      {lastSystemMessage && (
        <div className="alert alert-warn">
          <strong>Last system message:</strong> {lastSystemMessage}
        </div>
      )}

      <div className="row-between">
        <h3>Recent Gestures ({events.length})</h3>
        <button type="button" className="ghost-button" onClick={clearEvents}>
          Clear
        </button>
      </div>

      {events.length === 0 ? (
        <div className="empty-state">No gesture events yet.</div>
      ) : (
        <ul className="events-list">
          {events.map((event) => (
            <li key={`${event.timestamp}-${event.gesture}`} className="event-item">
              <div className="event-title">{event.gesture}</div>
              <div className="event-meta">
                confidence: {event.confidence.toFixed(2)} | {new Date(event.timestamp).toLocaleTimeString()}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
