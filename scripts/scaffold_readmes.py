import os
from pathlib import Path

targets = [
    Path(".organism_agents"),
    Path("examples/content_team/.organism_agents"),
    Path("workspaces/content_team/.organism_agents")
]

readmes = {
    "inbox": "# 📥 The Inbox (Task Entry)\nThis directory acts as the entry point for the OS State Bus.\nDrop a `.md` payload (an `InterAgentHandshakeAtom` or trigger file) in here. \nThe Orchestrator daemon actively watches this folder and will immediately dispatch it to the appropriate Organism (Agent).\n",
    "active": "# ⚙️ Active Processing (Flight Recorders)\nThis directory temporarily holds `.state.json` files while an Organism is actively thinking.\nThese act as black-box flight recorders, capturing exact timestamps, LLM traces, and crash faults in real-time. \nOnce a task completes (Success or Fail), the State Bus moves the final output to the `review/` folder.\n",
    "review": "# 🔍 Human Review (Output Gate)\nThis directory holds the final result of an Organism's execution (`*_report.md` or `_final_output.md`).\nIf a task finishes, or critically fails after exhausting retry limits, the final OS diagnostic report is placed here for human review.\n",
    "logs": "# 📜 Universal System Logs\nThis directory contains the `system.log`. \nIt captures the entire chronological history of the OS Orchestrator, LLM factory boots, network requests, and API rate limits.\n"
}

for base in targets:
    for folder, content in readmes.items():
        dir_path = base / folder
        dir_path.mkdir(parents=True, exist_ok=True)
        readme_path = dir_path / "README.md"
        with open(readme_path, "w") as f:
            f.write(content)
print("Documentation scaffolds successfully generated for all Workspaces.")
