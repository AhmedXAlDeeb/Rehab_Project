# Digital Twin Review Summary for EMG-Driven Prosthetic Control (Digital Digit - DD)

## 1) Why an EMG-Based Patient Digital Twin Is Significant for Control Enhancement

Building a patient-specific digital twin from acquired EMG data is strategically important for DD because it directly improves control quality before physical prosthesis fitting.

In this project, the digital twin is not only a 3D hand model. It is a personalized, data-coupled system that links:
- residual-limb EMG patterns,
- AI intent decoding,
- and real-time prosthetic behavior in simulation.

This gives major control advantages:

1. Better command decoding and lower ambiguity:
By mapping each patient's EMG activation signatures to intended grasps/motions, the model learns the patient's true neuromuscular patterns instead of relying on generic mappings.

2. Safer and faster controller tuning before hardware:
Control thresholds, class sets, and confidence logic can be tuned in simulation first, reducing trial-and-error burden in clinic.

3. Pre-fitting feasibility assessment:
The team can test whether a patient can reliably control selected grasp classes before expensive hardware decisions.

4. Reduced frustration and improved learning:
Visual closed-loop feedback (muscle intent -> virtual hand response) supports motor learning and calibration quality.

5. Foundation for adaptive control over time:
As new EMG sessions are collected, the twin can be updated, supporting continual personalization and robustness.

In short, the EMG-based digital twin is the control development environment for DD, enabling data-driven personalization, verification, and adaptation.

---

## 2) Definition of Digital Twin (for this project)

A digital twin is a dynamic digital representation of a physical system that stays synchronized with real-world data and is used for monitoring, simulation, prediction, and optimization.

For DD, the physical system is the amputee residual-limb plus intended prosthetic control behavior. The digital twin includes:
- EMG signal state (windowed multi-channel muscle activity),
- intent model state (classifier outputs and confidence),
- prosthetic state (joint/gesture state in simulation),
- and performance state (latency, accuracy, consistency, task outcomes).

So the DD twin is an actively updated control twin, not only a static CAD model.

---

## 3) Summary of Similar Projects from the Provided PDFs

## 3.1 Wu et al. (2024) - Digital Twin for Amputees: Bidirectional Interaction + CNN
Source PDF: resources/research/wu-et-al-2024-digital-twin-for-amputees-a-bidirectional-interaction-modeling-and-prototype-with-convolutional-neural.pdf

What they did:
- Built a simplified bidirectional digital twin setup using EMG + VR + ML + API + servo actuation.
- Compared SVM and 1D-CNN for EMG classification.
- Implemented near real-time data flow between sensing and actuation.

Reported outcomes (pilot):
- 1D-CNN outperformed SVM in their binary task.
- Very high reported metrics in pilot setup.

Most relevant value for DD:
- Confirms feasibility of EMG->ML->digital/physical response loop.
- Supports using 1D temporal CNN for EMG intent decoding.

Key limitations noted in that work:
- Very small pilot sample and simplified binary classification.
- Able-bodied participants only in the pilot context.
- Limited task complexity versus multi-grasp real-world prosthetic control.

## 3.2 Cellupica et al. (Algorithms 2024) - Interactive Digital Twin in VR for Sensorized Upper-Limb Prosthesis Training
Source PDF: resources/research/algorithms-17-00035.pdf

What they did:
- Developed a full VR training environment around a sensorized upper-limb prosthesis digital twin.
- Integrated physical twin and digital twin with real-time communication paths.
- Focused strongly on immersive training tasks and usability.

Most relevant value for DD:
- Strong reference for training protocol design, virtual tasks, and user adaptation workflow.
- Demonstrates the benefit of combining multibody simulation and interactive VR feedback for pre-use training.

Key limitations relative to DD goals:
- Greater focus on training environment integration than deep patient-specific EMG personalization across many classes.
- Does not fully solve cross-session, cross-patient generalization in amputee intent decoding.

