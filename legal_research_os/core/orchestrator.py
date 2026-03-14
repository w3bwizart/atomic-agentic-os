import os
import time
import json
import logging
import threading
from pathlib import Path
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from core.runner import execute_agent_task

log_dir = Path(".agents/logs")
log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=log_dir / 'system.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Orchestrator")

# ---------------------------------------------------------
# File Watcher & Execution Loop
# ---------------------------------------------------------
class InboxHandler(FileSystemEventHandler):
    def __init__(self):
        super().__init__()
        # Load workforce once
        with open("config/workforce.yaml", 'r') as f:
            self.workforce = yaml.safe_load(f).get("agents", [])

    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.md'):
            return

        filepath = Path(event.src_path)
        logger.info(f"New file detected in inbox: {filepath.name}")
        threading.Thread(target=self.process_file, args=(filepath,), daemon=True).start()

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
            # Atomic Claim Logic: Try to move the file
            # If the file was moved by another thread, FileNotFoundError handles it cleanly.
            active_dir = Path(".agents/active")
            active_dir.mkdir(parents=True, exist_ok=True)
            active_path = active_dir / filepath.name

            try:
                filepath.rename(active_path)
            except FileNotFoundError:
                logger.debug(f"File {filepath.name} already claimed by another agent thread. Skipping.")
                return

            with open(active_path, 'r') as f:
                content = f.read()

            metadata, body = self.parse_frontmatter(content)
            task_id = metadata.get('task_id', 'unknown_task')
            agent_id = metadata.get('agent_id', 'dictator')

            # Find agent in workforce
            agent_config = next((a for a in self.workforce if a['id'] == agent_id), None)
            if not agent_config:
                logger.error(f"Agent {agent_id} not found in workforce.yaml. Aborting task {task_id}.")
                active_path.unlink(missing_ok=True)
                return

            logger.info(f"Task {task_id} assigned to {agent_id} ({agent_config['role']})")

            # 1. State Recovery
            state_file = active_dir / f"{task_id}.state.json"
            state_data = {
                "current_step": "initialization",
                "assigned_agent": agent_id,
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

            # 2. SOP Injector
            kernel_md_path = Path("config/kernel.md")
            sops = ""
            if kernel_md_path.exists():
                with open(kernel_md_path, 'r') as f:
                    sops = f.read()

            # Delegate execution to Runner
            execute_agent_task(task_id, agent_id, agent_config, body, state_file, sops)

            # Remove active file post-processing
            if active_path.exists():
                active_path.unlink()

        except Exception as e:
            logger.error(f"Error processing file {filepath.name}: {e}")

def main():
    inbox_path = ".agents/inbox"
    os.makedirs(inbox_path, exist_ok=True)

    event_handler = InboxHandler()
    observer = Observer()
    observer.schedule(event_handler, inbox_path, recursive=False)
    observer.start()

    print(f"Orchestrator V2 started. Watching {inbox_path} for new requests...")
    logger.info("Orchestrator V2 online. Watching inbox.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Graceful shutdown initiated by KeyboardInterrupt.")
        print("\nOrchestrator V2 shutting down gracefully...")
        observer.stop()

    observer.join()

if __name__ == "__main__":
    main()
