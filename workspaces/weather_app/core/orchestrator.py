import os
import time
import json
import logging
import threading
import warnings
from pathlib import Path
import yaml
from watchdog.observers import Observer

warnings.filterwarnings("ignore", category=FutureWarning)
from watchdog.events import FileSystemEventHandler

from core.runner import execute_organism_agent_task

log_dir = Path(".organism_agents/logs")
log_dir.mkdir(parents=True, exist_ok=True)
import sys
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("Orchestrator")

# ---------------------------------------------------------
# File Watcher & Execution Loop
# ---------------------------------------------------------
class InboxHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.md'):
            return
        if event.src_path.endswith('README.md'):
            return

        filepath = Path(event.src_path)
        # Verify this is actually within a tenant's inbox
        if ".organism_agents" not in filepath.parts or "inbox" not in filepath.parts:
            return

        # Watchdog debounce: check logic happens in the thread to avoid blocking
        threading.Thread(target=self.process_file, args=(filepath,), daemon=True).start()

    def on_modified(self, event):
        # Allow `cp` file overwrites to trigger the orchestrator
        self.on_created(event)

    def parse_frontmatter(self, content):
        if not content.startswith('---'):
            return {}, content
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                metadata = yaml.safe_load(parts[1])
                return metadata, parts[2].strip()
            except yaml.YAMLError as e:
                logger.error(f"Error parsing frontmatter: {e}")
                return {}, content
        return {}, content

    def process_file(self, filepath: Path):
        try:
            # Brief pause to let file writing finish and avoid reading 0 bytes
            time.sleep(0.1)
            
            if not filepath.exists() or filepath.stat().st_size == 0:
                time.sleep(0.2)
                if not filepath.exists() or filepath.stat().st_size == 0:
                    return
            
            # Extract Tenant Workspace Context
            agents_dir_index = filepath.parts.index('.organism_agents')
            workspace_dir = Path(*filepath.parts[:agents_dir_index])
            
            logger.info(f"Tenant Detected [{workspace_dir.name}]: Processing {filepath.name}")

            # Atomic Claim Logic
            active_dir = workspace_dir / ".organism_agents" / "active"
            active_dir.mkdir(parents=True, exist_ok=True)
            active_path = active_dir / filepath.name

            try:
                filepath.rename(active_path)
            except FileNotFoundError:
                logger.debug(f"File {filepath.name} already claimed. Skipping.")
                return

            with open(active_path, 'r') as f:
                content = f.read()

            metadata, body = self.parse_frontmatter(content)
            task_id = metadata.get('task_id', 'unknown_task')
            organism_agent_id = metadata.get('organism_agent_id', 'dictator')

            # Load Isolated Tenant Workforce
            workforce_path = workspace_dir / "config" / "organism.workforce.yaml"
            if not workforce_path.exists():
                logger.error(f"Tenant {workspace_dir.name} missing organism.workforce.yaml. Aborting.")
                active_path.unlink(missing_ok=True)
                return
                
            with open(workforce_path, 'r') as f:
                tenant_workforce = yaml.safe_load(f).get("agents", [])

            # Find agent in local workforce
            agent_config = next((a for a in tenant_workforce if a['id'] == organism_agent_id), None)
            if not agent_config:
                logger.error(f"Agent {organism_agent_id} not found in {workspace_dir.name} workforce. Aborting.")
                active_path.unlink(missing_ok=True)
                return

            logger.info(f"Task {task_id} assigned to {organism_agent_id} within tenant {workspace_dir.name}")

            # 1. State Recovery inside Workspace
            state_file = active_dir / f"{task_id}.state.json"
            state_data = {
                "current_step": "initialization",
                "assigned_agent": organism_agent_id,
                "subtasks_completed": [],
                "tool_outputs": []
            }

            if state_file.exists():
                with open(state_file, 'r') as f:
                    state_data = json.load(f)
                    logger.info(f"Recovered state for {task_id} at step: {state_data['current_step']}")
            else:
                with open(state_file, 'w') as f:
                    json.dump(state_data, f, indent=2)

            # 2. SOP Injector for Tenant Workspace
            kernel_md_path = workspace_dir / "config" / "kernel.md"
            sops = ""
            if kernel_md_path.exists():
                with open(kernel_md_path, 'r') as f:
                    sops = f.read()

            # Delegate execution to Runner (Passing workspace_dir)
            execute_organism_agent_task(task_id, organism_agent_id, agent_config, body, state_file, sops, workspace_dir=str(workspace_dir))

            # Remove active file post-processing
            if active_path.exists():
                active_path.unlink()

        except Exception as e:
            logger.error(f"Error processing file {filepath.name}: {e}")

def main():
    # Watch all workspaces
    workspaces_path = Path("workspaces")
    workspaces_path.mkdir(exist_ok=True)

    event_handler = InboxHandler()
    observer = Observer()
    observer.schedule(event_handler, str(workspaces_path), recursive=True)
    
    global_os_path = Path(".organism_agents")
    if global_os_path.exists():
        observer.schedule(event_handler, str(global_os_path), recursive=True)
        
    observer.start()

    logger.info(f"Multi-Tenant Orchestrator online. Monitoring {workspaces_path} and Root OS...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Graceful shutdown initiated.")
        observer.stop()

    observer.join()

if __name__ == "__main__":
    main()