## 3.3 Advanced Research Directions for AI-Powered Smart Prosthetics (concept synthesis)
Source PDF: resources/research/Advanced Research Directions for AI-Powered Smart Prosthetics.pdf

What it emphasizes:
- Digital twins for virtual prototyping of control strategies before physical trials.
- Sim-to-real adaptation and RL in twin environments.
- Multi-modal sensing (EMG, IMU, pressure, vision) and world-model style predictive control.
- VR-based training and therapist analytics loops.

Most relevant value for DD:
- Supports extending EMG-only control toward multi-modal context-aware control.
- Reinforces simulation-first tuning and adaptive learning strategy.

Key limitation:
- Primarily direction-setting and concept integration rather than a validated full clinical pipeline.

## 3.4 Ahn et al. (Bioengineering 2024) - Medical Digital Twin via Reduced-Order Modeling
Source PDF: resources/research/bioengineering-11-00084.pdf

What they did:
- Built a digital twin for implant planning using parametric reduced-order modeling with real-time stress estimation.
- Integrated model outputs into clinical decision support visualization.

Most relevant value for DD:
- Demonstrates how reduced-order methods can enable real-time clinical decision support from complex models.
- Useful analogy for simplifying high-dimensional EMG-control optimization into deployable tools.

Key limitation for DD context:
- Different medical domain (implant planning), not EMG-driven upper-limb intent control.

## 3.5 Zhou et al. (2026) - Digital Twin AI survey (LLMs to world models)
Source PDF: resources/research/2601.01321v1.pdf

What it contributes:
- A broad AI-driven digital twin lifecycle framework: modeling, mirroring, intervening, autonomous management.
- Highlights transition from passive simulation to intelligent adaptive twins.

Most relevant value for DD:
- Provides a systems-level architecture lens for roadmap planning (from current classifier loop toward predictive and semi-autonomous adaptation).

Key limitation for immediate implementation:
- It is a broad cross-domain survey, not a prosthetic control implementation protocol.

## 3.6 Patiniott et al. (Applied Sciences 2025) - Ontology-Driven Cyber-Physical Prosthesis Service System
Source PDF: resources/research/applsci-15-12637-v2.pdf

What they did:
- Implemented an ontology-driven cyber-physical prosthesis service system (adProLiSS) for personalized and adaptive aftercare.
- Integrated embedded sensing, semantic reasoning, and digital-twin-mediated user feedback.
- Evaluated with 26 participants across user, clinical, and engineering groups.

Most relevant value for DD:
- Strong blueprint for integrating technical control data with clinical workflow and long-term service adaptation.
- Demonstrates how digital twins can support not only control but also care continuity, multidisciplinary collaboration, and decision support.

Key limitations relative to DD core objective:
- Main contribution is service architecture and semantic aftercare logic, not detailed low-latency EMG intent decoding benchmarks.

## 3.7 Yao - Pressure Simulation and Comfort Prediction for 3D-Printed Prosthetic Socket Interface
Source: user-provided abstract text in request

What this work presents:
- A digital twin workflow focused on socket-residual-limb interface mechanics.
- Residual-limb geometry acquisition via 3D scanning, nonlinear hyperelastic tissue modeling, and finite element simulation of donning/loading.
- Experimental validation using thin-film pressure sensor arrays and model calibration.
- Regression mapping from pressure features to subjective comfort scores.

Most relevant value for DD:
- Shows a closed-loop "simulation-measurement" approach for predicting comfort and reducing physical fitting iterations.
- Adds an essential biomechanical perspective that complements EMG control modeling.

Key limitations relative to DD core objective:
- Focused on socket/interface pressure and comfort, not high-dimensional intention decoding or real-time multi-grasp control.

## 3.8 Pizzolato et al. (Frontiers in Neurorobotics 2019) - Neuromusculoskeletal Modeling-Based Prostheses
Source PDF: resources/research/fnbot-13-00097.pdf

