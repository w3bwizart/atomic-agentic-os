from pydantic import Field
from atomic_agents.base.base_tool import BaseTool
from atomic_agents.base.base_io_schema import BaseIOSchema
from pathlib import Path
import shutil
import textwrap

from typing import List

class OrganismConfig(BaseIOSchema):
    """Configuration for a single agent within the OS."""
    id: str = Field(..., description="Unique identifier for the agent (e.g., 'editor').")
    role: str = Field(..., description="The role of the agent (e.g., 'Senior Editor').")
    description: str = Field(default="", description="A short description of the agent's responsibilities.")

class ScaffoldInputSchema(BaseIOSchema):
    """Schema for configuring a new workspace scaffold."""
    project_name: str = Field(..., description="Name of the new workspace directory (e.g., legal_research_os)")
    description: str = Field(..., description="A short description of what this workspace does.")
    team: List[OrganismConfig] = Field(default=[], description="A list of agents to bootstrap the OS workforce with.")

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
            if base_dir.is_absolute() or ".." in Path(params.project_name).parts or params.project_name in [".organism_agents", "core", "skills", ".vault", "config", "docs", "workspaces", "archives"]:
                return ScaffoldOutputSchema(status="error", message="Recursion Guard: Cannot scaffold inside core system directories or use absolute/traversal paths.")

            if base_dir.exists():
                return ScaffoldOutputSchema(status="error", message=f"Directory {base_dir} already exists.")

            # Create core directory tree
            (base_dir / ".organism_agents" / "inbox").mkdir(parents=True)
            (base_dir / ".organism_agents" / "active").mkdir(parents=True)
            (base_dir / ".organism_agents" / "review").mkdir(parents=True)
            (base_dir / ".organism_agents" / "logs").mkdir(parents=True)
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
            if Path("config/providers.yaml").exists():
                shutil.copy("config/providers.yaml", base_dir / "config" / "providers.yaml")

            kernel_content = textwrap.dedent(f"""\
            # Workspace: {params.project_name}
            {params.description}

            You are an isolated set of operational agents living inside {params.project_name}.
            When passing tasks sequentially, you MUST use the mailroom skill and transmit an `InterAgentHandshakeAtom`.
            """)

            if not params.team:
                params.team = [OrganismConfig(id="researcher", role="Senior Researcher", description="Gathers requirements.")]
                
            workforce_agents_yaml = ""
            policy_permissions = ""
            for i, agent in enumerate(params.team):
                workforce_agents_yaml += f"""  - id: "{agent.id}"\n    role: "{agent.role}"\n    description: "{agent.description}"\n    skills:\n      - file_management\n      - mailroom_routing\n    model_provider: "groq"\n"""
                policy_permissions += f'    "{agent.id}": [\n      "file_management",\n      "mailroom_routing"\n    ]'
                if i < len(params.team) - 1:
                    policy_permissions += ",\n"

            workforce_content = f"agents:\n{workforce_agents_yaml}"
            policy_content = f'{{\n  "permissions": {{\n{policy_permissions}\n  }}\n}}'

            readme_content = textwrap.dedent(f"""\
            # {params.project_name}
            {params.description}
            
            This workspace was autonomously scaffolded by the OS.
            """)

            # Inject Generated Settings
            with open(base_dir / "config" / "kernel.md", 'w') as f:
                f.write(kernel_content)

            with open(base_dir / "config" / "organism.workforce.yaml", 'w') as f:
                f.write(workforce_content)

            with open(base_dir / "README.md", 'w') as f:
                f.write(readme_content)

            first_agent = params.team[0].id if params.team else "researcher"
            with open(base_dir / ".organism_agents" / "inbox" / "seed_ticket.md", 'w') as f:
                f.write(f"---\ntask_id: SEED-001\norganism_agent_id: {first_agent}\n---\nAnalyze the environment.\n")

            # Default permissive policy for cloned repo
            with open(base_dir / ".vault" / "atom.policy.json", 'w') as f:
                f.write(policy_content)

            return ScaffoldOutputSchema(
                status="success",
                message=f"Successfully built fully-functional Agentic OS instance at: {params.project_name}",
                created_directory=str(base_dir)
            )

        except Exception as e:
            return ScaffoldOutputSchema(status="error", message=str(e))
