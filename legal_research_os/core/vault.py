import json
import logging
import os
from pathlib import Path

# Setup basic logging
logger = logging.getLogger(__name__)

VAULT_POLICY_PATH = Path(".vault/policy.json")

def check_permission(agent_id: str, skill_name: str) -> bool:
    """
    Check if an agent has permission to use a specific skill.
    Reads from .vault/policy.json.
    """
    if not VAULT_POLICY_PATH.exists():
        logger.warning(f"Vault policy file not found at {VAULT_POLICY_PATH}.")
        return False

    try:
        with open(VAULT_POLICY_PATH, 'r') as f:
            policy = json.load(f)

        permissions = policy.get("permissions", {})
        agent_permissions = permissions.get(agent_id, [])

        # In actual system, we might have roles or wildcard permissions
        if skill_name in agent_permissions:
            return True
        else:
            logger.warning(f"Security Violation: Agent {agent_id} denied access to {skill_name}")
            return False

    except Exception as e:
        logger.error(f"Error reading vault policy: {e}")
        return False
