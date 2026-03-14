"""
Skill Registry: Maps configuration strings to actual BaseTool implementations.
"""
from typing import Dict, Type
from atomic_agents.base.base_tool import BaseTool

# Import required tools
from skills.file_manager.tool import FileManagerSkill
from skills.terminal.tool import TerminalSkill
from skills.dependencies.tool import WaitSkill

TOOL_REGISTRY: Dict[str, Type[BaseTool]] = {
    "file_management": FileManagerSkill,
    "terminal_access": TerminalSkill,
    "read_active_state": WaitSkill,
    "read_review": WaitSkill,
}

def get_tool_class(skill_name: str) -> Type[BaseTool]:
    """Returns the tool class for a given skill string from workforce.yaml."""
    return TOOL_REGISTRY.get(skill_name)

print("\n--- OS Boot: Registering Agentic Skills ---")
for tool_name in TOOL_REGISTRY:
    print(f" -> [Registered] {tool_name}")
print("-------------------------------------------\n")
