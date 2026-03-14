import os
from atomic_agents.agents.atomic_agent import AtomicAgent, AgentConfig
import instructor
from openai import OpenAI

# Mock LLM
client = instructor.from_openai(OpenAI(api_key="dummy-key"))

agent = AtomicAgent(config=AgentConfig(client=client, model="gpt-4o"))
print("Memory hasattr:", hasattr(agent, "memory"))
if hasattr(agent, "memory"):
    print("Memory dict:", agent.memory.__dict__)
