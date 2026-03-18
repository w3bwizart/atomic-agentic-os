import json
from pathlib import Path
from pydantic import Field
from atomic_agents.context.system_prompt_generator import SystemPromptGenerator
from atomic_agents.base.base_tool import BaseTool

from core.schemas.atom_handshake import InterAgentHandshakeAtom

class MailroomSkill(BaseTool):
    """
    The Atomic Mailroom Molecule.
    Allows an agent to dispatch a strict InterAgentHandshakeAtom payload to another workspace's inbox.
    """
    input_schema = InterAgentHandshakeAtom

    def __init__(self):
        super().__init__()
        self.system_prompt_generator = SystemPromptGenerator(
            background=[
                "You are the Mailroom Gateway.",
                "Your responsibility is to strictly serialize an InterAgentHandshakeAtom Pydantic model into a Markdown file.",
                "This Markdown file is then dropped securely into the target Agent's (or Workspace's) file system inbox."
            ],
            steps=[
                "1. Receive the structured InterAgentHandshakeAtom atom.",
                "2. Generate the serialized Frontmatter + Markdown string.",
                "3. Securely write the file to '.organism_agents/inbox' or the specified workspace's inbox root."
            ]
        )

    def run(self, params: InterAgentHandshakeAtom) -> str:
        """
        Executes the Handshake dispatch.
        """
        try:
            workspace_dir = getattr(self, "workspace_dir", ".")
            inbox_dir = Path(workspace_dir) / ".organism_agents/inbox"
            inbox_dir.mkdir(parents=True, exist_ok=True)
            
            # The exact file payload
            file_name = f"{params.handshake_id}.md"
            target_path = inbox_dir / file_name
            
            # Serialize the Handshake Atom into the OS State Bus contract (Markdown + Frontmatter)
            file_content = params.to_markdown_file()
            
            with open(target_path, "w") as f:
                f.write(file_content)
                
            return f"OS Mailroom: Handshake {params.handshake_id} successfully dispatched to {target_path} for '{params.receiver_id}'."
            
        except Exception as e:
            return f"OS Mailroom Error: Failed to dispatch handshake: {str(e)}"
