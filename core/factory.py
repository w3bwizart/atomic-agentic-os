import os
import yaml
import logging
from pathlib import Path
from dotenv import load_dotenv

import instructor
from openai import OpenAI
from anthropic import Anthropic

load_dotenv()

logger = logging.getLogger("Factory")

def get_llm_provider(agent_id: str):
    """
    Reads config/providers.yaml, determines the assigned provider for the agent,
    and returns an initialized instructor client.
    """
    providers_path = Path("config/providers.yaml")
    if not providers_path.exists():
        logger.error("providers.yaml not found.")
        return None, None

    with open(providers_path, 'r') as f:
        config = yaml.safe_load(f)

    routing = config.get("routing", {})
    provider_name = routing.get(agent_id)

    if not provider_name:
        logger.warning(f"No routing found for {agent_id}. Defaulting to safe ollama fallback.")
        provider_name = "ollama"

    provider_config = config.get("providers", {}).get(provider_name, {})
    model = provider_config.get("model", "gpt-4o")

    logger.info(f"Initializing {provider_name} ({model}) for agent {agent_id}")

    if provider_name == "openai":
        api_key = provider_config.get("api_key")
        if api_key == "ENV_VAR": api_key = os.environ.get("OPENAI_API_KEY", "dummy-key")
        client = instructor.from_openai(OpenAI(api_key=api_key))
        return client, model

    elif provider_name == "anthropic":
        api_key = provider_config.get("api_key")
        if api_key == "ENV_VAR": api_key = os.environ.get("ANTHROPIC_API_KEY", "dummy-key")
        client = instructor.from_anthropic(Anthropic(api_key=api_key))
        return client, model

    elif provider_name == "groq":
        from openai import OpenAI
        api_key = provider_config.get("api_key")
        if api_key == "ENV_VAR": api_key = os.environ.get("GROQ_API_KEY", "dummy-key")
        
        client = instructor.from_openai(OpenAI(
            api_key=api_key,
            base_url="https://api.groq.com/openai/v1"
        ))
        return client, model

    elif provider_name == "ollama":
        base_url = provider_config.get("base_url", "http://localhost:11434/v1")
        # Ollama supports OpenAI compatible endpoints
        client = instructor.from_openai(OpenAI(base_url=base_url, api_key="ollama"))
        return client, model

    else:
        logger.error(f"Unsupported provider: {provider_name}")
        return None, None
