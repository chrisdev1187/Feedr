import json
import os
from pathlib import Path

SKILLS_DIR = Path(__file__).parent
REGISTRY_FILE = SKILLS_DIR / "registry.json"

class SkillLoader:
    def __init__(self):
        self.skills = []
        self.load_registry()

    def load_registry(self):
        if REGISTRY_FILE.exists():
            with open(REGISTRY_FILE, "r") as f:
                self.skills = json.load(f)
        else:
            print(f"⚠️ Registry file not found: {REGISTRY_FILE}")

    def get_skill(self, name):
        for skill in self.skills:
            if skill["name"] == name:
                return skill
        return None

    def load_instructions(self, skill_name):
        skill = self.get_skill(skill_name)
        if not skill:
            return ""
        
        instruction_path = SKILLS_DIR / skill["instruction_file"]
        if instruction_path.exists():
            return instruction_path.read_text(encoding="utf-8")
        return ""

    def match_triggers(self, user_input):
        """Cheap keyword-based trigger matching (Stage 1)."""
        user_input = user_input.lower()
        matched = []
        for skill in self.skills:
            for trigger in skill["triggers"]:
                if trigger in user_input:
                    matched.append(skill["name"])
                    break
        return matched

if __name__ == "__main__":
    loader = SkillLoader()
    print(f"Loaded {len(loader.skills)} skills.")
    matches = loader.match_triggers("Write a viral twitter thread about AI")
    print(f"Matched skills: {matches}")
    if matches:
        print(f"Instructions for {matches[0]}:\n{loader.load_instructions(matches[0])}")
