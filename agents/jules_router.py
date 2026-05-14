"""
Jules Router — Delegate complex coding tasks to Google's async agent
Install: npm install -g @google/jules
Docs: https://jules.google
"""

import subprocess
import json

def delegate_to_jules(task: str, repo_path: str = ".") -> dict:
    """
    Send a coding task to Jules for autonomous execution.
    Jules spins up a VM, does the work, and opens a PR.
    """
    try:
        # Create a remote session for Jules to work on
        result = subprocess.run(
            ["jules", "remote", "new", "--repo", repo_path, "--session", task],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes for planning phase
        )
        
        if result.returncode == 0:
            # Check status
            status = subprocess.run(
                ["jules", "remote", "list", "--task"],
                capture_output=True,
                text=True
            )
            return {"success": True, "session": result.stdout, "status": status.stdout}
        else:
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}