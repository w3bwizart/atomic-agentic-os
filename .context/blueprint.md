---
description: "Master Context Injection: Atomic Agentic OS (The V8 of AI Agents)"
---

# 🛸 ANTIGRAVITY MISSION: ATOMIC AGENTIC OS

**Role:** Senior AI Systems Architect.
**Project:** Atomic Agentic OS (A V8-style Runtime for AI).
**Architecture Pattern:** Atomic Design (Atoms → Molecules → Organisms → Workspaces → OS).

## 1. Technical Architecture (The "Shredder")
* **The Engine (`runner.py`):** A model-agnostic runtime using the `atomic-agents` framework. It must be heavily commented. It reads a "Cartridge" (Workspace) and executes it.
* **The Cartridge (Workspace):** Contains `workforce.yaml` (Agent definitions), `kernel.md` (System DNA), and `.agents/inbox` (The Trigger).
* **The Factory:** Handles multi-provider integration (Ollama, Gemini, Claude, DeepSeek) via a unified interface.
* **The State Bus:** A file-based communication layer (`.state.json`). Agents talk across workspaces by moving "Handshake Atoms" (JSON) between inboxes.
* **Connectivity:** Supports **MCP (Model Context Protocol)** and standard REST APIs as "Atomic Molecules" (Skills).

## 2. The Implementation Goals
1.  **Model Agnosticism:** The system must swap brains instantly via `config/providers.yaml`.
2.  **Strict Traceability:** Every execution must be logged for ISO compliance. The code (Engine) is immutable; the behavior (Markdown) is declarative.
3.  **Scalability:** Support for 1,000+ workspaces running in isolated Docker containers sharing a root `/workspaces` volume for inter-agent "mail."
4.  **Agentic UI:** Future-proofing for "Widgets"—UI components that render "State Atoms" (JSON) produced by agents.

## 3. Immediate Focus Tasks: The "Handshake & Runner"
1.  **Finalize the `InterAgentHandshake` Atom:** Create a Pydantic model that defines how one workspace requests data from another (Priority, Payload, Callback Path).
2.  **Refactor `core/runner.py`:** Write a clean, exhaustively commented engine that:
    * Loads the `workforce.yaml`.
    * Initializes the `atomic-agents` environment.
    * Executes the task and saves the flight recorder state to `.state.json`.
3.  **Implement the "Mailroom" Skill:** Create a skill that allows an agent to move a file from its `active/` folder to a neighbor's `inbox/`.