What they reviewed/proposed:
- Integration of personalized real-time neuromusculoskeletal (NMS) models with rehabilitation prostheses, FES, exoskeletons, and assistive robotics.
- Use of NMS models for optimizing stimulation strategies, improving safety monitoring, tracking functional recovery, and providing augmented feedback.

Most relevant value for DD:
- Provides theoretical and translational support for patient-specific physiological models as the foundation for advanced rehabilitation control.
- Reinforces the need to move beyond oversimplified control mappings toward personalized biomechanical-neural representations.

Key limitations relative to DD deployment:
- Broad neurorehabilitation narrative scope (including SCI), not a direct implementation of upper-limb amputee EMG digital twin with Ninapro-style pipelines.

---

## 4) Literature Gap (What is still missing)

Based on the reviewed PDFs and your project scope, the main gap is:

There is still no widely validated, end-to-end, patient-specific EMG digital twin pipeline for upper-limb amputees that jointly delivers:
- high-fidelity intent decoding across clinically relevant multi-grasp classes,
- real-time low-latency closed-loop simulation,
- robust adaptation across sessions/day-to-day drift,
- and clear pre-fitting decision support for clinicians.

More specific unresolved gaps:

1. Generalization gap:
Many studies are pilot-scale, binary/small-class, or non-amputee-heavy datasets.

2. Longitudinal robustness gap:
Few pipelines show stability against electrode shift, fatigue, sweat, and day-to-day neuromuscular variability.

3. Control-to-outcome gap:
High classification metrics do not always translate to better task completion and functional usability.

4. Personalization-at-scale gap:
Methods for fast per-patient adaptation while preserving generalized priors are still immature.

5. Clinical decision gap:
Limited standardized outputs that help clinicians choose control complexity, mapping strategy, and training dose before fabrication.

6. Interface-comfort and control integration gap:
Most works specialize in either (a) biomechanical socket/interface physics (fit, pressure, comfort) or (b) intention decoding/control. Few provide a unified digital twin that jointly optimizes both.

DD can directly target these gaps by combining Ninapro pretraining, amputee fine-tuning, digital twin task metrics, and clinician-facing recommendations.

---

## 4.1 General Interpretation: Digital Twin Covers Both Interface Physics and Control

Across the reviewed papers, the digital twin should be interpreted as a two-axis system rather than only a control simulator:

1. Shape/interface physics axis:
- Captures geometry and mechanics of residual limb, socket, and contact interface.
- Targets pressure distribution, stress hotspots, fit quality, and comfort prediction.
- Typical methods: 3D scanning, CAD personalization, finite element analysis, sensor-based calibration.

2. Control/intelligence axis:
- Captures neuromuscular intent, movement decoding, virtual/physical actuation, and adaptation.
- Targets accuracy, latency, robustness, and functional task success.
- Typical methods: EMG preprocessing, CNN/LSTM models, VR interaction, real-time closed-loop inference.

For DD, this implies a practical roadmap:
- Near-term core: prioritize the control axis (EMG -> intent -> virtual prosthetic behavior).
- Planned extension: add interface-physics modules for socket comfort and fit optimization.
- Long-term goal: unified patient twin combining comfort-safe fit and high-quality control in one clinical decision pipeline.

---

## 5) How We Build the Digital Twin for the DD Use Case

## 5.0 Why We Are Doing the Digital Twin (Based on the Digital Twin AI Review)

Following the Digital Twin AI review (Zhou et al., 2026), a strong digital twin should move through four connected functions:
- modeling the physical system,
- mirroring it in real time,
- intervening through prediction/optimization,
- and progressively enabling more autonomous adaptation.

For DD, we are building the digital twin because it provides a practical bridge from raw EMG signals to safe, personalized, and clinically useful prosthetic control decisions before expensive hardware commitments.

