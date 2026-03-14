from pydantic import Field
from atomic_agents.base.base_tool import BaseTool
from atomic_agents.base.base_io_schema import BaseIOSchema
import subprocess

class TerminalCommandInputSchema(BaseIOSchema):
    """Schema for executing a shell command."""
    command: str = Field(..., description="The shell command to execute.")

class TerminalCommandOutputSchema(BaseIOSchema):
    """Schema for the shell command output."""
    stdout: str = Field(..., description="The standard output of the command.")
    stderr: str = Field(..., description="The standard error of the command.")
    error: str = Field(None, description="Any execution error that occurred.")

class TerminalSkill(BaseTool[TerminalCommandInputSchema, TerminalCommandOutputSchema]):
    """Executes a shell command and returns output."""
    def run(self, params: TerminalCommandInputSchema) -> TerminalCommandOutputSchema:
        try:
            result = subprocess.run(params.command, shell=True, capture_output=True, text=True)
            return TerminalCommandOutputSchema(stdout=result.stdout, stderr=result.stderr)
        except Exception as e:
            return TerminalCommandOutputSchema(stdout="", stderr="", error=str(e))
