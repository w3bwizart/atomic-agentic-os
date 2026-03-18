from pydantic import Field
from atomic_agents.base.base_tool import BaseTool
from atomic_agents.base.base_io_schema import BaseIOSchema
from pathlib import Path
import shutil

class ScaffoldInputSchema(BaseIOSchema):
    """Schema for configuring a new workspace scaffold."""
    project_name: str = Field(..., description="Name of the new workspace directory (e.g., legal_research_os)")
    kernel_content: str = Field(..., description="Full markdown content for the config/kernel.md file. Must include necessary SOPs.")
    workforce_content: str = Field(..., description="Full YAML content for the config/workforce.yaml file defining the agents.")
    readme_content: str = Field(..., description="Full markdown content for the workspace README.md.")
    initial_ticket_filename: str = Field(..., description="Filename for the initial ticket in the inbox (e.g., ticket_001.md)")
    initial_ticket_content: str = Field(..., description="Full markdown content for the initial ticket in the inbox.")

class ScaffoldOutputSchema(BaseIOSchema):
    """Schema for scaffold operation results."""
    status: str = Field(..., description="Status of the operation (success/error).")
    message: str = Field(..., description="A message describing the result of the scaffold operation.")
    created_directory: str = Field(None, description="Path to the created directory.")

class ScaffoldSkill(BaseTool[ScaffoldInputSchema, ScaffoldOutputSchema]):
    """Creates a fully configured workspace folder, complete with its own core engines, configs, and seed tickets."""
    def run(self, params: ScaffoldInputSchema) -> ScaffoldOutputSchema:
        try:
            # Workspace Discovery Optimization: Isolate generated OSs inside a workspaces/ directory
            workspace_root = Path("workspaces")
            workspace_root.mkdir(exist_ok=True)

            base_dir = workspace_root / params.project_name

            # Recursion Guard: Prevent creating workspaces inside core system directories or using absolute/traversal paths
            if base_dir.is_absolute() or ".." in Path(params.project_name).parts or params.project_name in [".agents", "core", "skills", ".vault", "config", "docs", "workspaces", "archives"]:
                return ScaffoldOutputSchema(status="error", message="Recursion Guard: Cannot scaffold inside core system directories or use absolute/traversal paths.")

            if base_dir.exists():
                return ScaffoldOutputSchema(status="error", message=f"Directory {base_dir} already exists.")

            # Create core directory tree
            (base_dir / ".agents" / "inbox").mkdir(parents=True)
            (base_dir / ".agents" / "active").mkdir(parents=True)
            (base_dir / ".agents" / "review").mkdir(parents=True)
            (base_dir / ".agents" / "logs").mkdir(parents=True)
            (base_dir / ".vault").mkdir(parents=True)
            (base_dir / "config").mkdir(parents=True)

            # Copy core system binaries over (factory, runner, orchestrator, vault)
            if Path("core").exists():
                shutil.copytree("core", base_dir / "core")
            if Path("skills").exists():
                shutil.copytree("skills", base_dir / "skills")

            # Provide base execution tools for the new setup
            if Path("requirements.txt").exists():
                shutil.copy("requirements.txt", base_dir / "requirements.txt")
            if Path("cleanup.sh").exists():
                shutil.copy("cleanup.sh", base_dir / "cleanup.sh")

            # Inject Generated Settings
            with open(base_dir / "config" / "kernel.md", 'w') as f:
                f.write(params.kernel_content)

            with open(base_dir / "config" / "workforce.yaml", 'w') as f:
                f.write(params.workforce_content)

            with open(base_dir / "README.md", 'w') as f:
                f.write(params.readme_content)

            with open(base_dir / ".agents" / "inbox" / params.initial_ticket_filename, 'w') as f:
                f.write(params.initial_ticket_content)

            # Default permissive policy for cloned repo
            with open(base_dir / ".vault" / "policy.json", 'w') as f:
                f.write('{\n  "permissions": {\n    "dictator": [\n      "file_management",\n      "task_decomposition"\n    ]\n  }\n}')

            return ScaffoldOutputSchema(
                status="success",
                message=f"Successfully built fully-functional Agentic OS instance at: {params.project_name}",
                created_directory=str(base_dir)
            )

        except Exception as e:
            return ScaffoldOutputSchema(status="error", message=str(e))
