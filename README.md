# 🏗️ The Atomic Agentic OS: Architectural Blueprint (v2.0)

A decentralized **Agentic OS** where specialized Atomic Agents interact with a shared workspace and external systems. The system is designed to be **headless, file-based, and human-readable**, allowing it to scale from local coding tasks to enterprise-level business automations.

## 1. Directory Schema

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

## 🏗️ V8 Engine Architecture (Phase 1 Complete)

The OS has successfully completed its foundational "V8" re-architecture, enforcing a strict separation between the immutable runtime and declarative agent workflows.

### 1. The Engine (`core/runner.py`)
A 9-step immutable execution loop using `atomic-agents`. It strictly mounts authorized skills, initializes the agent context, handles API rate-limit retries via exponential backoff, and ensures full observability.

### 2. The Flight Recorder (`.state.json`)
Every task dispatched generates a state trace tracking timestamps, pipeline steps, LLM failures, and full memory dumps for ISO-compliant auditability.

### 3. The InterAgentHandshake (`core/schemas/handshake.py`)
A strict `Pydantic` schema defining how agents communicate. Requests are serialized into standard Markdown files with YAML frontmatter (Sender, Receiver, Priority, Directive, Payload).

### 4. The Mailroom Skill (`skills/mailroom/tool.py`)
An OS-level skill allowing an active agent to generate an `InterAgentHandshake` atom and seamlessly route it to another workspace's inbox over the flat-file State Bus.

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
Acknowledge this file to confirm the Atomic Agentic OS is mounted and the Flight Recorder is tracking.
```

2. Watch the orchestrator terminal. You should see logs indicating the OS booted the V8 framework for the agent `dictator`.
3. Check the `.agents/review/` directory. The engine will drop a full execution report there. Check `.agents/active/HW-002.state.json` to view the trace of the pipeline execution.
