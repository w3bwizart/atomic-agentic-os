# ✍️ Content Team Workspace Example

This workspace is a **3-Agent Pipeline** designed to research, draft, and publish highly optimized, long-form LinkedIn posts using the Atomic Agentic OS.

---

## ⚡ The Magic Assembly Line (For Beginners)

Imagine you own a tiny digital newspaper. You have three employees sitting in a row, passing a piece of paper down the desk:
1. **The Researcher**: Reads what the article should be about, Googles the interesting facts, writes a bulleted outline, and hands the paper to the Writer.
2. **The Writer**: Takes the outline, turns it into a really engaging story or draft, and hands the paper to the Editor.
3. **The Editor**: Takes the long story, chops it up into short, punchy, easy-to-read sentences formatted perfectly for a LinkedIn post, and publishes it for you to review.

### 1-Minute Execution Test
If your Orchestrator is already running in your main terminal, you can watch these three agents do this entire process in under 10 seconds.
Open a terminal and run this command:
```bash
cp examples/content_team/.agents/inbox/start_post.md .agents/inbox/start_post.md
```
Open `.agents/review/` to see your finished LinkedIn post!

---

## 🏛️ Architecture Framework (For Senior Developers)

This example demonstrates how to implement a specialized, multi-agent linear pipeline using explicit constraint boundaries within the OS.

### 1. Hardcoded Routing via `kernel.md`
The `kernel.md` acts as the System Prompt payload for the workspace. Notice how it explicitly forces the agents to use the `InterAgentHandshake` schema via the `mailroom_routing` skill to pass payloads sequentially (`researcher` -> `writer` -> `editor`). This ensures immutability; agents do not look backward.

### 2. Isolated Workforce via `workforce.yaml`
The roles, descriptions, and tools are narrowly scoped:
- Only the `editor` is authorized with the `file_management` skill to drop the final post payload into `.agents/review/`. 
- The `researcher` and `writer` only possess the `mailroom_routing` skill, meaning they physically **cannot** write finalized files to the review disk, naturally forcing compliance with the linear pipeline architecture.

### 3. Transparent LLM Context
Because the `InterAgentHandshake` serializes to Markdown, the entire context of the previous agent's execution is passed down the assembly line as a raw text string, reducing continuous context-window bloat while retaining high-fidelity instruction adherence.
