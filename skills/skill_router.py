import json
import os
import re
from pathlib import Path
from skills.skill_loader import SkillLoader

class SkillRouter:
    def __init__(self, ollama_client=None):
        self.loader = SkillLoader()
        self.ollama = ollama_client
        self.cache = {}

    def decide_skills(self, user_input):
        # 1. Caching check
        if user_input in self.cache:
            return self.cache[user_input]

        # 2. Stage 1: Cheap Keyword Match
        candidate_names = self.loader.match_triggers(user_input)
        if not candidate_names:
            return []

        # 3. Stage 2: Tiny LLM Refinement (Ollama)
        # We only pass the descriptions of matched candidates to save tokens
        candidates = [self.loader.get_skill(name) for name in candidate_names]
        
        prompt = f"""Given the user input, which of these skills should be activated? 
Return a JSON list of skill names only.

User Input: "{user_input}"

Available Skills:
"""
        for c in candidates:
            prompt += f"- {c['name']}: {c['description']}\n"

        active_skills = []
        try:
            if self.ollama:
                resp = self.ollama(prompt)
                # Extract JSON list
                match = re.search(r'\[.*\]', resp, re.DOTALL)
                if match:
                    active_skills = json.loads(match.group())
            else:
                # Fallback to just using Stage 1 if Ollama isn't provided
                active_skills = candidate_names
        except Exception as e:
            print(f"⚠️ Skill Router Error: {e}")
            active_skills = candidate_names # Fallback to all keywords

        # Filter to ensure we only return valid skill names
        final_skills = [s for s in active_skills if self.loader.get_skill(s)]
        
        # 4. Cache and return
        self.cache[user_input] = final_skills
        return final_skills

if __name__ == "__main__":
    # Mock Ollama for testing
    def mock_ollama(p):
        return '["viral_content"]'
    
    router = SkillRouter(ollama_client=mock_ollama)
    print(f"Decision: {router.decide_skills('Make a viral thread about the future of energy')}")
