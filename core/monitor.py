import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ProjectMonitor(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        if not event.is_directory:
            self.callback(f"File modified: {event.src_path}")

def start_monitoring(path=".", callback=print):
    event_handler = ProjectMonitor(callback)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    return observer

class ProactiveResearcher:
    def __init__(self, memory_engine):
        self.memory = memory_engine

    def research_github(self, query):
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

def babysitter_background_loop(monitor_path=".", interval=60):
    """
    Continuous background loop that runs tests and checks for issues.
    """
    from core.tools import ToolDelegator
    print(f"👶 Baby Sitter monitoring {monitor_path}...")

    while True:
        # 1. Run tests proactively
        res = ToolDelegator._run_command(["pytest"])
        if not res["success"]:
            print(f"⚠️ Baby Sitter Alert: Tests failing!\n{res['stderr']}")
            # Here we could trigger a notification or an auto-fix session

        # 2. Check git status for uncommitted changes
        git_res = ToolDelegator.run_gh(["status"])

        time.sleep(interval)
