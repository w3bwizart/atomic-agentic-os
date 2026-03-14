# 🏗️ The Atomic Agentic OS: Architectural Blueprint (v2.0)

A decentralized **Agentic OS** where specialized Atomic Agents interact with a shared workspace and external systems. The system is designed to be **headless, file-based, and human-readable**, allowing it to scale from local coding tasks to enterprise-level business automations.

## 1. Directory Schema

```text
.
├── .agents/
│   ├── inbox/          # Task entry point
│   ├── active/         # Processing state
│   ├── review/         # Human/QA gate
│   └── logs/           # Execution traces
├── .vault/
│   └── policy.json     # RBAC & Permissions
├── config/
│   ├── workforce.yaml  # Agent roles
│   ├── providers.yaml  # LLM settings
│   └── kernel.md       # System SOPs
├── core/
│   ├── orchestrator.py # File-watcher Dispatcher
│   ├── runner.py       # LLM Execution Loop
│   ├── factory.py      # LLM Provider Initialization
│   └── vault.py        # Security & Validation
├── docs/examples/      # Stress test configurations
└── skills/
    ├── registry.py     # Tool dynamic mapping (Phonebook)
    ├── dependencies/   # Cross-agent WaitSkill
    ├── file_manager/   # Standard file I/O operations
    └── terminal/       # Isolated bash access
```

## 🛠️ Core Feature List

### 1. Atomic Skill Attribution (RBAC)
Agents are defined by their Tools/Skills. We use Pydantic-driven tool validation to ensure agents only access their designated functions.

### 2. External System Integration (Connectors)
Access to the world via Direct APIs, **MCP (Model Context Protocol)**, and **Browser-as-a-Service**. Ingest data from SQL, Slack, Salesforce, or any web portal.

### 3. Secret Management (The "Zero-Knowledge" Layer)
Protect sensitive credentials from the "Agent Brain." Secrets are stored in a secure OS Keychain or a Vault (e.g., HashiCorp). The agent never "sees" the raw key in its context window; it only calls a `secure_request_skill` that handles the authentication behind the scenes.

### 4. Flat-File Messaging & State (The "Sprawl" Bus)
`.agents/` folder acts as the source of truth. Uses Markdown for human-readability and JSONL for high-speed agentic logs.

### 5. Dictator-Lieutenant Workflow
Hierarchical task breakdown. 1 Planner (Dictator) → N specialized executors (Lieutenants).

### 6. Centralized SOPs & Guidelines
A "Bible" (e.g., `kernel.md` or Obsidian vault) containing code standards, branding guides, and security rules.

## ✨ Visionary / "Nice-to-Have" Features

### 1. The "Agent Command Center" (Observability Dashboard)
A visual UI that parses the `.agents/` logs in real-time. View active agent "thoughts," tool-call history, and current bottlenecks. Stays "Flat-File First"—the dashboard is just a viewer for the markdown/JSONL files.

### 2. User & System Analytics
Tracking ROI and performance via token usage per task, success rate of "Micro-Commit" loops, and time-saved metrics for the business user.

### 3. The "Meta-Scaffolder" (The Yeoman Agent)
An "Architect Agent" that takes a high-level idea and generates the entire folder structure, `skill.md` files, and initial "Tickets" for a new project.

---

## 🚀 Setup & Diagnostic Testing

To test the core Agentic OS environment and ensure the file-watcher is processing correctly, follow these steps:

### 1. Installation

Clone this repository and create a Python virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start the Orchestrator

Run the core orchestrator script. This starts a `watchdog` daemon that listens to the `.agents/inbox/` directory and safely dispatches threaded jobs to the `runner`.

```bash
# Optional: Clear zombie processes first
./cleanup.sh

# Keep this running in your terminal
python3 core/orchestrator.py
```

### 3. Run the Diagnostic Test (The "Hello World")

The orchestrator is currently configured with a "Dictator" diagnostic mode. If a task is assigned to `dictator`, the system will simply acknowledge the file, initialize its internal state tracking, and move the file out of the inbox.

1. Create a markdown file inside `.agents/inbox/` (for example, `test.md`):

```markdown
---
task_id: "HW-002"
agent_id: "dictator"
priority: "high"
---
# Task: Diagnostic
Acknowledge this file.
```

2. Watch the orchestrator terminal. You should see logs indicating that the file was detected, the frontmatter parsed, SOPs injected, and the file moved.
3. Check the `.agents/active/` directory. The `test.md` file will now be located there, along with a newly generated `HW-002.state.json` file used for state synchronization. You can also view `.agents/logs/system.log` to trace exactly what happened.
