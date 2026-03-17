import unittest
import json
import os
from pathlib import Path
from core.runner import execute_agent_task

class TestRunner(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(".agents_test")
        self.active_dir = self.test_dir / "active"
        self.review_dir = self.test_dir / "review"
        self.active_dir.mkdir(parents=True, exist_ok=True)
        self.review_dir.mkdir(parents=True, exist_ok=True)
        
        self.state_file = self.active_dir / "TEST-001.state.json"
        with open(self.state_file, 'w') as f:
            json.dump({"current_step": "init"}, f)

        self.agent_config = {
            "role": "tester",
            "description": "test agent",
            "skills": []
        }

    def tearDown(self):
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_runner_diagnostic_mock(self):
        # We test the built-in diagnostic mock that triggers when dummy-key is present
        # Or task_id has specific prefixes. We'll use a mocked API Key scenario.
        
        # Override the review dir locally for test
        import core.runner
        original_path = core.runner.Path
        
        class MockPath:
            def __init__(self, path_str):
                self.path_str = str(path_str)
            def mkdir(self, *args, **kwargs): pass
            def exists(self): return True
            def __truediv__(self, other):
                if "review" in self.path_str:
                    return original_path(str(self.active_dir / other))
                return original_path(self.path_str) / other
                
        core.runner.Path = MockPath
        
        try:
            execute_agent_task(
                task_id="TEST-001",
                agent_id="test_agent",
                agent_config=self.agent_config,
                body="test body",
                state_file=self.state_file,
                sops="test sops"
            )
            
            # Verify state was updated
            with open(self.state_file, 'r') as f:
                state = json.load(f)
            self.assertEqual(state["current_step"], "executing_llm")
            
        finally:
            core.runner.Path = original_path

if __name__ == '__main__':
    unittest.main()
