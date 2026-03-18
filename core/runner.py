"""
LLM Runner (The Engine)
This module acts as the model-agnostic runtime for the Atomic Agentic OS.
It is an immutable "V8" engine that reads a Workspace Cartridge and strictly
executes it according to ISO compliance and traceability standards.
"""
import json
import logging
from pathlib import Path
from datetime import datetime
import time

from atomic_agents.agents.atomic_agent import AtomicAgent, AgentConfig
from atomic_agents.context.system_prompt_generator import SystemPromptGenerator

from core.factory import get_llm_provider
from skills.registry import get_tool_class
from core.vault import check_permission
from core.schemas.handshake import InterAgentHandshake

logger = logging.getLogger("LLMRunner")

def execute_agent_task(task_id: str, agent_id: str, agent_config: dict, body: str, state_file: Path, sops: str):
    """
    The Core Execution Pipeline.
    Strictly standardizes the processing of a State Bus event using Atomic-Agents.
    
    Args:
        task_id: The unique correlation ID for the transaction (often the Handshake ID).
        agent_id: The identifier of the agent defined in workforce.yaml.
        agent_config: The explicit dictionary of the agent's capabilities (role, tools).
        body: The declarative task instructions (often serialized markdown from a Handshake).
        state_file: The `.state.json` path acting as the flight recorder for this run.
        sops: Workspace-level Standard Operating Procedures injected into the kernel.
    """
    logger.info(f"V8 Engine: Booting execution for {task_id} assigned to {agent_id}.")
    
    # ---------------------------------------------------------
    # 1. FLIGHT RECORDER INITIALIZATION (Traceability)
    # ---------------------------------------------------------
    try:
        with open(state_file, 'r') as f:
            state_data = json.load(f)
    except Exception:
        state_data = {}

    state_data["current_step"] = "initializing_engine"
    state_data["timestamp_start"] = datetime.utcnow().isoformat()
    with open(state_file, 'w') as f: json.dump(state_data, f, indent=2)

    # ---------------------------------------------------------
    # 2. CONTEXT INJECTION (The "Paper")
    # ---------------------------------------------------------
    # We strictly isolate the Agent's specific role from the universal system SOPs.
    system_prompt = SystemPromptGenerator(
        background=[
            "You are a specialized Agent operating within the V8 Atomic Agentic OS runtime.",
            f"Your strict identity ID is: {agent_id}.",
            f"Your designated Role is: {agent_config.get('role', 'Generic Worker')}.",
            f"Role Explicit Description: {agent_config.get('description', 'No description provided.')}"
        ],
        steps=[
            "1. Read the provided Task Directive carefully.",
            "2. Identify the required output state format.",
            "3. Utilize your strictly injected tools to accomplish the task.",
            "4. Never hallucinate API calls or external systems not provided via tools."
        ],
        output_instructions=[
            "Universal Workspace Standard Operating Procedures (SOPs):",
            sops
        ]
    )

    # ---------------------------------------------------------
    # 3. BRAIN ALLOCATION (Model Agnosticism)
    # ---------------------------------------------------------
    client, model = get_llm_provider(agent_id)
    if not client:
        logger.error(f"V8 Engine Alert: Failed to mount LLM provider for {agent_id}. Halting.")
        state_data["current_step"] = "failed_llm_mount"
        with open(state_file, 'w') as f: json.dump(state_data, f, indent=2)
        return

    # ---------------------------------------------------------
    # 4. SKILL MOUNTING (Atomic Molecules)
    # ---------------------------------------------------------
    # Tools are dynamically injected, but gated by the strict .vault/policy.json RBAC.
    requested_skills = agent_config.get('skills', [])
    authorized_tools = []
    
    for skill in requested_skills:
        if check_permission(agent_id, skill):
            tool_class = get_tool_class(skill)
            if tool_class:
                tool_instance = tool_class()
                # Inject local state awareness into the tool if required
                if hasattr(tool_instance, 'state_file') or skill == 'terminal_access':
                    tool_instance.state_file = state_file
                authorized_tools.append(tool_instance)
                logger.info(f"V8 Tool Mount: Successfully bound {skill} to {agent_id}.")
            else:
                logger.warning(f"V8 Tool Mount Error: Skill '{skill}' authorized but missing from Runtime Registry.")
        else:
            logger.warning(f"SECURITY BLOCK: {agent_id} illegally attempted to load '{skill}'.")

    # ---------------------------------------------------------
    # 5. AGENT INSTANTIATION (The Organism)
    # ---------------------------------------------------------
    agent = AtomicAgent(
        config=AgentConfig(
            client=client,
            model=model,
            system_prompt_generator=system_prompt,
            tools=authorized_tools
        )
    )

    # ---------------------------------------------------------
    # 6. EXECUTION & RETRY LOOP (Fault Tolerance)
    # ---------------------------------------------------------
    state_data["current_step"] = "executing_llm"
    with open(state_file, 'w') as f: json.dump(state_data, f, indent=2)

    final_response = ""
    max_retries = 3
    retry_delay = 2
    execution_success = False

    try:
        # Diagnostic trap for safe testing pipelines without wasting API credits
        api_key = getattr(client, "api_key", getattr(getattr(client, "client", None), "api_key", ""))
        if api_key in ["dummy-key", "ollama", "ENV_VAR"]:
            final_response = f"[V8 Engine Diagnostic] Acknowledged payload by {agent_id}."
            execution_success = True
        else:
            # The strict run execution
            for attempt in range(max_retries):
                try:
                    response = agent.run(agent.input_schema(chat_message=body))
                    final_response = response.chat_message
                    
                    if not final_response or final_response.strip() == "":
                        logger.warning(f"V8 Execution Warning: {agent_id} generated an empty response. Marking failure.")
                        state_data["current_step"] = "failed_empty_return"
                    else:
                        execution_success = True
                    break # Break retry loop on successful completion
                    
                except Exception as llm_e:
                    logger.warning(f"V8 LLM Constraint Error (Attempt {attempt + 1}/{max_retries}) for {agent_id}: {llm_e}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2 # Exponential backoff for rate limits
                    else:
                        logger.error(f"V8 Engine Error: {agent_id} exhausted {max_retries} LLM retries. Fatal: {llm_e}")
                        final_response = f"V8 Fatal Execution Error: {llm_e}"
                        state_data["current_step"] = "failed_retry_exhaustion"
                        
    except Exception as fatal_e:
        logger.error(f"V8 System Panic: Unhandled exception during execution block: {fatal_e}", exc_info=True)
        final_response = f"V8 Engine Panic: {fatal_e}"
        state_data["current_step"] = "failed_system_panic"

    if execution_success:
        state_data["current_step"] = "completed"
        
    # ---------------------------------------------------------
    # 7. EVENT LOGGING (ISO Persistence)
    # ---------------------------------------------------------
    try:
        if hasattr(agent, "memory"):
            if callable(getattr(agent.memory, "model_dump", None)):
                state_data["agent_memory"] = agent.memory.model_dump()
            elif hasattr(agent.memory, "history"):
                state_data["agent_memory"] = [
                    msg.model_dump() if hasattr(msg, "model_dump") else str(msg) 
                    for msg in agent.memory.history
                ]
            else:
                state_data["agent_memory"] = str(agent.memory)
    except Exception as mem_e:
        logger.warning(f"V8 Memory Capture Error: Could not serialize agent history: {mem_e}")

    state_data["timestamp_end"] = datetime.utcnow().isoformat()
    with open(state_file, 'w') as f: json.dump(state_data, f, indent=2)

    # ---------------------------------------------------------
    # 8. TELEMETRY SYNCHRONIZATION
    # ---------------------------------------------------------
    try:
        history_path = Path.home() / ".agent_os_history"
        telemetry_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "os_path": str(Path.cwd()),
            "task_id": task_id,
            "agent_id": agent_id,
            "status": state_data.get("current_step", "unknown_fault")
        }
        with open(history_path, 'a') as f:
            f.write(json.dumps(telemetry_entry) + "\n")
    except Exception as telemetry_error:
        logger.warning(f"V8 Telemetry Failure: Cannot write to .agent_os_history: {telemetry_error}")

    # ---------------------------------------------------------
    # 9. RESULT DISPATCH (Artifact Generation)
    # ---------------------------------------------------------
    review_dir = Path(".agents/review")
    review_dir.mkdir(parents=True, exist_ok=True)
    review_file = review_dir / f"{task_id}_report.md"

    with open(review_file, 'w') as f:
        f.write(f"# V8 Execution Report: {task_id}\n")
        f.write(f"**Agent Segment:** {agent_id}\n")
        f.write(f"**Execution Status:** {'Success' if execution_success else 'FAILED'}\n")
        f.write(f"**Timestamp:** {state_data['timestamp_end']}\n\n")
        f.write(f"## Response Payload:\n{final_response}\n")
        f.write(f"\n## Modules Activated:\n")
        if authorized_tools:
            for tool in authorized_tools:
                f.write(f"- {tool.__class__.__name__}\n")
        else:
            f.write("- (None)\n")

    logger.info(f"V8 Engine: Task {task_id} successfully dispatched to {review_file}.")
