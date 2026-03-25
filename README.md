# Atomic Agentic OS

A headless, autonomously-orchestrated Artificial Intelligence Operating System secured by Role-Based Access Controls and visualized over a Cyberpunk Web Node. 

By unifying isolated agent state tracking, decentralized orchestration loops, and global telemetry, this framework enables you to dynamically "scaffold" hyper-specialized Agentic Workspaces on the fly.

---

## Quickstart Tutorial: The 3-Agent Content Team

This tutorial walks you through setting up a specialized OS workspace for a 3-agent content creation team (Writer, Editor, Publisher) and executing their first collaborative task.

### Step 1: Start the Dashboard and Mother Ship
Open two terminal windows in the root directory of the repository:

**Terminal 1 (Telemetry Dashboard):**
```bash
python3 dashboard/server.py
```
*Open `http://localhost:8180` in your web browser to watch the global execution log.*

**Terminal 2 (Mother Ship Orchestrator):**
```bash
PYTHONPATH=. venv/bin/python core/orchestrator.py
```

### Step 2: Scaffold the Content Team Workspace
The Mother Ship monitors the root `.organism_agents/inbox/` for commands. To tell the root OS `assistant` to build your specialized workspace, create a file named `scaffold_team.md` inside `.organism_agents/inbox/` with the following content:

```yaml
---
task_id: SCAFFOLD-001
organism_agent_id: assistant
---
Please create a new workspace using the `scaffold_skill`. 

project_name: "content_creation_team"
description: "A specialized 3-agent content factory for writing, editing, and publishing."
team:
  - id: "writer"
    role: "Content Writer"
    description: "Writes initial drafts."
  - id: "editor"
    role: "Content Editor"
    description: "Proofreads drafts and ensures high grammatical quality."
  - id: "publisher"
    role: "Content Publisher"
    description: "Finalizes the articles for release."
```

*Within 60 seconds, check the dashboard. The `assistant` will process the ticket and dynamically generate `workspaces/content_creation_team/`.*

### Step 3: Boot Up the Content Team OS
Now that the Mother Ship has scaffolded your new workspace, you need to boot its local orchestrator up. Open a third terminal window:

**Terminal 3 (Content Team Orchestrator):**
```bash
cd workspaces/content_creation_team
PYTHONPATH=../../ ../../venv/bin/python core/orchestrator.py
```

### Step 4: Execute a Collaborative Task
To trigger the new pipeline, we just drop a task into the newly created Content Team's inbox. Create a file named `write_article.md` inside `workspaces/content_creation_team/.organism_agents/inbox/` with the following content:

```yaml
---
task_id: CONTENT-001
organism_agent_id: writer
---
Please write a short 3-paragraph article about the future of Artificial Intelligence Operating Systems. 
Once you are done, use the mailroom_routing skill to pass the article to the `editor`. The `editor` must then proofread it and pass it to the `publisher` for finalization.
```

*Watch your Dashboard! You will see the Writer, Editor, and Publisher organically passing the workload downstream through their local state bus until the final article is completed and moved to the `review/` folder!*