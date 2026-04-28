import { useState } from "react";
import { ID_TO_GESTURE_MAP, SCENARIOS } from "../utils/scenarios";
import { createMockSignal } from "../utils/signal";
import { sendSignalForInference, generateAndFineTuneClassifier } from "../services/inferenceApi";

interface TaskResult {
  groundTruth: number;
  predicted: number | null;
  matched: boolean | null;
  isPredicting: boolean;
  isFineTuning: boolean;
  fineTuneResult: string | null;
}

export function ScenarioTrainingCard() {
  const [selectedScenarioIdx, setSelectedScenarioIdx] = useState<number>(0);
  const [tasks, setTasks] = useState<TaskResult[]>([]);
  const [isRunning, setIsRunning] = useState(false);

  const handleSelectScenario = (idx: number) => {
    setSelectedScenarioIdx(idx);
    setTasks(SCENARIOS[idx].motions.map(m => ({
      groundTruth: m,
      predicted: null,
      matched: null,
      isPredicting: false,
      isFineTuning: false,
      fineTuneResult: null,
    })));
  };

  // init first load
  if (tasks.length === 0) {
    handleSelectScenario(0);
  }

  const runScenario = async () => {
    setIsRunning(true);
    // Reset state
    const newTasks = SCENARIOS[selectedScenarioIdx].motions.map(m => ({
      groundTruth: m,
      predicted: null,
      matched: null,
      isPredicting: false,
      isFineTuning: false,
      fineTuneResult: null,
    }));
    setTasks(newTasks);

    for (let i = 0; i < newTasks.length; i++) {
        setTasks(prev => {
            const copy = [...prev];
            copy[i].isPredicting = true;
            return copy;
        });

        // The classification service takes this scenario and applies
        // classification against integration_service forward_signal
        try {
            // Generating "fake" signal but with randomness so it might get misclassified
            // Using a unique seed to add variance
            const signal = createMockSignal(Date.now() + i * 100);
            const res = await sendSignalForInference({
              mode: "integration",
              signal
            });
            
            const predictedId = res.predictedClass;
            const matched = predictedId === newTasks[i].groundTruth;

            setTasks(prev => {
                const copy = [...prev];
                copy[i].isPredicting = false;
                copy[i].predicted = predictedId;
                copy[i].matched = matched;
                return copy;
            });
        } catch (e: any) {
             setTasks(prev => {
                const copy = [...prev];
                copy[i].isPredicting = false;
                copy[i].fineTuneResult = "Error requesting prediction: " + e.message;
                return copy;
            });
        }

        // small delay for visual effect
        await new Promise((r) => setTimeout(r, 1000));
    }
    
    setIsRunning(false);
  };

  const handleFineTune = async (index: number) => {
      const task = tasks[index];
      if (task.isFineTuning) return;

      setTasks(prev => {
          const copy = [...prev];
          copy[index].isFineTuning = true;
          copy[index].fineTuneResult = null;
          return copy;
      });

      try {
          const response = await generateAndFineTuneClassifier({
             subject_idx_0based: 0,
             gesture_0based: task.groundTruth, 
             flags: {
                 fatigue: 0,
                 electrode_quality: 1,
                 session_idx_norm: 0,
                 amputation: 0,
             },
             n_samples: 30, // Generate small synthetic data to fine tune
             finetune_epochs: 2,
             finetune_batch_size: 16,
             finetune_learning_rate: 1e-4
          });

          setTasks(prev => {
             const copy = [...prev];
             copy[index].isFineTuning = false;
             copy[index].fineTuneResult = `Success! Generated ${response.generation.n_samples} samples. Final Loss: ${response.finetune.final_loss?.toFixed(3)}`;
             return copy;
         });
      } catch (err: any) {
         setTasks(prev => {
             const copy = [...prev];
             copy[index].isFineTuning = false;
             copy[index].fineTuneResult = `Failed: ${err.message}`;
             return copy;
         });
      }
  };

  return (
    <section className="card signal-card">
      <div className="row-between">
        <h2>Scenario Digital Twin Pipeline</h2>
        <span className="chip chip-primary">Integration Mode</span>
      </div>

      <p className="muted">
        Pick a scenario below. The system sweeps through the known ground truth motions, sending each to the Classification service (which drops it onto the 3D model). If an output doesn't match the ground truth, click "Fix with VAE" to generate synthetic data for the true motion and fine-tune instantly.
      </p>

      <div style={{ marginBottom: "1rem" }}>
        <label style={{ display: "block", marginBottom: "0.5rem" }}>Select Scenario:</label>
        <select 
          value={selectedScenarioIdx} 
          onChange={e => handleSelectScenario(Number(e.target.value))}
          disabled={isRunning}
          style={{ padding: "0.5rem", width: "100%", maxWidth: "300px", borderRadius: "4px" }}
        >
          {SCENARIOS.map((s, idx) => (
            <option key={idx} value={idx}>{s.name}</option>
          ))}
        </select>
        
        <button 
           className="primary-button" 
           onClick={runScenario} 
           disabled={isRunning}
           style={{ marginLeft: "1rem" }}
        >
          {isRunning ? "Running Scenario..." : "Start Scenario"}
        </button>
      </div>

       <div className="result-box">
         <table style={{ width: "100%", textAlign: "left", borderCollapse: "collapse" }}>
           <thead>
             <tr style={{ borderBottom: "1px solid #ccc" }}>
               <th style={{ padding: "0.5rem" }}>Ground Truth</th>
               <th style={{ padding: "0.5rem" }}>Predicted</th>
               <th style={{ padding: "0.5rem" }}>Status</th>
               <th style={{ padding: "0.5rem" }}>Digital Twin Action</th>
             </tr>
           </thead>
           <tbody>
             {tasks.map((task, i) => (
                <tr key={i} style={{ borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
                  <td style={{ padding: "0.5rem" }}>{ID_TO_GESTURE_MAP[task.groundTruth]}</td>
                  <td style={{ padding: "0.5rem" }}>
                    {task.isPredicting ? "Predicting..." : task.predicted !== null ? ID_TO_GESTURE_MAP[task.predicted] : "--"}
                  </td>
                  <td style={{ padding: "0.5rem" }}>
                    {task.matched === true && <span style={{ color: "#4caf50", fontWeight: "bold" }}>MATCH</span>}
                    {task.matched === false && <span style={{ color: "#f44336", fontWeight: "bold" }}>MISMATCH</span>}
                    {task.matched === null && "--"}
                  </td>
                  <td style={{ padding: "0.5rem" }}>
                     {task.matched === false && (
                         <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
                            <button 
                               className="ghost-button" 
                               onClick={() => handleFineTune(i)}
                               disabled={task.isFineTuning}
                               style={{ padding: "0.2rem 0.5rem", fontSize: "0.85rem", width: "fit-content" }}
                            >
                               {task.isFineTuning ? "Synthesizing & Tuning..." : "Fix via VAE Synthetic"}
                            </button>
                            {task.fineTuneResult && <small style={{ fontSize: "0.75rem", color: task.fineTuneResult.startsWith("Success") ? "#4caf50" : "#f44336"}}>{task.fineTuneResult}</small>}
                         </div>
                     )}
                     {task.matched === true && <small style={{ color: "#aaa" }}>No action needed</small>}
                  </td>
                </tr>
             ))}
           </tbody>
         </table>
       </div>

    </section>
  );
}