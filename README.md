# 🏗️ The Atomic Agentic OS - Built with Atomic-Agents

Welcome to the **Atomic Agentic OS**, a file-based operating system where specialized AI agents work together in an assembly line to automate your tasks.

Whether you're a starter building your first AI workflow or a Senior AI Architect designing ISO-compliant enterprise systems, this OS scales beautifully to fit your needs.

---

### 🧩 Pluggable Infrastructure (Bring Your Own Backend)
While this OS ships with a zero-dependency **Flat-File State Bus** for frictionless onboarding, the architecture is inherently modular. You can seamlessly swap components as your needs scale:
*   **The OS Inbox** can be swapped out for an enterprise message broker like **Apache Kafka** or **RabbitMQ**.
*   **The Flight Recorders (`.state.json`)** can be migrated to a **Graph/Vector Database** (e.g., Neo4j, Pinecone) to natively power Semantic Memory retrieval over horizontal agentic histories.
*   **The Artifacts (`.md`)** can stream directly into Amazon S3, Azure Blob, or PostgreSQL.

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
   # OLLAMA_API_BASE=http://localhost:11434/v1 (No API key needed for local Ollama!)
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

---

## 🚀 Deployment Patterns

The OS supports different architectural modalities depending on how complex your pipelines are.

### Pattern A: Creating Agents in the Root OS (Global)
If you just need a personal assistant or generic workers that operate on your main OS directory, you can build them directly into the Root OS.

1. **Define your workforce:** Open `config/organism.workforce.yaml` and add an agent (e.g., `id: assistant`).
2. **Assign tools:** Bind global skills inside the YAML configuration.
3. **Feed the task:** Drop a Markdown file (an `InterAgentHandshakeAtom`) into the global `.organism_agents/inbox/`.
   ```markdown
   ---
   task_id: GLOBAL-001
   organism_agent_id: assistant
   ---
   Summarize the contents of my latest project...
   ```
4. The Orchestrator will instantly parse the event and execute the task universally across the repository.

---

### Pattern B: Creating and Feeding Isolated Workspaces (Multi-Tenant)
For complex multi-agent pipelines (like a 3-agent content factory), you should isolate them inside dynamic Workspaces. The OS supports infinite parallel tenant workspaces securely walled off from each other.

1. **Scaffold the Workspace Autonomously:** Instead of manually copying folders, let the Root `assistant` generate it for you! Drop a markdown payload into the global `.organism_agents/inbox/`:
   ```markdown
   ---
   task_id: OS-SCAFFOLD
   organism_agent_id: assistant
   ---
   Use your scaffold tool to create a new isolated workspace called `my_tenant` mirroring the `content_team` architecture.
   ```
2. **Define the Isolated Workforce:** Open the newly generated `workspaces/my_tenant/config/organism.workforce.yaml` and modify your specialized assembly line.
3. **Feed the Workspace:** Drop a task specifically into that tenant's inbox: `workspaces/{tenant_name}/.organism_agents/inbox/`.
4. **Parallel Execution:** The Mother Ship dynamically mounts the local workforce and custom tools, completely walling them off from the global OS context. You can simultaneously feed 10 different workspaces and the engine will spin up 10 asynchronous threads!

---

### Pattern C: Containerized Agents (Docker)
For ultimate isolation, you can containerize the OS Engine or individual agent workspaces using Docker. Because the entire State Bus relies on basic Markdown files, you never have to worry about container networking or exposing ports!

1. **Dockerize the Orchestrator:** Create a basic `Dockerfile` in the root directory that installs your Python `requirements.txt` and runs `core/orchestrator.py`.
2. **Mount the Data Volumes:** When running the container, simply mount your local host directories as volumes so the agent can read and write payloads natively:
   ```bash
   docker run -d --name atomic_os \
     -v ./.organism_agents:/app/.organism_agents \
     -v ./workspaces:/app/workspaces \
     -v ./config:/app/config \
     atomic_agent_os:latest
   ```
3. **Execution from the Host Mac/Linux:** You can now securely run untrusted agent code mathematically sandboxed inside a Linux container, while still seamlessly dropping `.md` tasks securely from your local desktop!

---

## 🧠 Under the Hood (For Senior Developers)

If you are a Senior Engineer, you care about predictability, auditability, and immutability. The Atomic Agentic OS is designed to be a transparent **State Bus**, heavily relying on declarative file systems rather than obfuscated memory stores.

### The OS Execution Pipeline (`core/runner.py`)
At its core, the OS uses a strict, immutable 9-step execution loop powered by `atomic-agents`. When the Orchestrator daemon (`watchdog`) detects a payload, it spins up the Atomic Engine. The engine strictly mounts authorized tools based on Role-Based Access Control (`.vault/policy.json`), loads workspace SOPs into the system prompt, and manages exponential backoffs for rate limits.

### The Flat-File State Bus & Pydantic Handshakes
Agents do not communicate via hidden RPC calls.
Every task handoff is a strictly typed Pydantic schema (`InterAgentHandshakeAtom`).
When an agent finishes a block of work, it invokes the `mailroom_routing` skill, which serializes the Handshake out to a Markdown file with YAML frontmatter, and writes it to the next agent's `.organism_agents/inbox/`.
This file-based State Bus means you can `cat`, pause, or modify messages *in transit* horizontally between execution bursts.

### ISO-Compliant Flight Recorders
Every single transaction generates a `.state.json` file telemetry trace in the `.organism_agents/active/` directory. This acts as a flight recorder, mapping the precise start timestamp, tool mounting success, LLM validation steps, and crash tracebacks.


### Directory Schema Blueprint
```text
.
├── .organism_agents/
│   ├── inbox/          # Task entry point (Handshake Atoms dropped here)
│   ├── active/         # Processing state (Flight Recorders live here)
│   ├── review/         # Human/QA gate (Generated Engine Reports)
│   └── logs/           # Global execution traces
├── .vault/
│   └── policy.json     # RBAC & Tool Permissions
├── config/
│   ├── organism.workforce.yaml # Global Agent identity and roles
│   ├── providers.yaml  # Model agnostic routing (OpenAI, Anthropic, Groq, Ollama)
│   └── kernel.md       # Universal Workspace SOPs injected into the system prompt
├── core/
│   ├── orchestrator.py # File-watcher Dispatcher
│   ├── runner.py       # The OS Execution Engine
│   ├── factory.py      # LLM Provider Initialization
│   └── vault.py        # Security Validation
└── workspaces/             # Isolated Multi-Tenant Architectures
    └── content_team/       # Example Factory Sandbox
```