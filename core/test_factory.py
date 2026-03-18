import unittest
import os
from pathlib import Path
from core.factory import get_llm_provider

class TestFactory(unittest.TestCase):
    def setUp(self):
        self.config_dir = Path("config")
        self.config_dir.mkdir(exist_ok=True)
        with open(self.config_dir / "providers.yaml", 'w') as f:
            f.write('''
providers:
  openai:
    model: "gpt-4o"
    api_key: "ENV_VAR"
  ollama:
    model: "llama3"
    base_url: "http://localhost:11434/v1"

routing:
  dictator: "openai"
  coder: "ollama"
''')

    def test_routing_openai(self):
        # Given config says dictator = openai
        os.environ["OPENAI_API_KEY"] = "test-key"
        client, model = get_llm_provider("dictator")
        self.assertIsNotNone(client)
        self.assertEqual(model, "gpt-4o")

    def test_routing_fallback_ollama(self):
        # A missing agent should fallback to ollama
        client, model = get_llm_provider("unknown_agent")
        self.assertIsNotNone(client)
        self.assertEqual(model, "llama3")

if __name__ == '__main__':
    unittest.main()
