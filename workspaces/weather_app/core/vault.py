import json
import logging
import os
from pathlib import Path

# Setup basic logging
logger = logging.getLogger(__name__)

VAULT_POLICY_PATH = Path(".vault/atom.policy.json")

def check_permission(organism_agent_id: str, skill_name: str, workspace_dir: str = ".") -> bool:
    """
    Check if an agent has permission to use a specific skill.
    Reads from local workspace policy, falling back to global policy.
    """
    vault_path = Path(workspace_dir) / ".vault" / "atom.policy.json"
    if not vault_path.exists():
        vault_path = Path(".vault/atom.policy.json")

    if not vault_path.exists():
        logger.warning(f"Vault policy file not found at {vault_path}.")
        return False

    try:
        with open(VAULT_POLICY_PATH, 'r') as f:
            policy = json.load(f)

        permissions = policy.get("permissions", {})
        agent_permissions = permissions.get(organism_agent_id, [])

        # In actual system, we might have roles or wildcard permissions
        if skill_name in agent_permissions:
            return True
        else:
            logger.warning(f"Security Violation: Agent {organism_agent_id} denied access to {skill_name}")
            return False

    except Exception as e:
        logger.error(f"Error reading vault policy: {e}")
        return False
