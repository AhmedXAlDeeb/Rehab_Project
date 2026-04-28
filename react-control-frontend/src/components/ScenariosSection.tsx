import { useState } from "react";

export function ScenariosSection() {
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const SCENARIOS = [
    { 
      id: 1, 
      title: "Scenario 1: Drinking from a Cup", 
      dbs: "Primary: DB3 | Secondary: DB2",
      desc: "The most fundamental ADL for amputees. DB3 gives real amputee EMG; DB2 pre-trains on a larger intact cohort." 
    },
    { 
      id: 2, 
      title: "Scenario 2: Writing with a Pen", 
      dbs: "Primary: DB2 | Secondary: DB3, DB8",
      desc: "DB8 explicitly labels tripod grip as a movement class, making it a perfect supplement for this precision scenario." 
    },
    { 
      id: 3, 
      title: "Scenario 3: Unlocking a Door", 
      dbs: "Primary: DB2 | Secondary: DB3",
      desc: "Simulates lateral key grip to pinch the key, followed by wrist pronation to lock and supination to unlock." 
    },
    { 
      id: 5, 
      title: "Scenario 5: Carrying a Bag", 
      dbs: "Primary: DB6 | Secondary: DB2 / DB3",
      desc: "Tests long-term stability. Involves reaching, hooking fingers for a snap grasp, and holding a static grip." 
    },
  ];

  const handleTriggerEndpoint = async (scenarioId: number, scenarioTitle: string) => {
    setToastMessage(`Starting ${scenarioTitle}...`);
    
    try {
      const response = await fetch(`http://localhost:8001/scenario/${scenarioId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        }
      });

      if (!response.ok) throw new Error("Failed to trigger scenario endpoint");
      
      const data = await response.json();
      setToastMessage(`Completed! Processed ${data.movements_processed} movements.`);
    } catch (error) {
      console.error(error);
      setToastMessage(`Error firing endpoint for: ${scenarioTitle}`);
    } finally {
      setTimeout(() => setToastMessage(null), 4000);
    }
  };

  return (
    <section style={{ marginTop: "2rem" }}>
      <div className="row-between">
        <div>
          <h2>Scenarios</h2>
          <p className="muted" style={{ marginBottom: 0 }}>
            Pre-configured testing sequences and edge cases based on ADLs.
          </p>
        </div>
        {toastMessage && (
          <span className="chip chip-primary">
            {toastMessage}
          </span>
        )}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))", gap: "1rem", marginTop: "1rem" }}>
        {SCENARIOS.map((s) => (
          <div key={s.id} className="card" style={{ display: "flex", flexDirection: "column", justifyContent: "space-between" }}>
            <div style={{ marginBottom: "1.5rem" }}>
              <h3 style={{ fontSize: "1.05rem", marginBottom: "0.25rem", color: "#1e293b" }}>{s.title}</h3>
              <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "#4f46e5", marginBottom: "0.75rem" }}>
                {s.dbs}
              </div>
              <p className="muted" style={{ fontSize: "0.85rem", lineHeight: "1.4" }}>{s.desc}</p>
            </div>
            <button
              type="button"
              className="primary-button"
              style={{ padding: "0.5rem", fontSize: "0.8rem", backgroundColor: "#1e293b" }}
              onClick={() => handleTriggerEndpoint(s.id, s.title)}
            >
              Start Scenario Sequence
            </button>
          </div>
        ))}
      </div>
    </section>
  );
}