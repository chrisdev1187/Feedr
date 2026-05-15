"""
Jules Router — Delegate complex coding tasks to Google's async agent
Install: npm install -g @google/jules
Docs: https://jules.google
"""

import subprocess
import shutil

def delegate_to_jules(task: str, repo_path: str = ".") -> dict:
    """
    Send a coding task to Jules for autonomous execution.
    Jules spins up a VM, does the work, and opens a PR.
    """
    if not shutil.which("jules"):
        return {"success": False, "error": "jules-cli not found. Install with 'npm install -g @google/jules'"}

    try:
        # Create a remote session for Jules to work on
        result = subprocess.run(
            ["jules", "remote", "new", "--repo", repo_path, "--session", task],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes for planning phase
        )
        
        if result.returncode == 0:
            # Check status with timeout
            try:
                status = subprocess.run(
                    ["jules", "remote", "list", "--task"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                status_text = status.stdout
            except subprocess.TimeoutExpired:
                status_text = "Timeout waiting for Jules task list."

            return {"success": True, "session": result.stdout.strip(), "status": status_text}
        else:
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}
