from pydantic import Field
from atomic_agents.base.base_tool import BaseTool
from atomic_agents.base.base_io_schema import BaseIOSchema
from enum import Enum
import shutil
import os

class FileManagerAction(str, Enum):
    READ = "read"
    WRITE = "write"
    MOVE = "move"

class FileManagerInputSchema(BaseIOSchema):
    """Schema for file management operations."""
    action: FileManagerAction = Field(..., description="The action to perform: read, write, or move.")
    path: str = Field(..., description="The primary file or directory path (source for move).")
    destination: str = Field(None, description="The destination path, required only for 'move' action.")
    content: str = Field(None, description="The content to write, required only for 'write' action.")

class FileManagerOutputSchema(BaseIOSchema):
    """Schema for file management operation results."""
    status: str = Field(..., description="Status of the operation (success/error).")
    content: str = Field(None, description="The content of the file if 'read' action was performed.")
    message: str = Field(None, description="A message describing the result of the operation or error.")

class FileManagerSkill(BaseTool[FileManagerInputSchema, FileManagerOutputSchema]):
    """Executes file management operations."""
    def run(self, params: FileManagerInputSchema) -> FileManagerOutputSchema:
        try:
            if params.action == FileManagerAction.READ:
                with open(params.path, 'r') as f:
                    return FileManagerOutputSchema(status="success", content=f.read())
            elif params.action == FileManagerAction.WRITE:
                if params.content is None:
                    return FileManagerOutputSchema(status="error", message="Content is required for write action")
                with open(params.path, 'w') as f:
                    f.write(params.content)
                return FileManagerOutputSchema(status="success", message=f"Wrote to {params.path}")
            elif params.action == FileManagerAction.MOVE:
                if params.destination is None:
                    return FileManagerOutputSchema(status="error", message="Destination is required for move action")
                shutil.move(params.path, params.destination)
                return FileManagerOutputSchema(status="success", message=f"Moved {params.path} to {params.destination}")

            return FileManagerOutputSchema(status="error", message="Unknown action")
        except Exception as e:
            return FileManagerOutputSchema(status="error", message=str(e))
