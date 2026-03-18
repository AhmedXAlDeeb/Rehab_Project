# Digital Digit (DD) - Focused Presentation

Only the essentials: Digital Twin definition, related works, and DD mechanism to achieve goals.

- Digital Twin
- Control Enhancement
- Interface Physics

---

## 1. Definition of Digital Twin (DD Context)

A digital twin is a dynamic digital representation of a physical system, continuously synchronized with real data and used for simulation, prediction, optimization, and decision support.

### Physical twin in DD
- Residual limb and EMG signal behavior
- Intended prosthetic movement and task goals
- Socket-residual interface biomechanics (pressure/fit)

### Digital twin in DD
- Signal state: EMG windows and temporal patterns
- Control state: intent decoding, confidence, adaptation
- Physics state: virtual hand-object interaction, interface pressure
- Outcome state: latency, success, consistency, comfort indicators

**Key point:** DD digital twin is dual-purpose: control enhancement + interface comfort/safety.

---

## 2. Related Works Summary

| Work | Main contribution | Value for DD | Limitation vs DD target |
|---|---|---|---|
| Wu et al. (2024) | EMG + CNN + bidirectional digital twin pilot | Supports EMG-to-intent loop feasibility | Small pilot, binary task, limited generalization |
| Cellupica et al. (2024) | VR training with interactive prosthesis twin | Strong training and usability framework | Less focus on deep patient-specific decoding robustness |
| Zhou et al. (2026) | 4-stage AI digital twin lifecycle | Architecture roadmap for DD maturity | Survey-level, not prosthetic control implementation |
| Patiniott et al. (2025) | Ontology-driven adaptive aftercare ecosystem | Clinical workflow and long-term adaptation model | Not centered on low-latency EMG control benchmarking |
| Yao (interface DT) | Socket pressure simulation + comfort prediction | Direct model for fit/comfort optimization | Limited control decoding and task-level control metrics |
| Pizzolato et al. (2019) | Neuromusculoskeletal personalized modeling review | Supports personalized physiological control models | Broad neurorehab scope, not DD end-to-end pipeline |

**Gap identified:** few systems unify control intelligence and interface physics in one patient-specific twin.

---

## 3. DD Mechanism: How the Twin Achieves Its Goals

### L0-L5 pipeline
1. L0 Photogrammetry -> residual limb geometry
2. L1 Interface simulation -> pressure hotspot prediction
3. L2 Contralateral bootstrap -> auto-labeled EMG calibration
4. L3 Biological twin -> EMG decoding to intended kinematics
5. L4 Digital twin hand -> physics-based execution + grasp validation
6. L5 RL therapist/co-adaptation -> session planning + overnight control updates

### Goal A: Enhance Control
- Higher decode reliability
- Lower latency and confusion
- Better task success and consistency

### Goal B: Improve Fit/Safety
- Predict pressure hotspots before fabrication
- Reduce pain-driven EMG degradation
- Support comfort-aware prescriptions

### Goal C: Adaptive Rehab
- Personalized session progression
- Drift/fatigue-aware updates
- Clinician decision support

---

## Take-Home Message

DD uses a single integrated digital twin pipeline to connect measurement, interface physics, EMG intelligence, virtual prosthetic physics, and adaptive training.

This is how DD turns digital twin technology into a practical engine for prosthetic control enhancement and better rehabilitation outcomes.
