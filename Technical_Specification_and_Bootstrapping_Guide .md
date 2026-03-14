This document serves as the **Technical Specification and Bootstrapping Guide** for your Agentic OS. You can provide this file to your current system (Antigravity) to scaffold the environment and run the "Hello World" verification.

---

# 🚀 Agentic OS: System Specification & Hello World

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
│   └── skill.md        # System SOPs
├── core/
│   └── orchestrator.py # File-watcher & Logic
└── skills/
    └── terminal/
        └── tool.py     # Example Atomic Skill

```

---

## 2. File Definitions & Examples

### 📂 `config/workforce.yaml`

**Purpose:** Defines the agents available in the workspace and their assigned skills.

```yaml
agents:
  - id: "dictator_01"
    role: "Orchestrator"
    description: "Breaks down inbox requests into atomic tasks."
    skills: ["task_decomposition", "file_management"]

  - id: "lieutenant_coder_01"
    role: "Executor"
    description: "Executes terminal commands and writes code."
    skills: ["terminal_access", "git_management"]

```

### 📂 `config/skill.md`

**Purpose:** The "Bible" containing SOPs that every agent must follow to ensure quality and safety.

```markdown
# System SOPs v1.0

## Terminal Usage
- Always use absolute paths.
- Never delete directories recursively without a backup.
- Use `echo` to verify state before running complex pipes.

## Communication
- Use JSONL for system logs.
- Use Markdown for human-facing reports in the `/review` folder.

```

### 📂 `skills/terminal/tool.py`

**Purpose:** A functional "Atomic Skill" using the `atomic-agents` pattern.

```python
from pydantic import Field
from atomic_agents.lib.base.base_tool import BaseTool

class TerminalCommandConfig(BaseTool.Config):
    command: str = Field(..., description="The shell command to execute.")

class TerminalSkill(BaseTool):
    """Executes a shell command and returns output."""
    def run(self, params: TerminalCommandConfig):
        import subprocess
        result = subprocess.run(params.command, shell=True, capture_output=True, text=True)
        return {"stdout": result.stdout, "stderr": result.stderr}

```

### 📂 `.vault/policy.json`

**Purpose:** Restricts which agents can call specific sensitive skills.

```json
{
  "permissions": {
    "lieutenant_coder_01": ["terminal_access"],
    "dictator_01": ["read_inbox", "write_active"]
  }
}

```

---

## 3. The "Hello World" Test Case

To verify the setup, we will simulate a task where an agent must echo "Hello World" to the console and record the result.

### Step 1: Create the Trigger File

**File:** `.agents/inbox/hello_test.md`

```markdown
---
task_id: "HW-001"
priority: "high"
---
# Task: Hello World
Please use the terminal skill to echo the phrase "Hello World: Agentic OS is Online".
Move the result to the review folder once finished.

```

### Step 2: The Expected Output (Success State)

If the architecture is working, the system should generate the following file after processing:

**File:** `.agents/review/HW-001_result.md`

```markdown
# Task HW-001: Execution Report
**Agent:** lieutenant_coder_01
**Status:** Success

## Terminal Output:
> Hello World: Agentic OS is Online

## Logs:
- [12:00:01] Picked up task from inbox.
- [12:00:02] Initializing TerminalSkill.
- [12:00:03] Executed: `echo "Hello World..."`
- [12:00:04] Task moved to review.

```

---

## 4. Integration with Antigravity

To make this work with your existing setup:

1. **The Watcher:** Have Antigravity monitor the `.agents/inbox/` folder using `watchdog` (Python).
2. **The Loader:** When a `.md` file appears, parse the Frontmatter (the YAML at the top) to identify the task.
3. **The Dispatcher:** Load the `workforce.yaml` and instantiate an `Atomic Agent` equipped with the tools defined in the `skills/` directory.
4. **The SOP Injector:** Always prepend the contents of `config/skill.md` to the agent's system prompt to ensure it follows your vault's rules.