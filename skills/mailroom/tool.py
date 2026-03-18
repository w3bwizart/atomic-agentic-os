import json
from pathlib import Path
from pydantic import Field
from atomic_agents.context.system_prompt_generator import SystemPromptGenerator
from atomic_agents.base.base_tool import BaseTool

from core.schemas.handshake import InterAgentHandshake

class MailroomSkill(BaseTool):
    """
    The Atomic Mailroom Molecule.
    Allows an agent to dispatch a strict InterAgentHandshake payload to another workspace's inbox.
    """
    input_schema = InterAgentHandshake

    def __init__(self):
        super().__init__()
        self.system_prompt_generator = SystemPromptGenerator(
            background=[
                "You are the Mailroom Gateway.",
                "Your responsibility is to strictly serialize an InterAgentHandshake Pydantic model into a Markdown file.",
                "This Markdown file is then dropped securely into the target Agent's (or Workspace's) file system inbox."
            ],
            steps=[
                "1. Receive the structured InterAgentHandshake atom.",
                "2. Generate the serialized Frontmatter + Markdown string.",
                "3. Securely write the file to '.agents/inbox' or the specified workspace's inbox root."
            ]
        )

    def run(self, params: InterAgentHandshake) -> str:
        """
        Executes the Handshake dispatch.
        """
        try:
            # By default, we route to the local root .agents/inbox
            # If a different workspace is specified, we route it to `workspaces/{workspace}/.agents/inbox`
            if params.sender_workspace == "root" or not params.sender_workspace:
                inbox_dir = Path(".agents/inbox")
            else:
                # Assuming the OS root holds a `workspaces/` directory housing the isolated pods 
                inbox_dir = Path("workspaces") / params.sender_workspace / ".agents/inbox"
            
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
