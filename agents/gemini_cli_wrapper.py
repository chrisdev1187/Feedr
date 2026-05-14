"""
Gemini CLI Wrapper — Deep research and long-context tasks
Install: npm install -g @google/gemini-cli
Free tier: 60 req/min, 1000 req/day with 1M token context
"""

import subprocess
import tempfile

def deep_research(query: str, max_tokens: int = 10000) -> str:
    """
    Use Gemini CLI for deep research tasks.
    Works non-interactively in scripts.
    """
    # Gemini CLI can be invoked non-interactively[reference:18]
    result = subprocess.run(
        ["gemini", "-p", query],
        capture_output=True,
        text=True,
        timeout=120
    )
    return result.stdout

def research_with_context(query: str, context_file: str) -> str:
    """Research with file context (whole codebase understanding)"""
    # Gemini CLI understands entire projects[reference:19]
    result = subprocess.run(
        ["gemini", "-c", context_file, "-p", query],
        capture_output=True,
        text=True
    )
    return result.stdout