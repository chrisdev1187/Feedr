"""
Monitoring and proactive research tools for Spoon Feedr.
Includes file system watchers and background research loops.
"""

import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ProjectMonitor(FileSystemEventHandler):
    """Event handler for monitoring file system changes in the project."""

    def __init__(self, callback):
        """Initializes with a callback to trigger on file modifications."""
        self.callback = callback

    def on_modified(self, event):
        """Called when a file is modified."""
        if not event.is_directory:
            self.callback(f"File modified: {event.src_path}")

def start_monitoring(path=".", callback=print):
    """Starts a background observer to monitor file changes."""
    event_handler = ProjectMonitor(callback)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    return observer

class ProactiveResearcher:
    """Agentic researcher that proactively finds relevant code and patterns on GitHub."""

    def __init__(self, memory_engine):
        """Initializes with a memory engine to store research results."""
        self.memory = memory_engine

    def research_github(self, query):
        """Uses gh CLI to search for similar projects or patterns and stores them in memory."""
        from core.tools import ToolDelegator
        # Use gh CLI to search for similar projects
        res = ToolDelegator.run_gh(["search", "repos", query, "--limit", "3", "--json", "fullName,description,url"])
        if res["success"]:
            import json
            repos = json.loads(res["stdout"])
            for repo in repos:
                # Store in vector memory for future "patching" ideas
                self.memory.add_to_vector_memory(
                    f"Relevant Repo: {repo['fullName']} - {repo['description']}",
                    metadata={"url": repo['url'], "type": "github_research"}
                )
            return repos
        return []

def babysitter_background_loop(monitor_path=".", interval=300):
    """
    Continuous background loop that runs tests and checks for issues proactively.
    Now includes Code Rabbit proactive reviews.
    """
    from core.tools import ToolDelegator
    from core.coderabbit import CodeRabbit
    print(f"👶 Baby Sitter monitoring {monitor_path}...")
    rabbit = CodeRabbit()

    while True:
        # 1. Run tests proactively
        res = ToolDelegator._run_command(["pytest"])
        if not res["success"]:
            print(f"⚠️ Baby Sitter Alert: Tests failing!\n{res.get('stderr', '')}")

        # 2. Proactive Code Review (Code Rabbit)
        print("🐰 Code Rabbit starting proactive review...")
        rabbit.review_project(monitor_path)

        # 3. Check git status
        git_res = ToolDelegator.run_gh(["status"])

        time.sleep(interval)
