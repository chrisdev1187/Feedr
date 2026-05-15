"""
Jules Router — Delegate complex coding tasks to Google's async agent
Install: npm install -g @google/jules
Docs: https://jules.google
"""

import subprocess
import shutil
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

# Cache resolved path
JULES_PATH = shutil.which("jules")

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=5, max=20))
def delegate_to_jules(task: str, repo_path: str = ".") -> dict:
    """
    Send a coding task to Jules for autonomous execution.
    Jules spins up a VM, does the work, and opens a PR.
    """
    if not JULES_PATH:
        logger.error("jules-cli not found in PATH")
        return {"success": False, "error": "jules-cli not found. Install with 'npm install -g @google/jules'"}

    try:
        logger.info(f"Delegating task to Jules: {task[:50]}...")
        # Create a remote session for Jules to work on
        result = subprocess.run(
            [JULES_PATH, "remote", "new", "--repo", repo_path, "--session", task],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes for planning phase
        )
        
        if result.returncode == 0:
            # Check status with timeout
            try:
                status = subprocess.run(
                    [JULES_PATH, "remote", "list", "--task"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                status_text = status.stdout
            except subprocess.TimeoutExpired:
                status_text = "Timeout waiting for Jules task list."

            return {"success": True, "session": result.stdout.strip(), "status": status_text}
        else:
            logger.error(f"Jules CLI error: {result.stderr}")
            return {"success": False, "error": result.stderr}
    except Exception as e:
        logger.error(f"Jules delegation exception: {e}")
        return {"success": False, "error": str(e)}
