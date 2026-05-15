"""
Gemini CLI Wrapper — Deep research and long-context tasks
Install: npm install -g @google/gemini-cli
Free tier: 60 req/min, 1000 req/day with 1M token context
"""

import subprocess
import shutil

# Cache the resolved gemini binary path
GEMINI_PATH = shutil.which("gemini")

def deep_research(query: str, max_tokens: int = 10000) -> str:
    """
    Use Gemini CLI for deep research tasks.
    Works non-interactively in scripts.
    """
    if not GEMINI_PATH:
        return "Error: gemini-cli not found. Install with 'npm install -g @google/gemini-cli'"

    try:
        result = subprocess.run(
            [GEMINI_PATH, "-p", query],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            return result.stdout
        return f"Error: {result.stderr}"
    except Exception as e:
        return f"Exception during research: {e}"

def research_with_context(query: str, context_file: str) -> str:
    """Research with file context (whole codebase understanding)"""
    if not GEMINI_PATH:
        return "Error: gemini-cli not found."

    try:
        result = subprocess.run(
            [GEMINI_PATH, "-c", context_file, "-p", query],
            capture_output=True,
            text=True,
            timeout=180
        )
        if result.returncode == 0:
            return result.stdout
        return f"Error: {result.stderr}"
    except Exception as e:
        return f"Exception during context research: {e}"
