import uuid
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class InterAgentHandshake(BaseModel):
    """
    The strict protocol for inter-workspace agent communication in the Atomic Agentic OS.
    This Atom guarantees a predictable contract when one agent (the Sender) needs to 
    request work or pass data to another agent (the Receiver) usually located 
    in a different workspace.
    """
    
    handshake_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="A unique correlation ID for this request, allowing the OS and Agents to track the lifecycle of this specific handshake across multiple workspace logs."
    )
    
    timestamp: str = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="ISO 8601 UTC timestamp of exactly when this handshake was created."
    )
    
    sender_id: str = Field(
        ..., 
        description="The ID of the Agent initiating the handshake."
    )
    
    sender_workspace: str = Field(
        ...,
        description="The directory name of the Workspace where the Sender resides (e.g., 'marketing_os'). Used for routing return payloads."
    )
    
    receiver_id: str = Field(
        ...,
        description="The ID of the Agent this handshake is intended for."
    )
    
    priority: str = Field(
        default="normal",
        description="The execution urgency of this handshake. Valid values: 'low', 'normal', 'high', 'critical'."
    )
    
    directive: str = Field(
        ...,
        description="The explicit instruction or task the Receiver must execute. This should act as the 'System Prompt' contextual injection for this specific run."
    )
    
    payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="A strictly typed set of key-value data the receiver needs to execute the directive. This prevents loose unstructured text hallucination."
    )
    
    callback_required: bool = Field(
        default=False,
        description="If True, the Receiver MUST generate a return Handshake and route it back to the `sender_workspace` inbox upon completion."
    )
    
    def to_markdown_file(self) -> str:
        """
        Serializes the strict Atom into the OS-native Markdown format used by the State Bus file-watcher.
        """
        import yaml
        
        # We extract metadata strictly
        metadata = {
            "task_id": self.handshake_id,
            "agent_id": self.receiver_id,
            "priority": self.priority,
            "sender_workspace": self.sender_workspace,
            "callback_required": self.callback_required
        }
        
        frontmatter = yaml.dump(metadata, default_flow_style=False)
        
        # The body is constructed securely
        body_content = f"## Directive\n{self.directive}\n\n"
        if self.payload:
            import json
            body_content += f"## Payload\n```json\n{json.dumps(self.payload, indent=2)}\n```\n"
            
        return f"---\n{frontmatter}---\n{body_content}"
