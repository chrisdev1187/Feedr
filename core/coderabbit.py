"""
Code Rabbit — Proactive code reviewer for Spoon Feedr.
Periodically checks the codebase for issues, bugs, and improvements.
"""

import os
import json
from vibe_launcher import CloudLLM
from core.memory import MemoryEngine

class CodeRabbit:
    """Proactive reviewer that analyzes code and 'comments' on potential issues."""

    def __init__(self):
        """Initializes with CloudLLM for analysis and MemoryEngine for storage."""
        self.cloud = CloudLLM()
        self.memory = MemoryEngine()

    def review_file(self, filepath):
        """Reviews a specific file for potential issues."""
        if not os.path.exists(filepath):
            return

        with open(filepath, "r") as f:
            content = f.read()

        prompt = f"""You are Code Rabbit, an expert AI code reviewer.
Review the following code for bugs, security issues, performance bottlenecks, or style improvements.
Return a JSON list of findings: [{{"line": int, "issue": str, "severity": "low/medium/high", "suggestion": str}}].
If no issues, return [].

FILE: {filepath}
CONTENT:
{content}
"""
        try:
            resp = self.cloud.chat([{"role": "user", "content": prompt}], temperature=0.2)
            import re
            match = re.search(r'\[.*\]', resp, re.DOTALL)
            if match:
                findings = json.loads(match.group())
                for finding in findings:
                    # Store finding in memory
                    self.memory.store_fact(
                        f"issue_{filepath}_{finding['line']}",
                        finding,
                        category="code_rabbit_review"
                    )
                    self.memory.add_to_vector_memory(
                        f"Code Rabbit finding in {filepath}: {finding['issue']}",
                        metadata={"file": filepath, "line": finding['line'], "type": "code_review"}
                    )
                return findings
        except Exception as e:
            print(f"Code Rabbit review failed for {filepath}: {e}")
        return []

    def review_project(self, root_dir="."):
        """Reviews the entire project by iterating through python files."""
        all_findings = {}
        for root, _, files in os.walk(root_dir):
            if "venv" in root or ".git" in root or "db" in root:
                continue
            for file in files:
                if file.endswith(".py"):
                    path = os.path.join(root, file)
                    findings = self.review_file(path)
                    if findings:
                        all_findings[path] = findings
        return all_findings
