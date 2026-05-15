"""
Gemini CLI Wrapper — Deep research and long-context tasks
Install: npm install -g @google/gemini-cli
Free tier: 60 req/min, 1000 req/day with 1M token context
"""

import subprocess
import shutil
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

# Cache the resolved gemini binary path
GEMINI_PATH = shutil.which("gemini")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=15))
def deep_research(query: str, max_tokens: int = 10000) -> str:
    """
    Use Gemini CLI for deep research tasks.
    Works non-interactively in scripts with retries.
    """
    if not GEMINI_PATH:
        logger.error("gemini-cli not found in PATH")
        return "Error: gemini-cli not found. Install with 'npm install -g @google/gemini-cli'"

    try:
        logger.info(f"Running Gemini research: {query[:50]}...")
        result = subprocess.run(
            [GEMINI_PATH, "-p", query],
            capture_output=True,
            text=True,
            timeout=120
        )
        if result.returncode == 0:
            return result.stdout
        logger.error(f"Gemini CLI error: {result.stderr}")
        return f"Error: {result.stderr}"
    except subprocess.TimeoutExpired:
        logger.error("Gemini research timed out")
        return "Error: Research task timed out."
    except Exception as e:
        logger.error(f"Gemini research exception: {e}")
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
