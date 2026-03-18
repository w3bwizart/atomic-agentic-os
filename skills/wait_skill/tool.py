from pydantic import Field
from atomic_agents.base.base_tool import BaseTool
from atomic_agents.base.base_io_schema import BaseIOSchema
from pathlib import Path
import json
import time

class WaitDependenciesInputSchema(BaseIOSchema):
    """Schema for waiting on other agents' tasks."""
    task_ids: list[str] = Field(..., description="List of task IDs to wait for.")
    timeout_seconds: int = Field(60, description="Max time to wait for the tasks to complete.")

class WaitDependenciesOutputSchema(BaseIOSchema):
    """Schema for wait operation results."""
    status: str = Field(..., description="Status of the operation (success/timeout/error).")
    message: str = Field(None, description="Detailed message regarding the wait state.")

class WaitSkill(BaseTool[WaitDependenciesInputSchema, WaitDependenciesOutputSchema]):
    """Waits for specified tasks to reach 'completed' state in the active directory."""
    def run(self, params: WaitDependenciesInputSchema) -> WaitDependenciesOutputSchema:
        active_dir = Path(".agents/active")
        start_time = time.time()

        while time.time() - start_time < params.timeout_seconds:
            all_completed = True
            for task_id in params.task_ids:
                state_file = active_dir / f"{task_id}.state.json"
                if not state_file.exists():
                    all_completed = False
                    break
                try:
                    with open(state_file, 'r') as f:
                        state = json.load(f)
                        if state.get("current_step") != "completed":
                            all_completed = False
                            break
                except Exception:
                    all_completed = False
                    break

            if all_completed:
                return WaitDependenciesOutputSchema(status="success", message=f"All dependencies {params.task_ids} are completed.")

            time.sleep(2) # Poll every 2 seconds

        return WaitDependenciesOutputSchema(status="timeout", message=f"Timeout reached waiting for tasks {params.task_ids}.")
