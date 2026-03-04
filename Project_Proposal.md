# Project Proposal: SimHand — AI-Powered Digital Twin for Prosthetic Hand Control & Training

---

## 1. Executive Summary

**SimHand** is a focused, two-phase simulation project that uses the **Ninapro database** — the world's largest public multimodal dataset for prosthetic hand research (180+ acquisitions from intact subjects and transradial amputees) — to build an AI-powered digital twin of a prosthetic hand.

- **Phase 1 — Residual Limb Modeling:** Build a functional digital model of the amputee's forearm by analyzing their sEMG muscle activation patterns — creating a personalized "muscle map" that characterizes what the residual limb *can do*. Train a CNN classifier on Ninapro sEMG data to decode hand movement intent from forearm muscle signals.
- **Phase 2 — Prosthetic Hand Digital Twin:** Use the trained classifier to drive a real-time 3D prosthetic hand on screen. The amputee's forearm muscle signals control the virtual hand, enabling pre-fitting evaluation, control optimization, and rehabilitation training — before a physical prosthetic hand is fabricated.

The two phases flow directly from each other: Phase 1 produces the AI brain (EMG → intent), Phase 2 gives it a body (the digital twin hand that responds).

---

## 2. The Core Problem

### 2.1 Problem Statement

There are **>2.3 million amputees in the U.S.**, with approximately **41,000 upper-limb amputations per year** globally. Despite advances in myoelectric prosthetic hands, major problems persist:

| Pain Point | Current Reality |
|---|---|
| **Poor EMG control** | Current myoelectric hands offer only **2-6 control modes** (open/close, rotate). The hand has **20+ DOF** but the controller can barely distinguish a few commands. Pattern recognition accuracy degrades outside lab conditions. |
| **No way to test before buying** | There is no way to test how well an amputee can control a specific prosthetic hand *before* it is fabricated and fitted. Mismatches are discovered only after delivery — at a cost of **$20,000–$100,000** per device. |
| **30-50% abandonment rate** | The highest of any prosthetic category. Primary reasons: unintuitive control, frustration, and lengthy training (Biddiss & Chau, 2007). |
| **Tedious rehabilitation** | Learning to control a myoelectric hand requires **weeks to months** of repetitive in-clinic training with no visual feedback of what the hand would actually do. |
| **Employment impact** | **78% of amputees stop working within 2 years**; **29% switch occupations**; **34% say they would have kept working with better prosthetic adjustments** (Schoppen et al., 2001; Lee et al., 2022). |

### 2.2 Root Cause

The root cause is simple: **amputees cannot see or practice with a prosthetic hand before they get one**. There is no digital twin that:

1. Maps the amputee's residual muscle capabilities (what movements can their forearm signals actually produce?)
2. Shows a prosthetic hand responding to those signals in real-time (so they can practice and clinicians can optimize)

**This project solves both.**

---

## 3. Available Data — Ninapro Database

All project work is built directly on the **Ninapro datasets** — publicly available, well-documented, and specifically designed for prosthetic hand research:

| Dataset | Subjects | Movements | EMG Setup | Modalities | Our Use |
|---------|----------|-----------|-----------|------------|---------|
| **DB1** | 27 intact | 52 | 10 Otto Bock | sEMG, kinematic | Pre-training the CNN |
| **DB2** | 40 intact | 49 | 12 Delsys Trigno | sEMG, kinematic, inertial, force | Pre-training + force-aware models |
| **DB3** | **11 amputees** | 49 | 12 Delsys Trigno | sEMG, inertial | **Primary amputee training/testing** |
| DB4 | 10 intact | 52 | 12 Cometa | sEMG, kinematic | Cross-sensor generalization |
| DB5 | 10 intact | 52 | 2 Thalmic Myo (16 ch) | sEMG, inertial | Low-cost sensor feasibility |
| **DB6** | 10 intact | 7 | 14 Delsys Trigno | sEMG, inertial, eye tracking | Day-to-day stability testing |
| **DB7** | 20 intact + **2 amputees** | 6 | 12 Delsys Trigno | sEMG, inertial | Transfer learning validation |
| **DB8** | 10 intact + **2 amputees** | 9 | 16 Delsys Trigno | sEMG, kinematic | Finger-level regression |
| DB9 | 77 intact | 40 | — | sEMG, kinematic | Kinematics reference |
| **DB10** | 30 intact + **15 amputees** | 10 | 12 Delsys Trigno | sEMG, IMU, eye tracking, behavioral, clinical | Multimodal fusion |

