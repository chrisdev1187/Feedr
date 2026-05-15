"""
2026 Vibe Coder Pro v2 - FINAL UNIFIED LAUNCHER
All agents: NVIDIA, Jules, Gemini CLI, Ollama, Groq, DeepSeek, OpenRouter
"""

import os
import sys
import json
import re
import subprocess
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import time
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from ratelimit import limits, sleep_and_retry

logger = logging.getLogger(__name__)

# ========== LOGGING & TELEMETRY ==========
try:
    from utils.logger import VibeLogger
except ImportError:
    class VibeLogger:
        def __init__(self, *args, **kwargs): pass
        def log_interaction(self, *args): pass
        def get_summary(self): return "Telemetry inactive"
        def get_provider_health(self): return "Health unknown"
        def log_provider_hit(self, *args): pass

# ========== SKILL FRAMEWORK ==========
try:
    from skills.skill_router import SkillRouter
    from skills.skill_loader import SkillLoader
except ImportError:
    class SkillRouter:
        def __init__(self, *args, **kwargs): pass
        def decide_skills(self, *args): return []
    class SkillLoader:
        def __init__(self, *args, **kwargs): pass
        def load_instructions(self, *args): return ""
        def get_skill(self, name): return {}

# ========== HELPERS ==========
def run_cli_tool(cmd_list, **kwargs):
    """Run a CLI tool, handling Windows .cmd extensions if needed."""
    if sys.platform == "win32":
        executable = shutil.which(cmd_list[0])
        if not executable and shutil.which(cmd_list[0] + ".cmd"):
            cmd_list[0] = cmd_list[0] + ".cmd"
    return subprocess.run(cmd_list, capture_output=True, text=True, **kwargs)

# ========== RECALL/REMEMBER ==========
_memory_cache = {}
def remember(key, value):
    _memory_cache[key] = value
def recall(key):
    return _memory_cache.get(key)

# ========== ENVIRONMENT & CONFIG ==========
env_path = Path(".") / ".env"
try:
    from dotenv import load_dotenv
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    else:
        pass
except ImportError:
    pass

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

def ensure_ollama_ready():
    """Verify Ollama is running and has the required model."""
    try:
        import ollama
        try:
            ollama.list()
            return True
        except Exception:
            return False
    except ImportError:
        return False

# ========== CLOUD LLM WATERFALL ==========
class CloudLLM:
    def __init__(self, logger=None):
        self.logger = logger
        self.providers = []
        if GEMINI_API_KEY: self.providers.append(("gemini", self._gemini))
        if GROQ_API_KEY: self.providers.append(("groq", self._groq))
        if DEEPSEEK_API_KEY: self.providers.append(("deepseek", self._deepseek))
        if OPENROUTER_API_KEY: self.providers.append(("openrouter", self._openrouter))
        if NVIDIA_API_KEY: self.providers.append(("nvidia", self._nvidia))

    @sleep_and_retry
    @limits(calls=60, period=60)
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def _call_with_retry(self, func, messages, temp):
        return func(messages, temp)

    def _gemini(self, messages, temp):
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash-preview")
        return model.generate_content(messages[-1]["content"], generation_config={"temperature": temp}).text
    
    def _groq(self, messages, temp):
        from groq import Groq
        client = Groq(api_key=GROQ_API_KEY)
        resp = client.chat.completions.create(model="llama3-70b-8192", messages=messages, temperature=temp)
        return resp.choices[0].message.content
    
    def _nvidia(self, messages, temp):
        from openai import OpenAI
        client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_API_KEY)
        model = "qwen/qwen3-coder-480b-a35b-instruct"
        resp = client.chat.completions.create(model=model, messages=messages, temperature=temp, max_tokens=2000)
        return resp.choices[0].message.content

    def chat(self, messages: list, temperature: float = 0.7, preferred: str = None) -> str:
        provider_dict = {name: func for name, func in self.providers}
        
        if preferred and preferred in provider_dict:
            try:
                return self._call_with_retry(provider_dict[preferred], messages, temperature)
            except Exception as e:
                print(f"Preferred provider {preferred} failed: {e}")

        for name, func in self.providers:
            if name == preferred: continue
            try:
                return self._call_with_retry(func, messages, temperature)
            except Exception:
                continue
        
        return self._local_chat(messages, temperature) or "All LLMs failed."

    def _local_chat(self, messages, temperature):
        try:
            import ollama
            resp = ollama.chat(model=OLLAMA_MODEL, messages=messages, options={"temperature": temperature})
            return resp["message"]["content"]
        except Exception:
            return None

def parse_intent(user_input: str) -> Dict:
    cloud = CloudLLM()
    prompt = f"""Classify this request. Return JSON only. Input: "{user_input}"
Fields: mode (app/content/viral_short/research/coding_task), platform, tone, complexity (simple/medium/complex), missing (list)"""
    try:
        resp = cloud.chat([{"role": "user", "content": prompt}], temperature=0.3)
        match = re.search(r'\{.*\}', resp, re.DOTALL)
        if match: return json.loads(match.group())
    except: pass
    return {"mode": "content", "complexity": "medium"}
