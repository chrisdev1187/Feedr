"""
Feature Patcher — Automatically "steals" and adapts code from other GitHub repos.
Core component of Spoon Feedr's reuse-first philosophy.
"""

import os
import json
import logging
import re
from core.tools import ToolDelegator
from vibe_launcher import CloudLLM
from core.memory import MemoryEngine

logger = logging.getLogger(__name__)

class FeaturePatcher:
    """Orchestrates the 'Research -> Extract -> Adapt -> Patch' loop."""

    def __init__(self):
        """Initializes patcher with cloud LLM and memory engine."""
        self.cloud = CloudLLM()
        self.memory = MemoryEngine()

    def _extract_and_clean(self, source_code, feature_description):
        """Uses LLM to de-contextualize the found code for reuse."""
        prompt = f"""
        ACT AS: Expert AI Software Engineer.
        SOURCE CODE:
        {source_code}

        TASK: Extract the logic related to '{feature_description}'.
        DE-CONTEXTUALIZE: Remove repo-specific imports, hardcoded paths, or specific project logic.
        CLEAN: Return only the generalized, reusable logic as a single code block.
        """
        resp = self.cloud.chat([{"role": "user", "content": prompt}], temperature=0.1)
        match = re.search(r'```python\n(.*?)\n```', resp, re.DOTALL)
        return match.group(1) if match else resp

    def find_and_patch(self, feature_description):
        """Main loop: finds similar code on GitHub and applies it to the current project."""
        logger.info(f"Starting automated patch loop for: {feature_description}")

        # 1. Research phase: find relevant repos
        search_query = f"language:python {feature_description}"
        res = ToolDelegator.run_gh(["search", "repos", search_query, "--limit", "3", "--json", "fullName,url,description"])
        if not res["success"] or not res["stdout"]:
            return {"success": False, "error": "No relevant repositories found."}

        repo_list = json.loads(res["stdout"])

        # 2. Extraction phase: fetch and clean snippets
        all_snippets = []
        for repo in repo_list:
            logger.info(f"Analyzing repo for reuse: {repo['fullName']}")
            # Fetch most relevant files (heuristic: files matching keywords)
            # Use gh repo view to list files and then gh api to get content
            # For MVP, we'll use a simplified extraction logic
            files_res = ToolDelegator.run_gh(["repo", "view", repo['fullName'], "--json", "files"])
            # (In a real implementation, we would iterate and find the best file)

        # 3. Adaptation & Patching phase: delegate to Aider
        patch_instruction = f"""
        RESEARCH DATA: {json.dumps(repo_list)}
        TASK: Implement {feature_description} in our project.
        REUSE-FIRST: Analyze the patterns from these repos and apply the best parts here.
        GIT-NATIVE: Use git to commit changes after successful application.
        """

        logger.info("Delegating patch application to Aider...")
        # Use Aider to do the heavy lifting of applying the research to local files
        patch_res = ToolDelegator.run_aider(patch_instruction)

        return {
            "success": patch_res["success"],
            "research": repo_list,
            "aider_output": patch_res.get("stdout", patch_res.get("error"))
        }

    def self_improve(self):
        """Self-improvement loop: researches and applies better patterns to Spoon Feedr itself."""
        logger.info("🤖 Spoon Feedr is starting a self-improvement cycle...")
        improvement_task = "optimizing LangGraph state management and UI aesthetic"
        return self.find_and_patch(improvement_task)
