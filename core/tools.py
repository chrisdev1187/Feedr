"""
Tool delegation layer for Spoon Feedr.
Wraps specialized CLI tools like Aider, Jules, gh, and Playwright CLI.
"""

import subprocess
import sys
import shutil
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class ToolDelegator:
    """Delegator class to handle execution of external CLI agents and tools."""

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def run_aider(message, auto_test=True, model=None, cwd=None):
        """Runs Aider for git-native code editing and test loops."""
        cmd = ["aider", "--message", message]
        if auto_test:
            cmd.append("--auto-test")
        if model:
            cmd.extend(["--model", model])
        # Add git-native flags by default for Spoon Feedr
        cmd.extend(["--no-show-diffs", "--dark-mode"])
        return ToolDelegator._run_command(cmd, cwd=cwd)

    @staticmethod
    @retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=6))
    def run_jules(task, repo_path="."):
        """Runs Google Jules for asynchronous cloud-based coding tasks."""
        # Improved Jules delegation with repo awareness
        cmd = ["jules", "remote", "new", "--repo", repo_path, "--session", task]
        return ToolDelegator._run_command(cmd)

    @staticmethod
    def run_gh(args, cwd=None):
        """Runs the GitHub CLI with the provided arguments."""
        cmd = ["gh"] + args
        return ToolDelegator._run_command(cmd, cwd=cwd)

    @staticmethod
    def run_ollama(prompt, model="llama3.2"):
        """Directly runs Ollama CLI for local model inference."""
        cmd = ["ollama", "run", model, prompt]
        return ToolDelegator._run_command(cmd)

    @staticmethod
    def run_browser(cmd_args, session="default"):
        """Runs Playwright CLI for token-efficient browser automation."""
        if not shutil.which("playwright-cli"):
            return {"success": False, "error": "playwright-cli not found. Install with 'npm install -g @playwright/cli'"}

        cmd = ["playwright-cli"]
        if session:
            cmd.append(f"-s={session}")
        cmd.extend(cmd_args)
        return ToolDelegator._run_command(cmd)

    @staticmethod
    def _run_command(cmd_list, cwd=None):
        """Internal helper to run shell commands with cross-platform support and error boundaries."""
        if sys.platform == "win32":
            executable = shutil.which(cmd_list[0])
            if not executable and shutil.which(cmd_list[0] + ".cmd"):
                cmd_list[0] = cmd_list[0] + ".cmd"

        try:
            logger.info(f"Executing command: {' '.join(cmd_list)} in {cwd or 'current dir'}")
            result = subprocess.run(cmd_list, capture_output=True, text=True, check=False, cwd=cwd)
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired as e:
            logger.error(f"Command timed out: {e}")
            return {"success": False, "error": "Timeout", "details": str(e)}
        except Exception as e:
            logger.error(f"Command failed: {e}")
            return {"success": False, "error": str(e)}
