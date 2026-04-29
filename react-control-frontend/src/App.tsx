import { useState, useEffect } from "react";

import { GestureStreamPanel } from "./components/GestureStreamPanel";
import { SignalSenderCard } from "./components/SignalSenderCard";
import { SignalUploadCard } from "./components/SignalUploadCard";
import { ScenariosSection } from "./components/ScenariosSection";
import { MujocoStreamTab } from "./components/MujocoStreamTab";
import type { UnifiedInferenceResult } from "./types/api";

function App() {
  const [lastInference, setLastInference] = useState<UnifiedInferenceResult | null>(null);
  const [theme, setTheme] = useState<"dark" | "light">(() => {
    const saved = localStorage.getItem("theme");
    return (saved as "dark" | "light") || "dark";
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  return (
    <div className="app-shell">
      <div className="app-backdrop" aria-hidden />

      <main className="app-main">
        <section className="hero-panel card">
          <div className="header-row">
            <div>
              <h1>Digital Digit</h1>
              <p>
                Prosthetic Control Interface - EMG signal classification, MuJoCo simulation monitoring, and gesture prediction.
              </p>
              <div className="chip-row">
                <span className="chip">/api -&gt; integration_service :8001</span>
                <span className="chip">/directapi -&gt; classification_service :8000</span>
                <span className="chip">ws://localhost:8765</span>
              </div>
            </div>
            <button className="theme-toggle" onClick={toggleTheme} aria-label="Toggle theme">
              {theme === "dark" ? (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <circle cx="12" cy="12" r="5" />
                  <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
                </svg>
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
                </svg>
              )}
            </button>
          </div>
        </section>

        {lastInference && (
          <section className="last-result card">
            <div className="chip-row">
              <span className="chip chip-primary">Predicted class {lastInference.predictedClass}</span>
              <span className="chip">Mode: {lastInference.mode}</span>
              {lastInference.mappedGesture && <span className="chip chip-secondary">Gesture: {lastInference.mappedGesture}</span>}
              {lastInference.websocketDelivery && <span className="chip">WS delivery: {lastInference.websocketDelivery}</span>}
            </div>
          </section>
        )}

        <section className="main-grid">
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <SignalSenderCard onInferenceComplete={setLastInference} />
            <SignalUploadCard onClassificationComplete={setLastInference} />
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
            <GestureStreamPanel />
            <MujocoStreamTab />
          </div>
        </section>

        <ScenariosSection />

      </main>
    </div>
  );
}

export default App;
