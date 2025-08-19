import time
import subprocess
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# --- CONFIGURATION ---
# The directory to watch ('.' means the current directory)
WATCH_PATH = '.'
# The git branch to push to
BRANCH_NAME = 'main'
# Time to wait after a change before committing (in seconds)
# This prevents multiple rapid commits during saves.
COMMIT_COOLDOWN = 10
# --- END CONFIGURATION ---

class ChangeHandler(FileSystemEventHandler):
    """Handles file system events and triggers git commits."""
    def __init__(self):
        self.last_commit_time = 0

    def on_any_event(self, event):
        """
        This function is called when any file or directory is changed.
        """
        # Ignore changes in the .git directory and this script itself
        if '.git' in event.src_path or 'auto_commit.py' in event.src_path:
            return

        current_time = time.time()
        # Check if enough time has passed since the last commit
        if current_time - self.last_commit_time > COMMIT_COOLDOWN:
            print(f"Change detected in: {event.src_path}")
            self.commit_and_push()
            self.last_commit_time = current_time

    def commit_and_push(self):
        """Adds, commits, and pushes changes to the repository."""
        try:
            # Generate a commit message with the current timestamp
            commit_message = f"Auto-commit: Changes detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            print("Running 'git add .'...")
            subprocess.run(["git", "add", "."], check=True)
            
            print(f"Committing with message: '{commit_message}'")
            # Use --no-verify to bypass any pre-commit hooks if needed
            subprocess.run(["git", "commit", "-m", commit_message, "--no-verify"], check=True)
            
            print(f"Pushing to branch '{BRANCH_NAME}'...")
            subprocess.run(["git", "push", "origin", BRANCH_NAME], check=True)
            
            print("✅ Successfully committed and pushed changes.")

        except subprocess.CalledProcessError as e:
            print(f"🛑 An error occurred during git operation: {e}")
        except FileNotFoundError:
            print("🛑 'git' command not found. Is Git installed and in your PATH?")

if __name__ == "__main__":
    print(f"🚀 Starting file watcher in directory: '{WATCH_PATH}'")
    print(f"Changes will be pushed to the '{BRANCH_NAME}' branch.")
    print("Press Ctrl+C to stop.")

    event_handler = ChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, WATCH_PATH, recursive=True)
    
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nWatcher stopped.")
    observer.join()