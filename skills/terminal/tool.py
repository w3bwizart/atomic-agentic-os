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
            output = TerminalCommandOutputSchema(stdout=result.stdout, stderr=result.stderr)
        except Exception as e:
            output = TerminalCommandOutputSchema(stdout="", stderr="", error=str(e))

        # Persistent logging for audit trail
        state_file = getattr(self, "state_file", None)
        if state_file and state_file.exists():
            try:
                import json
                with open(state_file, 'r') as f:
                    state_data = json.load(f)

                tool_outputs = state_data.get("tool_outputs", [])
                tool_outputs.append({
                    "tool": "TerminalSkill",
                    "command": params.command,
                    "stdout": output.stdout,
                    "stderr": output.stderr,
                    "error": output.error
                })
                state_data["tool_outputs"] = tool_outputs

                with open(state_file, 'w') as f:
                    json.dump(state_data, f, indent=2)
            except Exception:
                pass # Fail silently if logging fails

        return output
