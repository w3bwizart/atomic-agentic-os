from pydantic import Field
from atomic_agents.lib.base.base_tool import BaseTool
from enum import Enum
import shutil
import os

class FileManagerAction(str, Enum):
    READ = "read"
    WRITE = "write"
    MOVE = "move"

class FileManagerConfig(BaseTool.Config):
    action: FileManagerAction = Field(..., description="The action to perform: read, write, or move.")
    path: str = Field(..., description="The primary file or directory path (source for move).")
    destination: str = Field(None, description="The destination path, required only for 'move' action.")
    content: str = Field(None, description="The content to write, required only for 'write' action.")

class FileManagerSkill(BaseTool):
    """Executes file management operations."""
    def run(self, params: FileManagerConfig):
        try:
            if params.action == FileManagerAction.READ:
                with open(params.path, 'r') as f:
                    return {"status": "success", "content": f.read()}
            elif params.action == FileManagerAction.WRITE:
                if params.content is None:
                    return {"status": "error", "message": "Content is required for write action"}
                with open(params.path, 'w') as f:
                    f.write(params.content)
                return {"status": "success", "message": f"Wrote to {params.path}"}
            elif params.action == FileManagerAction.MOVE:
                if params.destination is None:
                    return {"status": "error", "message": "Destination is required for move action"}
                shutil.move(params.path, params.destination)
                return {"status": "success", "message": f"Moved {params.path} to {params.destination}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
