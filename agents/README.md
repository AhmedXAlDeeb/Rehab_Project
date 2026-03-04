# RehabPath — Agent Directory

This folder contains personality and system-prompt definitions for the five AI agents used to develop the RehabPath platform. Each agent covers a different perspective. Use them by loading their system prompt into a chat session and logging the conversation in their respective log file.

---

## Agent Roster

| Agent | File | Role | Log |
|-------|------|------|-----|
| 🧑‍🦽 **Khaled** — Patient | [patient.md](patient.md) | Simulates a new transradial amputee planning their first prosthetic. Stress-tests features from lived experience at every stage — pre-fitting through mastery. | [logs/patient_log.md](logs/patient_log.md) |
| 👨‍💻 **Omar** — Engineer | [engineer.md](engineer.md) | Senior software engineer. Designs, implements, and debugs all code. MuJoCo, RL, PyTorch, signal processing. | [logs/engineer_log.md](logs/engineer_log.md) |
| 🔬 **Sara** — Researcher | [researcher.md](researcher.md) | Research analyst. Reads and synthesises papers, validates design decisions against literature, identifies benchmarks. | [logs/researcher_log.md](logs/researcher_log.md) |
| 📋 **Hana** — Product Manager | [pm.md](pm.md) | PM. Owns the roadmap, prioritises the backlog, writes user stories, and tracks KPIs. | [logs/pm_log.md](logs/pm_log.md) |
| 🩺 **Dr. Rania** — Clinical Expert | [clinical_expert.md](clinical_expert.md) | PM&R physician. Validates clinical credibility, enforces safety guardrails, maps to clinical outcome measures. | [logs/clinical_log.md](logs/clinical_log.md) |

---

## When to Use Each Agent

```
DESIGN a new feature?
  → Start with Hana (PM) to write the user story and define acceptance criteria
  → Check with Dr. Rania (Clinical) for safety and validity
  → Move to Omar (Engineer) to design the implementation

VALIDATE an assumption?
  → Sara (Researcher) for literature backing
  → Khaled (Patient) for lived-experience reality check — use the Journey Map in patient.md
     to pick the right conversation starter for the layer you're building
  → Dr. Rania (Clinical) for clinical credibility

STUCK on an implementation problem?
  → Omar (Engineer) exclusively — paste the code, describe the error

PREPARING a presentation or report section?
  → Sara for citations and evidence
  → Hana for narrative structure and KPI framing
  → Alex for a patient voice / opening hook

REVIEWING completed work?
  → Hana checks: does this meet acceptance criteria?
  → Dr. Rania checks: is this clinically safe and valid?
  → Omar checks: is this the right engineering approach?
```

---

## Workspace Structure

```
agents/
├── README.md              ← You are here
├── patient.md             ← Alex — patient participant
├── engineer.md            ← Omar — senior software engineer
├── researcher.md          ← Sara — research analyst
├── pm.md                  ← Hana — product manager
├── clinical_expert.md     ← Dr. Rania — clinical domain expert
└── logs/
    ├── patient_log.md
    ├── engineer_log.md
    ├── researcher_log.md
    ├── pm_log.md
    └── clinical_log.md

resources/
├── research/              ← All PDF papers
│   ├── wu-et-al-2024-digital-twin-for-amputees...pdf
│   ├── adv intell discov - 2026 - Chowdhury...pdf
│   ├── 38904_Robotic_Foundation_Model.pdf
│   ├── bioengineering-11-00084.pdf
│   ├── Advanced Research Directions for AI-Powered Smart Prosthetics.pdf
│   ├── 2601.01321.pdf / 2601.01321v1.pdf
│   └── TE013342.pdf
└── projects/
    └── RehabArm-RL-Sim2Real/   ← Existing simulation codebase
        ├── src/env.py
        ├── src/train.py
        ├── src/utils.py
        ├── assets/arm.xml
        └── main.py
```

---

## How to Load an Agent

### In GitHub Copilot Chat (VS Code)
1. Open a new chat
2. Copy the **System Prompt** block from the agent's `.md` file
3. Prepend your message with:  
   > `[SYSTEM]: {paste system prompt here}`  
   > `[USER]: {your question}`

### In ChatGPT / Claude (web)
1. Open a new conversation
2. Paste the system prompt as the first message (or into the custom instructions field)
3. Begin the conversation

### Logging
After each session, add a block to the agent's log file using the template in that file.

---

## Agent Interaction Map

```
           Khaled (Patient)
               ↑ reality check
Hana (PM) ────────────────── Dr. Rania (Clinical)
     ↓ user stories          ↑ clinical safety
Omar (Engineer) ←── Sara (Researcher) ← papers
     ↑ implementation            ↑ evidence
     └──────── code ─────────────┘
```

Sara and Dr. Rania should always be consulted together for any design decision touching patient safety or clinical protocol.
