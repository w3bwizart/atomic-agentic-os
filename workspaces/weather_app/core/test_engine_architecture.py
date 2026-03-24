import unittest
import shutil
from pathlib import Path

from core.schemas.atom_handshake import InterAgentHandshakeAtom
from skills.mailroom_routing.tool import MailroomSkill

class TestEngineArchitecture(unittest.TestCase):
    def setUp(self):
        # Create a mock workspace environment
        self.workspace_root = Path("workspaces")
        self.marketing_os = self.workspace_root / "marketing_os" / ".organism_agents" / "inbox"
        self.marketing_os.mkdir(parents=True, exist_ok=True)
        
        self.local_inbox = Path(".organism_agents/inbox")
        self.local_inbox.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.workspace_root, ignore_errors=True)
        shutil.rmtree(Path(".organism_agents"), ignore_errors=True)

    def test_handshake_serialization(self):
        handshake = InterAgentHandshakeAtom(
            sender_id="copywriter",
            sender_workspace="marketing_os",
            receiver_id="editor",
            priority="high",
            directive="Review attached copy payload for grammar.",
            payload={"draft": "Hello word."},
            callback_required=True
        )
        
        md_output = handshake.to_markdown_file()
        
        # Verify strict frontmatter OS injection
        self.assertIn("task_id: ", md_output)
        self.assertIn("organism_agent_id: editor", md_output)
        self.assertIn("priority: high", md_output)
        
        # Verify strict payload construction
        self.assertIn("## Directive\nReview attached copy payload for grammar.", md_output)
        self.assertIn("## Payload\n```json\n{\n  \"draft\": \"Hello word.\"\n}\n```", md_output)

    def test_mailroom_local_routing(self):
        mailroom = MailroomSkill()
        handshake = InterAgentHandshakeAtom(
            sender_id="dictator",
            sender_workspace="root",
            receiver_id="worker",
            directive="Local task."
        )
        
        result = mailroom.run(handshake)
        self.assertIn("successfully dispatched", result)
        
        expected_file = self.local_inbox / f"{handshake.handshake_id}.md"
        self.assertTrue(expected_file.exists())

    def test_mailroom_cross_workspace_routing(self):
        mailroom = MailroomSkill()
        mailroom.workspace_dir = self.workspace_root / "marketing_os"
        handshake = InterAgentHandshakeAtom(
            sender_id="root_dispatch",
            sender_workspace="marketing_os",
            receiver_id="seo_agent",
            directive="Optimize index.",
            priority="critical"
        )
        
        result = mailroom.run(handshake)
        self.assertIn("successfully dispatched", result)
        
        expected_file = self.marketing_os / f"{handshake.handshake_id}.md"
        self.assertTrue(expected_file.exists())
        
        # Verify content was physically written
        with open(expected_file, 'r') as f:
            content = f.read()
            self.assertIn("organism_agent_id: seo_agent", content)
            self.assertIn("priority: critical", content)

if __name__ == '__main__':
    unittest.main()
