# 🏗️ The Atomic Agentic OS: Architectural Blueprint (v2.0 - V8 Engine)

A decentralized, file-based **Agentic OS** built to act as the "V8 Engine" for specialized AI agents. 
The system enforces strict separation between the "Shredder" (the immutable, model-agnostic runtime) and the "Paper" (declarative agent workflows, ISO-compliant state traces, and prompt injections).

## 🌟 Current Status: Phase 1 (Core OS Hardening) Complete
The OS has completed its foundational V8 re-architecture. The execution pipeline is fully automated, highly observable, and uses a strict inter-workspace communication schema.

---

## 🏗️ The V8 Architecture

### 1. The Engine (`core/runner.py`)
The universal execution loop. It is a 9-step immutable pipeline powered by `atomic-agents`. It strictly mounts authorized skills, initializes the agent context, handles API rate-limit retries via exponential backoff, and ensures total observability through the Flight Recorder.

### 2. The Flight Recorder (`.state.json`)
Every task dispatched to an agent generates a `.state.json` file in the `.agents/active/` directory. This file tracks timestamps, the active step of the pipeline, LLM failure states, and full memory dumps to guarantee ISO-compliant auditability.

### 3. The InterAgentHandshake (`core/schemas/handshake.py`)
A strict `Pydantic` schema defining how agents communicate. Every request passed through the system is serialized into a standard Markdown file loaded with YAML frontmatter containing the required execution arguments (Sender ID, Receiver ID, Priority, Directive, Payload).

### 4. The Mailroom Skill (`skills/mailroom/tool.py`)
A dedicated OS-level skill that allows an active agent to seamlessly generate an `InterAgentHandshake` atom and seamlessly drop it into another isolated workspace's inbox over the flat-file State Bus.

---

## 📁 Directory Schema (The Workspace Cartridge)

```text
.
├── .agents/
│   ├── inbox/          # Task entry point (Handshake Atoms dropped here)
│   ├── active/         # Processing state (Flight Recorders live here)
│   ├── review/         # Human/QA gate (Generated Engine Reports)
│   └── logs/           # Global execution traces
├── .vault/
│   └── policy.json     # RBAC & Tool Permissions
├── config/
│   ├── workforce.yaml  # Agent identity and roles
│   ├── providers.yaml  # Model agnostic routing (OpenAI, Anthropic, Ollama)
│   └── kernel.md       # Universal Workspace SOPs injected into the system prompt
├── core/
│   ├── orchestrator.py # File-watcher Dispatcher
│   ├── runner.py       # The V8 Execution Engine
│   ├── factory.py      # LLM Provider Initialization
│   └── vault.py        # Security Validation
└── skills/
    ├── registry.py     # Global OS Tool Registry
    ├── mailroom/       # Cross-workspace I/O Hub
    ├── file_manager/   # Standard file operations
    ├── scaffolder/     # Meta-agent workflow generation
    └── terminal/       # Isolated Bash access
```

---

## 🚀 Setup & Execution

### 1. Installation

Clone this repository and create a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Verify V8 Engine Integrity

The OS ships with a full validation suite. Ensures the Handshake payload serializes correctly and the Mailroom correctly routes across conceptual workspaces.

```bash
source venv/bin/activate
PYTHONPATH=. python3 -m unittest discover core/
```

### 3. Boot the Orchestrator

Run the core orchestrator script. This starts a `watchdog` daemon that listens to the `.agents/inbox/` directory and mounts the V8 Engine to process incoming requests.

```bash
# Optional: Clear zombie processes first
./cleanup.sh

# Keep this running in your terminal
PYTHONPATH=. python3 core/orchestrator.py
```

### 4. Run the Diagnostic Handshake test

1. Create a Handshake test file inside `.agents/inbox/` (for example, `test.md`):

```markdown
---
task_id: "HW-002"
agent_id: "dictator"
priority: "high"
---
# Task: Diagnostic
Acknowledge this file to confirm the V8 pipeline is mounted and the Flight Recorder is tracking.
```

2. Watch the orchestrator terminal. You should see logs indicating the OS booted the V8 framework for the agent `dictator`.
3. Check the `.agents/review/` directory. The engine will drop a full execution report there. Check `.agents/active/HW-002.state.json` to view the trace of the pipeline execution.
