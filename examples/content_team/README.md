# ✍️ Content Team Workspace Example

This workspace is a **3-Agent Pipeline** designed to research, draft, and publish highly optimized, long-form LinkedIn posts using the Atomic Agentic OS.

## 🏗️ Architecture

The workspace utilizes three distinct agents acting in an assembly line:

1. **`researcher`**: Gathers the initial facts and structures the core arguments.
2. **`writer`**: Takes the structured outline and weaves it into an engaging narrative draft.
3. **`editor`**: Formats the final piece specifically for LinkedIn (hooks, spacing, CTAs) and saves the final output.

## 🚀 How to Run the Test

1. Ensure the main Atomic Agentic OS environment is set up (see root `README.md`).
2. The orchestrator must be running. If not, start it from the root directory:
   ```bash
   PYTHONPATH=. python3 core/orchestrator.py
   ```
3. To trigger the pipeline, simply copy the provided sample handshake into the main OS root inbox (`.agents/inbox/`), or if the orchestrator supports workspace-specific watching, drop it in this workspace's inbox.
   
   If running against the global root orchestrator, copy the setup:
   ```bash
   cp examples/content_team/config/workforce.yaml config/workforce.yaml
   cp examples/content_team/config/kernel.md config/kernel.md
   cp examples/content_team/.vault/policy.json .vault/policy.json
   
   # Trigger the workflow
   cp examples/content_team/.agents/inbox/start_post.md .agents/inbox/start_post.md
   ```

4. Watch the terminal as the `researcher` picks up the task, uses the `mailroom` skill to hand it to the `writer`, who then hands it to the `editor`.
5. The final LinkedIn post will be generated as a Markdown file in `.agents/review/`.

## 🧠 Why This Pattern Works
- **Atomic Specialization**: Each agent has a single, well-defined role, significantly reducing AI hallucination.
- **Observable State**: Since agents use the `mailroom` skill to pass work via `InterAgentHandshake` markdown files, you can inspect the exact state and payload at every step in the `.agents/inbox/` or `.agents/active/` directories.
- **Scalability**: Want to add a `fact-checker` or an `image-generator`? Just add them to `workforce.yaml` and update the `kernel.md` workflow.
