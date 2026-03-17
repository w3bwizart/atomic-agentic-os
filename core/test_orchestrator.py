import unittest
import os
import json
import shutil
from pathlib import Path
from core.orchestrator import InboxHandler

class TestOrchestrator(unittest.TestCase):
    def setUp(self):
        # Create a sandboxed inbox for testing
        self.test_dir = Path(".agents_test")
        self.inbox = self.test_dir / "inbox"
        self.inbox.mkdir(parents=True, exist_ok=True)
        
        # We need to mock workforce for the handler
        self.workforce_dir = Path("config")
        self.workforce_dir.mkdir(exist_ok=True)
        with open(self.workforce_dir / "workforce.yaml", 'w') as f:
            f.write('agents:\n  - id: "dictator"\n    role: "Strategy"')

    def tearDown(self):
        # Clean up
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_parse_frontmatter_valid(self):
        handler = InboxHandler()
        content = "---\ntask_id: \"TEST-1\"\nagent_id: \"dictator\"\n---\nHello"
        meta, body = handler.parse_frontmatter(content)
        self.assertEqual(meta.get("task_id"), "TEST-1")
        self.assertEqual(body, "Hello")

    def test_parse_frontmatter_invalid(self):
        handler = InboxHandler()
        content = "No frontmatter here"
        meta, body = handler.parse_frontmatter(content)
        self.assertEqual(meta, {})
        self.assertEqual(body, "No frontmatter here")

if __name__ == '__main__':
    unittest.main()