In other words, the digital twin is not an extra visualization layer. It is the core engineering workflow for:
- translating patient EMG into controllable actions,
- testing and improving control policies safely in simulation,
- and producing evidence-based recommendations for clinicians.

## 5.0.1 Processes We Are Modeling and Their Direct Benefits

The table below states clearly what processes we model and why each one matters.

| Process being modeled in the twin | What we model in practice | Direct benefit |
|---|---|---|
| Residual-limb signal generation | Multi-channel EMG windows, feature dynamics, temporal patterns | Captures patient-specific intent signatures instead of generic assumptions |
| Intent decoding process | EMG -> class probabilities/confidence (CNN/CNN-LSTM) | Improves command reliability and reduces false activations |
| Prosthetic response process | Predicted intent -> virtual hand kinematics/gesture transitions | Lets us verify if decoded intent leads to functionally correct hand behavior |
| Human-in-the-loop training process | Repeated task trials with feedback (open/close, grasp switch, object tasks) | Speeds user learning and reduces frustration during calibration |
| Performance evolution process | Session-wise metrics: latency, per-class accuracy, confusion, consistency | Quantifies progress and supports objective tuning decisions |
| Adaptation/drift process | Changes across days (electrode shift, fatigue, signal variance) | Increases robustness for real-world use beyond one-time lab calibration |
| Clinical decision process | Mapping model outputs to suggested grasp set and thresholds | Provides clinicians with actionable pre-fitting recommendations |
| (Planned extension) Interface physics process | Socket-residual pressure/stress and comfort indicators | Balances high control performance with comfort and safety |

## 5.0.2 How DD Maps to the Four-Stage Digital Twin AI Lifecycle

Based on Zhou et al. (2026), DD aligns as follows:

1. Modeling:
- We model neuromuscular intent formation from EMG and, in future, interface biomechanics.

2. Mirroring:
- We synchronize current EMG state with a live virtual prosthetic state (real-time twin behavior).

3. Intervening:
- We use model outputs to optimize class mappings, thresholds, and training tasks that improve control outcomes.

4. Toward autonomous management:
- We progressively add adaptive updates (drift handling and personalization updates) while keeping clinician oversight.

This lifecycle framing explains both why DD needs a digital twin and how the system is expected to mature from simulation support to adaptive clinical intelligence.

## 5.0.3 Presentation-Aligned Process Map (L0-L5) and Control Enhancement Benefit

To align with your presentation, DD should be described as one pipeline where each layer contributes to control enhancement either directly or indirectly.

| Presentation layer | Process modeled in DD | How it enhances prosthetic control |
|---|---|---|
| L0 - Smartphone photogrammetry | Residual limb geometry reconstruction and metric calibration | Improves downstream personalization quality (electrode/socket placement assumptions become more patient-specific) |
| L1 - Socket/interface simulation | Pressure-contact mechanics and hotspot prediction | Reduces pain/discomfort that degrades EMG quality and training adherence, indirectly improving control stability |
| L2 - Contralateral bootstrap | Webcam-based intact-hand kinematics used to auto-label residual EMG | Speeds calibration and improves early decoder quality with less patient cognitive burden |
| L3 - Biological twin | EMG temporal decoding to intended kinematics/grasp intent | Core control enhancement: better intention decoding, lower confusion, improved responsiveness |
| L4 - Digital twin hand | Physics-based virtual prosthetic execution and grasp validation | Converts decoder output into measurable functional outcomes (stable grasp, task completion, latency) |
| L5 - RL therapist/co-adaptation | Session policy adaptation and overnight controller updates | Continuously improves control policy for each patient across sessions and fatigue/drift conditions |

This makes the DD narrative explicit: it is not only a digital representation tool; it is a control enhancement engine across acquisition, simulation, adaptation, and evaluation.

## 5.1 Twin Objective
Create a patient-specific digital twin that jointly supports:
- prosthetic control enhancement,
- interface comfort/safety modeling,
- pre-fitting evaluation,
- controller personalization,
- and rehabilitation training.

