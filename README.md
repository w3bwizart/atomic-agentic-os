# 🏗️ The Atomic Agentic OS (v2.0)

Welcome to the **Atomic Agentic OS**, a file-based operating system where specialized AI agents work together in an assembly line to automate your tasks.

Whether you're a starter building your first AI workflow or a Senior AI Architect designing ISO-compliant enterprise systems, this OS scales beautifully to fit your needs.

---

## ⚡ The 1-Minute Quick Start (For Beginners)

Want to see the magic happen instantly? Here is everything you need to know.

Think of this OS like a factory.
1. The **Inbox** is where you drop a task.
2. The **Orchestrator** is the manager who wakes up the workers when a task arrives.
3. The **Agents** are the specialized workers that read the task, do their job, and pass it to the next person.
4. The **Review** folder is where the finished product is placed.

### Step 1: Add Your AI Key
The OS is completely **model-agnostic**. It seamlessly natively routes to **Groq, OpenAI, Anthropic, Gemini, or local Ollama** models!
To get started, simply configure your favorite provider. 
1. Create a file called `.env` in the root folder.
2. Add your provider's API key inside it (e.g., Groq for maximum speed):
   ```bash
   GROQ_API_KEY=your_key_here
   # OPENAI_API_KEY=...
   # ANTHROPIC_API_KEY=...
   ```

### Step 2: Turn on the Multi-Tenant Orchestrator
Open your terminal and run the daemon:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Start the Recursive Watcher
PYTHONPATH=. venv/bin/python core/orchestrator.py
```
*Leave this terminal open! You will see the matrix-style logs streaming here.*

### Step 3: Trigger an Isolated Workspace Workflow
Open a **second terminal** and trigger the active sandbox. The Orchestrator automatically binds to dynamically loaded folders in `workspaces/`:
```bash
touch workspaces/content_team/.agents/inbox/start_post.md
```

Watch your first terminal! The `researcher`, `writer`, and `editor` agents will securely load the `content_team` workforce graph, pass internal handshakes back and forth, and drop a highly-polished LinkedIn post into the `workspaces/content_team/.agents/review/` directory!

---

## 🧠 Under the Hood (For Senior Developers)

If you are a Senior Engineer, you care about predictability, auditability, and immutability. The Atomic Agentic OS is designed to be a transparent **State Bus**, heavily relying on declarative file systems rather than obfuscated memory stores.

### The OS Execution Pipeline (`core/runner.py`)
At its core, the OS uses a strict, immutable 9-step execution loop powered by `atomic-agents`. When the Orchestrator daemon (`watchdog`) detects a payload, it spins up the Atomic Engine. The engine strictly mounts authorized tools based on Role-Based Access Control (`.vault/policy.json`), loads workspace SOPs into the system prompt, and manages exponential backoffs for rate limits.

### The Flat-File State Bus & Pydantic Handshakes
Agents do not communicate via hidden RPC calls.
Every task handoff is a strictly typed Pydantic schema (`InterAgentHandshake`).
When an agent finishes a block of work, it invokes the `mailroom_routing` skill, which serializes the Handshake out to a Markdown file with YAML frontmatter, and writes it to the next agent's `.agents/inbox/`.
This file-based State Bus means you can `cat`, pause, or modify messages *in transit* horizontally between execution bursts.

### ISO-Compliant Flight Recorders
Every single transaction generates a `.state.json` file telemetry trace in the `.agents/active/` directory. This acts as a flight recorder, mapping the precise start timestamp, tool mounting success, LLM validation steps, and crash tracebacks.

### Directory Schema Blueprint
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
│   ├── providers.yaml  # Model agnostic routing (OpenAI, Anthropic, Groq, Ollama)
│   └── kernel.md       # Universal Workspace SOPs injected into the system prompt
├── core/
│   ├── orchestrator.py # File-watcher Dispatcher
│   ├── runner.py       # The OS Execution Engine
│   ├── factory.py      # LLM Provider Initialization
│   └── vault.py        # Security Validation
└── skills/
    ├── registry.py     # Global OS Tool Registry
    ├── mailroom/       # Cross-workspace I/O Hub
    ├── file_manager/   # Standard file operations
    ├── scaffolder/     # Meta-agent workflow generation
    └── terminal/       # Isolated Bash access
```

## 🔮 The Roadmap: Moving to Multi-Tenancy
The Atomic Agentic OS is currently a high-performance **Single-Tenant MVP**, utilizing a single-threaded orchestrator loop and generalized fail-safes. The next evolutionary phase is **Multi-Tenant Architecture**, where the Orchestrator will seamlessly spin up isolated environments based on dynamic folder structures (), completely removing hardcoded fallbacks and enabling universal scalability.

