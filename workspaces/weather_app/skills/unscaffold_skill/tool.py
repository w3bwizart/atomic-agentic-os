from pydantic import Field
from atomic_agents.base.base_tool import BaseTool
from atomic_agents.base.base_io_schema import BaseIOSchema
from pathlib import Path
import shutil

class UnscaffoldInputSchema(BaseIOSchema):
    """Schema for archiving and removing a workspace scaffold."""
    project_name: str = Field(..., description="Name of the workspace directory to archive and delete (e.g., legal_research_os)")

class UnscaffoldOutputSchema(BaseIOSchema):
    """Schema for unscaffold operation results."""
    status: str = Field(..., description="Status of the operation (success/error).")
    message: str = Field(..., description="A message describing the result of the unscaffold operation.")
    archive_path: str = Field(None, description="Path to the created archive.")

class UnscaffoldSkill(BaseTool[UnscaffoldInputSchema, UnscaffoldOutputSchema]):
    """Archives a completed workspace folder into the archives/ directory and removes the original footprint."""
    def run(self, params: UnscaffoldInputSchema) -> UnscaffoldOutputSchema:
        try:
            workspace_dir = Path("workspaces") / params.project_name
            archive_dir = Path("archives")

            # Security and Recursion Guard
            if ".." in Path(params.project_name).parts or params.project_name in [".agents", "core", "skills", ".vault", "config", "docs", "workspaces", "archives"]:
                return UnscaffoldOutputSchema(status="error", message="Security Guard: Cannot unscaffold core system directories or use traversal paths.")

            if not workspace_dir.exists():
                return UnscaffoldOutputSchema(status="error", message=f"Workspace {params.project_name} not found in workspaces/ directory.")

            archive_dir.mkdir(exist_ok=True)

            # Use shutil to make a compressed tarball
            archive_target = archive_dir / params.project_name
            archive_path = shutil.make_archive(str(archive_target), 'zip', str(workspace_dir))

            # Remove the original workspace cleanly
            shutil.rmtree(workspace_dir)

            return UnscaffoldOutputSchema(
                status="success",
                message=f"Successfully archived and removed workspace: {params.project_name}",
                archive_path=archive_path
            )

        except Exception as e:
            return UnscaffoldOutputSchema(status="error", message=str(e))
