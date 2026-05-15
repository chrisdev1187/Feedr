"""
Tool delegation layer for Spoon Feedr.
Wraps specialized CLI tools like Aider, Jules, and gh.
"""

import subprocess
import sys
import shutil

class ToolDelegator:
    """Delegator class to handle execution of external CLI agents and tools."""

    @staticmethod
    def run_aider(message, auto_test=True, model=None):
        """Runs Aider for git-native code editing and test loops."""
        cmd = ["aider", "--message", message]
        if auto_test:
            cmd.append("--auto-test")
        if model:
            cmd.extend(["--model", model])
        # Add git-native flags by default for Spoon Feedr
        cmd.extend(["--no-show-diffs", "--dark-mode"])
        return ToolDelegator._run_command(cmd)

    @staticmethod
    def run_jules(task, repo_path="."):
        """Runs Google Jules for asynchronous cloud-based coding tasks."""
        # Improved Jules delegation with repo awareness
        cmd = ["jules", "remote", "new", "--repo", repo_path, "--session", task]
        return ToolDelegator._run_command(cmd)

    @staticmethod
    def run_gh(args):
        """Runs the GitHub CLI with the provided arguments."""
        cmd = ["gh"] + args
        return ToolDelegator._run_command(cmd)

    @staticmethod
    def run_ollama(prompt, model="llama3.2"):
        """Directly runs Ollama CLI for local model inference."""
        cmd = ["ollama", "run", model, prompt]
        return ToolDelegator._run_command(cmd)

    @staticmethod
    def _run_command(cmd_list):
        """Internal helper to run shell commands with cross-platform support."""
        if sys.platform == "win32":
            executable = shutil.which(cmd_list[0])
            if not executable and shutil.which(cmd_list[0] + ".cmd"):
                cmd_list[0] = cmd_list[0] + ".cmd"

        try:
            result = subprocess.run(cmd_list, capture_output=True, text=True, check=False)
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
