# DreamTeam — Autonomous Development Cruiser for Cursor

[![License: PolyForm](https://img.shields.io/badge/License-PolyForm_Noncommercial-blue.svg)](LICENSE)
[![System: Cursor](https://img.shields.io/badge/Designed_for-Cursor-00AEEF.svg)](https://cursor.sh)

A long-range **Autonomous Development Cruiser for Cursor** capable of executing **500+ sequential tasks** without quality degradation. Built for fault tolerance, continuous learning, and multi-layered agent orchestration using **ping-pong execution loop**.

> [!IMPORTANT]
> **Dispatcher Architecture:** DreamTeam is designed to offload deep work from the main chat. The **Dispatcher** coordinates **Left and Right Orchestrators** to run batches of 15+ tasks with minimal supervision. Each context switch (ping-pong) performs a context reset, ensuring the dispatcher never hits context ceilings. This is the key to executing **500+ tasks** with zero performance degradation.

**Quick Start:**
1. `python -m dreamteam new-project .` (in an empty folder)
2. Open in Cursor → `/start` + your goal
3. Start or resume the execution loop: `/run`

---

## Pipeline: High-Performance Autonomy

The system uses a recursive dispatching loop. The **Dispatcher** coordinates specialized orchestrators to handle batches of tasks, keeping the main context clean and stable.

```mermaid
---
config:
  layout: fixed
  look: handDrawn
---
flowchart BT
 subgraph PhaseP["Planning"]
    direction TB
        P2["Sub-Planner"]
        P1["Planner"]
  end
 subgraph PhaseE["Execution Loop"]
    direction TB
        E2["Reviewer"]
        E1["Developer"]
        E3["DevExperience"]
        E4["Git-Ops"]
        Upd["update-task Done"]
  end
 subgraph PhaseM["Maintenance"]
    direction TB
        M2["FixPlanner"]
        M1["Learning / Meta"]
        M3["Researcher"]
        M4["Auditor"]
  end
 subgraph Ops["Operational Phases"]
    direction LR
        PhaseP
        PhaseE
        PhaseM
  end
 subgraph Context["Isolated Agent Context"]
    direction TB
        Ops
        LR_Agent{"Left and Right Orchestrator"}
        Term[["Terminal Subagent"]]
  end
 subgraph Engine["DreamTeam Cruiser Engine"]
    direction LR
        DP["Dispatcher"]
        Context
        DAG[("Task DAG")]
        RAG[("Memory DB")]
        Counter[("Counter")]
  end
    User(["User Goal"]) --> DP
    DP -- Switch batch --> LR_Agent
    LR_Agent --> Ops
    P1 --> P2
    E1 --> E2
    E2 --> E3
    E3 --> E4
    E4 --> Upd
    M1 --> M2 & E1
    Ops -.-> Term
    P2 --- DAG
    M2 --- DAG
    M3 --- RAG
    Upd -. "Batch Limit =15 or
    Context Overflow" .-> DP
    P2 -. Planning Done .-> DP
    M4 --> RAG
    Counter --> M4 & M3 & M1
    DAG --> M4 & M3

     P2:::clsWorker
     P1:::clsWorker
     E2:::clsWorker
     E1:::clsWorker
     E3:::clsWorker
     E4:::clsWorker
     Upd:::clsWorker
     M2:::clsMaintain
     M1:::clsMaintain
     M3:::maintain
     LR_Agent:::clsOrch
     Term:::clsInfra
     DP:::clsMain
     DAG:::clsDB
     RAG:::clsDB
    classDef clsMain fill:#4f46e5,color:#fff,stroke:#3730a3,stroke-width:2px,rx:10
    classDef clsOrch fill:#f8fafc,stroke:#94a3b8,stroke-width:2px,stroke-dasharray: 4,rx:10
    classDef clsWorker fill:#ffffff,stroke:#e2e8f0,stroke-width:1px,rx:4
    classDef clsMaintain fill:#ecfdf5,stroke:#10b981,color:#064e3b,rx:4
    classDef clsInfra fill:#0f172a,color:#fff,stroke:#1e293b,rx:2
    classDef clsDB fill:#fff,stroke:#64748b,stroke-width:2px,shape:cylinder
    style LR_Agent stroke:#00C853,fill:#FFD600
    style Context fill:#f8fafc,stroke:#e2e8f0,stroke-width:1px
    style DAG stroke:#000000,fill:#FF6D00
    style RAG fill:#FF6D00
    style Counter fill:#FF6D00
    style User fill:#00C853
    style Engine fill:#fdfaff,stroke:#c4b5fd,stroke-width:2px
```
---

## Economy & Model Selection

> [!IMPORTANT]
> **Model Inheritance:** By default, all sub-agents inherit the model name chosen in the main chat (where `/start` or `/run` was invoked).

To optimize project **economy**:
*   **Heavy Reasoning** (Planner, Auditor, Researcher, Learning): We recommend using frontier models (e.g., Claude 4.6 Sonnet) for high architectural compliance.
*   **Routine Tasks** (Developer, Reviewer, Git-Ops): These can often be shifted to more economical models to maintain sustainability over 500+ sequential tasks.

Thoughtful model selection ensures the Project Budget lasts for the entire Cruiser journey.

---

## Under the Hood: Scalable Autonomy

The system is built to minimize "Main Chat" context overflow. Using a **Dual Orchestrator system (Left/Right)**, DreamTeam offloads execution to sub-agents, leaving the main chat lean and responsive. This architectural split allows massive task sequences to run even on non-frontier models.
## AI Sub-Agent Hierarchy

DreamTeam uses a multi-layered intelligence system to ensure stability over long durations:

1.  **Level 1: Fleet Control (Dispatcher)**: The entry point. It doesn't perform tasks but manages the switching between "Left" and "Right" Orchestrators. This ensures that even for 1000-task journeys, the main chat context remains lean and responsive.
2.  **Level 2: Task Orchestration (Orchestrators)**: Specialized agents that run inside a fresh context. They decide whether to launch the **Planning Phase** or the **Execution Loop** and handle all self-correction triggers.
3.  **Level 3: Specialized Workers**: 
    *   **Planner & Sub-Planner**: Decompose high-level goals into a detailed task DAG.
    *   **Developer**: Implements features and runs tests.
    *   **Reviewer**: Verifies code quality and architectural compliance.
    *   **Git-Ops**: Handles commits and repository maintenance.
    *   **Maintenance Agents**: (Researcher, Learning, Meta-Planner, Auditor) Keep the context compressed and the pipeline optimized.

---

## Core Mechanisms

### Fault Tolerance — Nothing Gets Lost
The system is designed to recover from crashes, mismatches, and stuck tasks without manual intervention:
*   **run-next**: Verifies DB↔Files consistency, auto-syncs if needed, and resets stuck tasks.
*   **recover**: Full system reset, integrity verification, and memory health check.
*   **State-in-DB**: All state lives in SQLite. The Cruiser can resume after a break without losing a single bit of context.

### Learnability — The Pipeline Adapts
DreamTeam improves from production feedback instead of degrading:
*   **DevExperiencer**: Records every outcome, attempt count, and time spent.
*   **Learning Agent**: Analyzes the Experience DB to detect patterns of failure or high friction.
*   **FixPlanner**: Automatically adjusts upcoming tasks (library choices, dependency updates) to avoid recurring roadblocks.
*   **Developer Updates**: The system may augment `.cursor/agents/developer-addendum.md` with additional instructions to permanently adopt successful patterns.

### Analytics Dashboard — Monitor the Friction
Launch a minimalistic web dashboard to track your Cruiser's performance:
*   **KPIs**: Total tasks, estimated tokens, and **Friction Score** (Avg Attempts).
*   **Visualization**: Identify hallucination spikes and time-heavy tasks.
*   **Task Lineage**: Track original plans vs. tasks added during self-correction.

> **Command:** `python -m dreamteam dashboard`

---

## Documentation
- [guide/](guide/) — Full setup, commands, and best practices.
- [INSTRUCTIONS.md](guide/INSTRUCTIONS.md) — System overview.
- [COMMANDS.md](guide/COMMANDS.md) — CLI reference.

---

## License
MIT license

---
<p align="center">Crafted for Cursor adepts with love from <b>BuLab</b></p>
