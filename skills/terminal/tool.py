from pydantic import Field
from atomic_agents.lib.base.base_tool import BaseTool

class TerminalCommandConfig(BaseTool.Config):
    command: str = Field(..., description="The shell command to execute.")

class TerminalSkill(BaseTool):
    """Executes a shell command and returns output."""
    def run(self, params: TerminalCommandConfig):
        import subprocess
        result = subprocess.run(params.command, shell=True, capture_output=True, text=True)
        return {"stdout": result.stdout, "stderr": result.stderr}
