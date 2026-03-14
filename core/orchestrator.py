import os
import time
import json
import logging
from pathlib import Path
import yaml
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Setup logging to point exactly to the log directory
log_dir = Path(".agents/logs")
log_dir.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=log_dir / 'system.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Orchestrator")

class InboxHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory or not event.src_path.endswith('.md'):
            return

        filepath = Path(event.src_path)
        logger.info(f"New file detected in inbox: {filepath.name}")
        self.process_file(filepath)

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
            with open(filepath, 'r') as f:
                content = f.read()

            metadata, body = self.parse_frontmatter(content)
            task_id = metadata.get('task_id', 'unknown_task')
            agent_id = metadata.get('agent_id', 'dictator')  # default to dictator

            logger.info(f"Task {task_id} assigned to {agent_id}")

            # 1. State synchronizer: Create hidden state in active/
            active_dir = Path(".agents/active")
            active_dir.mkdir(parents=True, exist_ok=True)

            state_file = active_dir / f"{task_id}.state.json"
            state_data = {
                "current_step": "initialization",
                "assigned_agent": agent_id,
                "subtasks_completed": [],
                "tool_outputs": []
            }
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2)

            # 2. Inject config/skill.md into system prompt (simulation for now)
            skill_md_path = Path("config/skill.md")
            sops = ""
            if skill_md_path.exists():
                with open(skill_md_path, 'r') as f:
                    sops = f.read()

            logger.info(f"Injected SOPs. Length: {len(sops)}")

            # 3. Diagnostic Test behavior: Dictator acknowledges and moves to active/
            if agent_id == 'dictator' or agent_id == 'dictator_01':
                logger.info(f"Dictator module: running Diagnostic test for {task_id}")

                # Move file to active
                active_path = active_dir / filepath.name
                filepath.rename(active_path)
                logger.info(f"Moved {filepath.name} to active/")

                # Update state
                state_data["current_step"] = "acknowledged_by_dictator"
                with open(state_file, 'w') as f:
                    json.dump(state_data, f, indent=2)

        except Exception as e:
            logger.error(f"Error processing file {filepath.name}: {e}")

def main():
    inbox_path = ".agents/inbox"
    os.makedirs(inbox_path, exist_ok=True)

    event_handler = InboxHandler()
    observer = Observer()
    observer.schedule(event_handler, inbox_path, recursive=False)
    observer.start()

    print(f"Orchestrator started. Watching {inbox_path} for new requests...")
    logger.info("Orchestrator online. Watching inbox.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

if __name__ == "__main__":
    main()