## 5.2 Core System Architecture

1. Sensing Layer:
- Multi-channel sEMG acquisition (and optional IMU later).

2. Signal Intelligence Layer:
- Preprocessing: bandpass, notch, rectification, windowing.
- Feature + sequence modeling (1D-CNN or CNN-LSTM).
- Output: intent class probabilities and confidence.

3. Twin State Layer:
- Stores synchronized states:
  - EMG latent/feature state,
  - intent state,
  - virtual hand kinematic state,
  - performance state.

4. Simulation/Interaction Layer:
- Real-time virtual hand response in Unity or MuJoCo.
- Task engine (grasp switch, hold, release, object interaction).

5. Adaptation Layer:
- Session calibration,
- confidence gating,
- online/periodic fine-tuning,
- drift detection.

6. Clinical Analytics Layer:
- Patient report: per-class accuracy, confusion profile, response latency, stability.
- Recommendation engine: suggested grasp set size and mapping changes.

## 5.3 Practical Build Phases

Phase A: Offline twin (dataset replay)
- Use Ninapro data to validate EMG->intent->virtual hand loop.
- Benchmark models and tune preprocessing.

Phase B: Subject-specific calibration twin
- Short calibration recording for new user.
- Transfer learning adaptation and threshold tuning.

Phase C: Real-time interactive twin
- Live EMG streaming with low-latency inference and visual feedback.
- Deploy structured rehab tasks and progression metrics.

Phase D: Decision-support and continuous learning
- Add clinician dashboard outputs.
- Update model periodically using approved session data.

## 5.4 Minimum Technical KPIs for DD

- End-to-end latency: target under 100 ms for responsive control.
- Practical control set performance: high reliability on core 6-10 grasps.
- Session consistency: reduced variance in repeated attempts.
- User-level improvement: measurable progress across sessions.

---

## 6) Suggested Positioning Statement for Your Report/Proposal

DD proposes a patient-specific EMG digital twin that transforms prosthetic control development from post-fitting trial-and-error into pre-fitting, data-driven personalization. By coupling residual-limb EMG modeling, AI intent decoding, and real-time virtual prosthesis interaction, the platform enables earlier control optimization, lower rehabilitation burden, and more confident clinical decisions before physical fabrication.

---

## 7) Short Conclusion

The reviewed literature supports the feasibility and value of EMG-integrated prosthetic digital twins, especially for simulation-first development and VR training. However, robust amputee-specific, multi-class, clinically actionable pipelines remain limited. DD can fill this gap by delivering an end-to-end EMG digital twin workflow centered on personalization, real-time control quality, and pre-fitting decision support.

---

## References (from provided PDFs)

- Wu, J., Jangid, V., and Park, J. (2024). Digital Twin for Amputees: A Bidirectional Interaction Modeling and Prototype with CNN.
- Cellupica, A., et al. (2024). An Interactive Digital-Twin Model for VR Environments to Train in the Use of a Sensorized Upper-Limb Prosthesis.
- Ahn, S., et al. (2024). Toward Digital Twin Development for Implant Placement Planning Using a Parametric Reduced-Order Model.
- Patiniott, N., et al. (2025). Design and Implementation of an Ontology-Driven Cyber-Physical Prosthesis Service System for Personalised and Adaptive Care.
- Zhou, R., et al. (2026). Digital Twin AI: Opportunities and Challenges from LLMs to World Models.
- Advanced Research Directions for AI-Powered Smart Prosthetics (provided summary document).
- Yao, J. Pressure simulation and comfort prediction of the interface between receiving cavity and residual limb of 3D-printed prostheses based on digital twins (user-provided abstract text).
- Pizzolato, C., et al. (2019). Neuromusculoskeletal Modeling-Based Prostheses for Recovery After Spinal Cord Injury. Frontiers in Neurorobotics, 13:97.

