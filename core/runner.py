"""
LLM Runner (The Engine)
This module acts as the model-agnostic runtime for the Atomic Agentic OS.
It is an immutable "OS" engine that reads a Workspace Cartridge and strictly
executes it according to ISO compliance and traceability standards.
"""
import json
import logging
from pathlib import Path
from datetime import datetime
import time
import yaml

from atomic_agents.agents.atomic_agent import AtomicAgent as OrganismAtomicAgent, AgentConfig
from atomic_agents.context.system_prompt_generator import SystemPromptGenerator

import importlib.util
from core.factory import get_llm_provider
from core.vault import check_permission
from core.schemas.atom_handshake import InterAgentHandshakeAtom

logger = logging.getLogger("LLMRunner")

def execute_organism_agent_task(task_id: str, organism_agent_id: str, agent_config: dict, body: str, state_file: Path, sops: str, workspace_dir: str = "."):
    """
    The Core Execution Pipeline.
    Strictly standardizes the processing of a State Bus event using Atomic-Agents.
    
    Args:
        task_id: The unique correlation ID for the transaction (often the Handshake ID).
        organism_agent_id: The identifier of the agent defined in organism.workforce.yaml.
        agent_config: The explicit dictionary of the agent's capabilities (role, tools).
        body: The declarative task instructions (often serialized markdown from a Handshake).
        state_file: The `.state.json` path acting as the flight recorder for this run.
        sops: Workspace-level Standard Operating Procedures injected into the kernel.
    """
    logger.info(f"Atomic Engine: Booting execution for {task_id} assigned to {organism_agent_id}.")
    
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
            "You are a specialized Agent operating within the OS Atomic Agentic OS runtime.",
            f"Your strict identity ID is: {organism_agent_id}.",
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
            "CRITICAL: If you are instructed to use a tool to output your work (like InterAgentHandshakeAtom), you MUST NOT output conversational text. You MUST directly invoke the tool to deliver your payload. Failure to use the tool will cause the system to crash.",
            "Universal Workspace Standard Operating Procedures (SOPs):",
            sops
        ]
    )

    # ---------------------------------------------------------
    # 3. BRAIN ALLOCATION (Model Agnosticism)
    # ---------------------------------------------------------
    client, model = get_llm_provider(organism_agent_id)
    if not client:
        logger.error(f"Atomic Engine Alert: Failed to mount LLM provider for {organism_agent_id}. Halting.")
        state_data["current_step"] = "failed_llm_mount"
        with open(state_file, 'w') as f: json.dump(state_data, f, indent=2)
        return

    # ---------------------------------------------------------
    # 4. SKILL MOUNTING (Atomic Molecules)
    # ---------------------------------------------------------
    # Tools are dynamically injected, but gated by the strict .vault/atom.policy.json RBAC.
    requested_skills = agent_config.get('skills', [])
    authorized_tools = []
    
    for skill in requested_skills:
        if check_permission(organism_agent_id, skill, workspace_dir=workspace_dir):
            tool_class = None
            
            # 1. STRICT TENANT ISOLATION: Always attempt to load the custom Python script directly from the Workspace first.
            skill_path = Path(workspace_dir) / "skills" / skill / "tool.py"
            
            # 2. GLOBAL FALLBACK: If running at the Root OS (e.g. system maintenance), fallback to the core skills menu.
            if not skill_path.exists() and workspace_dir == ".":
                skill_path = Path("skills") / skill / "tool.py"
                
            if skill_path.exists():
                module_name = f"dynamic_skill_{skill}"
                spec = importlib.util.spec_from_file_location(module_name, str(skill_path))
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    try:
                        spec.loader.exec_module(module)
                        # Extract the BaseTool class
                        from atomic_agents.base.base_tool import BaseTool
                        for attr_name in dir(module):
                            attr = getattr(module, attr_name)
                            if isinstance(attr, type) and issubclass(attr, BaseTool) and attr is not BaseTool:
                                tool_class = attr
                                break
                    except Exception as e:
                        logger.error(f"OS Tool Mount Error: Failed to compile Python module {skill_path}: {e}")
            
            if tool_class:
                tool_instance = tool_class()
                # Inject local state awareness into the tool if required
                if hasattr(tool_instance, 'state_file') or skill == 'terminal_access':
                    tool_instance.state_file = state_file
                tool_instance.workspace_dir = workspace_dir
                authorized_tools.append(tool_instance)
                logger.info(f"OS Tool Mount: Successfully bound {skill} to {organism_agent_id}.")
            else:
                if not skill_path.exists():
                    logger.warning(f"OS Tool Mount Error: Skill '{skill}' missing physical Python script at {skill_path}.")
                else:
                    logger.warning(f"OS Tool Mount Error: Skill '{skill}' found but missing a valid BaseTool inheritance.")
        else:
            logger.warning(f"SECURITY BLOCK: {organism_agent_id} illegally attempted to load '{skill}'.")

    # ---------------------------------------------------------
    # 5. AGENT INSTANTIATION (The Organism)
    # ---------------------------------------------------------
    agent = OrganismAtomicAgent(
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
            final_response = f"[Atomic Engine Diagnostic] Acknowledged payload by {organism_agent_id}."
            execution_success = True
        else:
            # The strict run execution
            for attempt in range(max_retries):
                try:
                    response = agent.run(agent.input_schema(chat_message=body))
                    final_response = response.chat_message
                    
                    if not final_response or final_response.strip() == "":
                        logger.warning(f"OS Execution Warning: {organism_agent_id} generated an empty response. Marking failure.")
                        state_data["current_step"] = "failed_empty_return"
                    else:
                        execution_success = True
                        
                        # OS SYNTHETIC ROUTING (Dynamic Workspace Extraction)
                        try:
                            receiver = None
                            directive = "Process the attached payload."
                            
                            workforce_path = Path(workspace_dir) / "config" / "organism.workforce.yaml"
                            if workforce_path.exists():
                                with open(workforce_path, 'r') as f:
                                    workforce_data = yaml.safe_load(f).get("agents", [])
                                # Find next agent
                                for i, w_agent in enumerate(workforce_data):
                                    if w_agent['id'] == organism_agent_id:
                                        if i + 1 < len(workforce_data):
                                            receiver = workforce_data[i+1]['id']
                                            directive = workforce_data[i+1].get('description', directive)
                                        break
                            
                            payload_data = {"raw_llm_output": final_response}
                            
                            if receiver:
                                logger.info(f"OS Synthetic Route: Forcing Handshake from {organism_agent_id} to {receiver} in {workspace_dir}.")
                                inbox_dir = Path(workspace_dir) / ".agents" / "inbox"
                                inbox_dir.mkdir(parents=True, exist_ok=True)
                                handshake = InterAgentHandshakeAtom(
                                    handshake_id=task_id, sender_workspace=Path(workspace_dir).name, 
                                    sender_id=organism_agent_id, receiver_id=receiver, 
                                    payload=payload_data, directive=directive
                                )
                                with open(inbox_dir / f"{handshake.handshake_id}.md", "w") as hf:
                                    hf.write(handshake.to_markdown_file())
                                    
                            else:
                                logger.info(f"OS Synthetic Route: Terminal agent finished. Saving payload to {workspace_dir}/review.")
                                review_dir = Path(workspace_dir) / ".agents" / "review"
                                review_dir.mkdir(parents=True, exist_ok=True)
                                review_post = review_dir / f"{task_id}_final_output.md"
                                with open(review_post, "w") as f:
                                    f.write(final_response)
                                    
                        except Exception as parse_e:
                            logger.warning(f"OS Synthetic Routing failed: {parse_e}")
                            
                    break # Break retry loop on successful completion
                    
                except Exception as llm_e:
                    logger.warning(f"OS LLM Constraint Error (Attempt {attempt + 1}/{max_retries}) for {organism_agent_id}: {llm_e}")
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        retry_delay *= 2 # Exponential backoff for rate limits
                    else:
                        logger.error(f"Atomic Engine Error: {organism_agent_id} exhausted {max_retries} LLM retries. Fatal: {llm_e}")
                        final_response = f"OS Fatal Execution Error: {llm_e}"
                        state_data["current_step"] = "failed_retry_exhaustion"
                        
    except Exception as fatal_e:
        logger.error(f"OS System Panic: Unhandled exception during execution block: {fatal_e}", exc_info=True)
        final_response = f"Atomic Engine Panic: {fatal_e}"
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
        logger.warning(f"OS Memory Capture Error: Could not serialize agent history: {mem_e}")

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
            "organism_agent_id": organism_agent_id,
            "status": state_data.get("current_step", "unknown_fault")
        }
        with open(history_path, 'a') as f:
            f.write(json.dumps(telemetry_entry) + "\n")
    except Exception as telemetry_error:
        logger.warning(f"OS Telemetry Failure: Cannot write to .agent_os_history: {telemetry_error}")

    # ---------------------------------------------------------
    # 9. RESULT DISPATCH (Artifact Generation)
    # ---------------------------------------------------------
    review_dir = Path(workspace_dir) / ".agents" / "review"
    review_dir.mkdir(parents=True, exist_ok=True)
    review_file = review_dir / f"{task_id}_report.md"

    with open(review_file, 'w') as f:
        f.write(f"# OS Execution Report: {task_id}\n")
        f.write(f"**Agent Segment:** {organism_agent_id}\n")
        f.write(f"**Execution Status:** {'Success' if execution_success else 'FAILED'}\n")
        f.write(f"**Timestamp:** {state_data['timestamp_end']}\n\n")
        f.write(f"## Response Payload:\n{final_response}\n")
        f.write(f"\n## Modules Activated:\n")
        if authorized_tools:
            for tool in authorized_tools:
                f.write(f"- {tool.__class__.__name__}\n")
        else:
            f.write("- (None)\n")

    logger.info(f"Atomic Engine: Task {task_id} successfully dispatched to {review_file}.")