**Total amputee data available:** 11 (DB3) + 2 (DB7) + 2 (DB8) + 15 (DB10) = **30 amputee subjects** across 4 datasets.

---

## 4. Proposed Solution — Two Phases

### 4.1 System Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                       SimHand Platform                         │
│                                                                │
│  ┌─────────────────────┐        ┌─────────────────────────┐   │
│  │      PHASE 1        │        │       PHASE 2           │   │
│  │  Residual Limb      │───────▶│  Prosthetic Hand        │   │
│  │  Modeling & AI      │ feeds  │  Digital Twin            │   │
│  │                     │ into   │                          │   │
│  │  • sEMG analysis    │        │  • 3D hand on screen    │   │
│  │  • Muscle mapping   │        │  • Responds to sEMG     │   │
│  │  • CNN classifier   │        │  • Grasp simulation     │   │
│  │  • Movement intent  │        │  • Training tasks       │   │
│  └─────────┬───────────┘        └────────────┬────────────┘   │
│            │                                  │                │
│            ▼                                  ▼                │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              Ninapro Database (DB1–DB10)               │    │
│  │     180+ acquisitions: sEMG, kinematics, IMU, force   │    │
│  └────────────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────────┘
```

---

### 4.2 Phase 1 — Residual Limb Modeling & AI Movement Classifier

**Objective:** Build a functional model of the amputee's residual forearm by analyzing their sEMG patterns, and train an AI that can decode hand movement intent from those signals.

**What this phase produces:** A trained CNN model that takes multi-channel sEMG input and outputs the intended hand movement (out of up to 49 movement classes).

#### Step 1: sEMG Signal Processing & Feature Extraction

- Load Ninapro sEMG data (12-channel Delsys Trigno recordings at 2 kHz)
- Preprocessing: bandpass filter (20-500 Hz), rectification, notch filter (50/60 Hz)
- Segment into overlapping windows (200ms window, 50ms stride)
- Extract time-domain features: MAV, RMS, WL, ZC, SSC per channel
- Extract frequency-domain features: MNF, MDF, spectral power bands
- Result: a feature matrix per window representing the forearm's current muscle state

#### Step 2: Muscle Activation Mapping (The "Limb Model")

- For each amputee subject in DB3, build a **personalized muscle activation map**:
  - Which EMG channels activate for which intended movements?
  - What is the activation strength and timing pattern?
  - Which movements are clearly distinguishable vs. which overlap?
- Visualize as a **forearm muscle heatmap** — a 2D circular layout of electrode positions showing activation intensity per movement
- This map IS the functional digital model of the residual limb — it characterizes what that specific amputee's forearm can and cannot express through muscle signals
- Clinical value: immediately shows the clinician which movements are easy/hard for this patient → guides prosthetic configuration

#### Step 3: CNN Movement Intent Classifier

- **Architecture:** Temporal CNN (1D convolutions over multi-channel sEMG windows) or CNN-LSTM hybrid
- **Training strategy:**
  1. **Pre-train** on intact subjects (DB1: 27 subjects × 52 movements; DB2: 40 subjects × 49 movements) — large data, many movements
  2. **Fine-tune** on amputee data (DB3: 11 amputees × 49 movements) — adapts to amputation-specific signal patterns
  3. **Validate** on held-out amputees from DB7 (2 amputees) and DB10 (15 amputees) — tests generalization
- **Target accuracy:** >85% on amputees for 49 movements; >95% for a practical subset of 6-10 core grasps (following Wu et al., who achieved 99% on a simplified task)
- **Per-patient personalization:** For a new patient, collect 10-15 min of calibration sEMG → fine-tune the pre-trained model via transfer learning → personalized classifier ready

#### Step 4: Multi-Modal Fusion (using DB10)

- Integrate sEMG + IMU (forearm orientation) from DB10's 15 amputees
- Test whether adding arm posture context (forearm angle, rotation) improves classification
- Expected: +3-5% accuracy gain, especially for distinguishing posture-dependent grasps

**Phase 1 Deliverables:**
1. Personalized muscle activation maps for each amputee in the dataset
2. Trained CNN classifier with documented accuracy on amputee test sets
3. Transfer learning pipeline ready for new patients
4. Open-source signal processing and training code

---

### 4.3 Phase 2 — Prosthetic Hand Digital Twin

**Objective:** Build a real-time 3D prosthetic hand on screen that responds to the CNN classifier's output — enabling amputees to see a virtual hand move in response to their muscle signals, and practice controlling it.

**How it connects to Phase 1:** The CNN from Phase 1 decodes the sEMG → movement intent. Phase 2 takes that intent and animates a 3D hand model accordingly. Together they form a complete loop: **muscles → AI → digital hand**.

#### Step 1: 3D Hand Model

- Model a prosthetic hand (based on iHannes or similar multi-DOF myoelectric design) with articulated finger joints
- Use a physics engine (Unity or MuJoCo) for rigid-body kinematics and object interaction
- Define a movement mapping: each of the classifier's output classes (e.g., "power grasp", "precision pinch", "wrist rotation") drives specific joint angles and finger configurations
- Render on screen in real-time with multiple camera views

#### Step 2: Replay Mode — Offline Digital Twin (using Ninapro data directly)

- Load any Ninapro recording (e.g., an amputee from DB3 performing 49 movements)
- Run the sEMG through the Phase 1 CNN → get movement intent predictions over time
- Drive the 3D hand model with those predictions
- **Result:** You can watch the digital twin hand "perform" the movements that the amputee's muscles were attempting
- Compare the digital twin's movements against the Ninapro kinematic ground truth (DB1/DB2/DB8 provide actual finger positions) → measure how faithfully the digital twin reproduces intended movements
- **This is the core demonstration:** showing that sEMG from an amputee's forearm can drive a realistic prosthetic hand simulation

#### Step 3: Real-Time Mode — Live Interaction (with sEMG hardware)

- Connect a live sEMG sensor array (e.g., Thalmic Myo, Delsys Trigno, or low-cost OTBioelettronica)
- Stream sEMG in real-time → Phase 1 CNN classifies → 3D hand responds on screen
- The user sees the hand open, close, pinch, rotate, etc., in <100ms latency
- This enables:
  - **Pre-fitting evaluation:** Test how well the patient can control a prosthetic hand *before* it is built
  - **Training:** Practice controlling different grasps with visual feedback
  - **Clinician optimization:** Adjust the classifier's movement mapping, sensitivity thresholds, or reduce the number of movement classes to match the patient's muscle differentiation ability

#### Step 4: Training Tasks & Performance Tracking

- Simple on-screen tasks for the amputee to practice:
  - "Open the hand" → "Close into power grasp" → "Release"
  - "Pick up the virtual ball" (requires selecting correct grasp + activating muscles)
  - "Switch between 3 grasp types on command"
- Performance metrics tracked:
  - Classification accuracy per session (does the correct movement trigger?)
  - Response time (how fast from muscle activation to correct hand movement?)
  - Consistency (how stable are repeated attempts?)
  - Progress over sessions (learning curve)
- Simple dashboard showing improvement over time

**Phase 2 Deliverables:**
1. 3D prosthetic hand model with physics-based finger articulation
2. Replay mode: Ninapro recordings → CNN → animated digital twin hand
3. Real-time mode: live sEMG → CNN → hand animation (<100ms latency)
4. Training task suite with performance tracking
5. Clinician-facing dashboard

---

## 5. Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| ML/DL Framework | PyTorch | CNN training, transfer learning, inference |
| Signal Processing | SciPy, NumPy, MNE-Python | sEMG filtering, feature extraction, windowing |
| 3D Hand Simulation | Unity 3D (Desktop) or PyBullet/MuJoCo | Prosthetic hand model, physics, rendering |
| Data Platform | **Ninapro Database (DB1-DB10)** | 180+ sEMG acquisitions (free, open access) |
| sEMG Hardware (Phase 2 live mode) | Thalmic Myo Armband ($200) or Delsys Trigno | Live forearm EMG capture |
| Visualization | Matplotlib / Plotly / Streamlit | Muscle activation maps, performance dashboards |
| Backend | Python | Data pipelines, model serving |
| Version Control | Git + GitHub | Code management |

---

## 6. Business Problem & Market Opportunity

### 6.1 The Business Problem

The prosthetic hand industry has a **massive waste problem**: 30-50% of devices costing $20,000-$100,000 each are abandoned because patients can't control them well enough. There is no way to evaluate patient-device compatibility before committing to fabrication.

### 6.2 Market Size

| Metric | Value |
|--------|-------|
| Global prosthetics market | **$7.1 billion** |
| Upper-limb / myoelectric segment | **~$600 million** |
| Device abandonment waste (per year, US alone) | **~$200-500 million** |
| CAGR (upper-limb prosthetics, 2024-2030) | **7.2%** |

### 6.3 Cost of the Problem (Per Patient)

| Cost Driver | Cost |
|-------------|------|
| Myoelectric prosthetic hand | $20,000 – $100,000 |
| EMG calibration sessions (5-15 visits) | $2,500 – $10,000 |
| Occupational therapy (6-16 weeks) | $5,000 – $25,000 |
| Lost productivity | $15,000 – $40,000/year |
| Abandoned device (30-50% rate) | Full device cost wasted |

### 6.4 How SimHand Solves This

| Problem | SimHand Solution | Savings |
|---------|-----------------|---------|
| Can't test before buying | Digital twin lets patient try controlling a virtual hand first | Avoid $20K-$100K bad purchase |
| Slow EMG calibration | AI pre-trained on 180+ subjects; needs only 10-15 min patient calibration | 50-70% fewer clinic visits |
| Tedious rehab | Visual feedback on screen makes training engaging and measurable | 30-50% shorter rehab |
| High abandonment | Patients are more confident and proficient before getting the device | Reduce from 30-50% to <15% |

### 6.5 Business Model

```
┌────────────────────────────────────────────────┐
│              Revenue Streams                   │
├────────────────────────────────────────────────┤
│                                                │
│  1. SaaS License (clinics/hospitals)           │
│     → $500-2,000/month                         │
│                                                │
│  2. Per-Patient Assessment Fee                 │
│     → $200-500 per evaluation                  │
│                                                │
│  3. OEM Licensing to hand manufacturers        │
│     → Ottobock, Össur, etc. embed SimHand      │
│       as a pre-fitting tool with their devices │
│                                                │
│  4. Research Licensing                         │
│     → Universities & labs pay for the          │
│       pre-trained models and pipeline          │
│                                                │
└────────────────────────────────────────────────┘
```

---

## 7. Project Timeline

### Phase 1: Residual Limb Modeling & AI Classifier (Months 1-4)

| Month | Tasks |
|-------|-------|
| 1 | Download and explore Ninapro DB1, DB2, DB3. Build sEMG preprocessing pipeline (filtering, windowing, feature extraction). |
| 2 | Implement CNN architecture. Pre-train on DB1+DB2 (intact subjects). Evaluate baseline accuracy. |
| 3 | Fine-tune on DB3 (11 amputees). Build muscle activation maps for each amputee. Validate on DB7/DB10 amputees. |
| 4 | Implement transfer learning pipeline (few-shot per-patient adaptation). Test multi-modal fusion (sEMG+IMU from DB10). Document results. |

**Milestone:** CNN achieving >85% accuracy on 49 movements (amputee data), >95% on 6-10 core grasps.

### Phase 2: Prosthetic Hand Digital Twin (Months 5-8)

| Month | Tasks |
|-------|-------|
| 5 | Build 3D prosthetic hand model (articulated fingers, physics). Define movement-to-joint mapping for all classifier output classes. |
| 6 | Implement replay mode: Ninapro sEMG → CNN → 3D hand animation. Validate against kinematic ground truth. |
| 7 | Implement real-time mode with live sEMG sensor. Build training tasks and scoring system. |
| 8 | Build performance dashboard. Test with volunteers. Polish and document. |

**Milestone:** Working digital twin hand driven by live sEMG with <100ms latency, plus training task suite.

---

## 8. Key Performance Indicators

| KPI | Target | How Measured |
|-----|--------|--------------|
| CNN accuracy (49 movements, amputees) | > 85% | Test on held-out Ninapro DB3 subjects |
| CNN accuracy (6-10 core grasps) | > 95% | Test on DB3 + DB7 + DB10 amputees |
| Transfer learning calibration time | < 15 min per new patient | Timed calibration session |
| Digital twin latency (sEMG → hand response) | < 100 ms | End-to-end timing measurement |
| Replay accuracy vs. kinematic ground truth | > 80% movement match | Compare CNN predictions to DB8 finger kinematics |
| Training task improvement | > 30% faster after 5 sessions | Task completion time tracking |

---

## 9. Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| CNN accuracy drops on amputees vs. intact subjects | High | High | Use amputee-specific fine-tuning; reduce to fewer classes if needed |
| Ninapro data doesn't generalize to new sensors | Medium | Medium | Test with DB4 (Cometa) and DB5 (Myo Armband); design sensor-agnostic features |
| EMG signal degrades over time (sweat, electrode shift) | High | Medium | Use DB6 (repeatability data) to train for day-to-day variability |
| Real-time latency too high for responsive feel | Low | Medium | Optimize CNN inference (ONNX/TensorRT); use lightweight architecture |
| Limited amputee data (30 subjects total) | Medium | High | Augmentation (noise injection, channel dropout); pre-train on larger intact data |

---

## 10. Team & Resources

| Role | Count | Skills |
|------|-------|--------|
| ML Engineer | 1-2 | PyTorch, signal processing, CNN architecture |
| 3D Developer | 1 | Unity or PyBullet, hand kinematics, rendering |
| Biomedical Engineer (Lead) | 1 | sEMG domain knowledge, prosthetics background |

### Budget (8 months)

| Item | Cost |
|------|------|
| Computing (GPU cloud for training) | $500 – $1,500 |
| sEMG sensor for live testing (Myo Armband or similar) | $200 – $3,000 |
| Ninapro data access | **$0** (free, open access) |
| Software (Unity, PyTorch — all free/open-source) | $0 |
| **Total** | **$700 – $4,500** |

---

## 11. Expected Outcomes

1. **A working AI model** that decodes hand movement intent from forearm EMG signals, trained and validated on real amputee data (Ninapro).
2. **A visual digital twin** of a prosthetic hand that responds to those decoded signals in real-time on screen.
3. **A practical tool** that could let amputees "try" a prosthetic hand before buying one, and practice controlling it with visual feedback.
4. **Publishable research** contributing to the Ninapro ecosystem and prosthetic hand ML community.

---

## 12. References

1. Wu, J., Jangid, V., & Park, J. (2024). "Digital Twin for Amputees: A Bidirectional Interaction Modeling and Prototype with Convolutional Neural Network." *Proc. HFES Annual Meeting*, 68(1), 1410–1416.
2. Cellupica, A., Cirelli, M., et al. (2024). "An Interactive Digital-Twin Model for Virtual Reality Environments to Train in the Use of a Sensorized Upper-Limb Prosthesis." *Algorithms*, 17, 35.
3. Atzori, M., Gijsberts, A., et al. "The Ninapro Database." ninapro.hevs.ch.
4. Biddiss, E. & Chau, T. (2007). "Upper-limb prosthetics: critical factors in device abandonment." *Am J Phys Med Rehabil*, 86(12), 977-987.
5. Schoppen, T., et al. (2001). "Employment reintegration after limb amputation." *Disability and Rehabilitation*.
6. Lee, S., et al. (2022). "Occupational changes following upper limb amputation." *Journal of Hand Surgery*.
6. Biddiss, E. & Chau, T. (2007). "Upper-limb prosthetics: critical factors in device abandonment." *American Journal of Physical Medicine & Rehabilitation*, 86(12), 977-987.
7. Schoppen, T., et al. (2001). "Employment reintegration after limb amputation." *Disability and Rehabilitation*.
8. Lee, S., et al. (2022). "Occupational changes following upper limb amputation." *Journal of Hand Surgery*.

---

*Prepared for: SBME 4th Year — Rehabilitation Engineering Project, March 2026*
