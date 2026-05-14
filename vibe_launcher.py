#!/usr/bin/env python3
"""
2026 Vibe Coder Pro v2 - FINAL UNIFIED LAUNCHER
All agents: NVIDIA, Jules, Gemini CLI, Ollama, Groq, DeepSeek, OpenRouter
Plus Windows file extension viewer/modifier.
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

# ========== LOGGING & TELEMETRY ==========
try:
    from utils.logger import VibeLogger
except ImportError:
    class VibeLogger:
        def __init__(self, *args, **kwargs): pass
        def log_interaction(self, *args): pass
        def get_summary(self): return "Telemetry inactive"

# ========== SKILL FRAMEWORK ==========
try:
    from skills.skill_router import SkillRouter
    from skills.skill_loader import SkillLoader
except ImportError:
    # Handle the case where skills folder is not in path or doesn't exist yet
    class SkillRouter:
        def __init__(self, *args, **kwargs): pass
        def decide_skills(self, *args): return []
    class SkillLoader:
        def __init__(self, *args, **kwargs): pass
        def load_instructions(self, *args): return ""

try:
    from utils.api_router import ServiceConnector, get_routing_map
except ImportError:
    class ServiceConnector:
        def call_service(self, *args): return {"error": "API Router inactive"}
    def get_routing_map(): return {}

# ========== HELPERS ==========
def run_cli_tool(cmd_list, **kwargs):
    """Run a CLI tool, handling Windows .cmd extensions if needed."""
    if sys.platform == "win32":
        executable = shutil.which(cmd_list[0])
        if not executable and shutil.which(cmd_list[0] + ".cmd"):
            cmd_list[0] = cmd_list[0] + ".cmd"
    return subprocess.run(cmd_list, capture_output=True, text=True, **kwargs)

# ========== WINDOWS FILE EXTENSION TOGGLE ==========
def toggle_file_extensions(show: bool = True) -> bool:
    """
    Show or hide file extensions in Windows File Explorer.
    show=True -> show extensions (e.g., .txt .py)
    show=False -> hide them
    Returns True on success.
    """
    if sys.platform != "win32":
        print("⚠️ File extension toggle only works on Windows")
        return False
    
    # Registry path for explorer settings
    key_path = r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
    value_name = "HideFileExt"
    # 1 = hide, 0 = show
    new_value = 0 if show else 1
    
    try:
        subprocess.run(
            ["reg", "add", key_path, "/v", value_name, "/t", "REG_DWORD", "/d", str(new_value), "/f"],
            capture_output=True,
            check=True
        )
        # Restart explorer to apply changes
        subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], capture_output=True)
        subprocess.run(["start", "explorer.exe"], shell=True)
        print(f"✅ File extensions {'shown' if show else 'hidden'}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def modify_file_extension(filepath: str, new_extension: str) -> Path:
    """Rename a file to change its extension (e.g., .txt -> .md)."""
    p = Path(filepath)
    if not p.exists():
        raise FileNotFoundError(f"{filepath} not found")
    new_path = p.with_suffix(f".{new_extension.lstrip('.')}")
    p.rename(new_path)
    print(f"📁 Renamed: {p.name} -> {new_path.name}")
    return new_path

# ========== ENVIRONMENT & CONFIG ==========
# Force load from current directory
env_path = Path(".") / ".env"
try:
    from dotenv import load_dotenv
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
        print(f"📝 Loaded .env from {env_path.absolute()}")
    else:
        print("⚠️ No .env file found in current directory.")
except ImportError:
    print("⚠️ python-dotenv not installed. Using OS environment variables only.")

# API keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

def get_system_status():
    """Diagnostic check of all components."""
    status = {
        "Cloud Providers": [],
        "Local AI": "Offline",
        "Packages": [],
        "Skills": []
    }
    
    # Check Providers
    if GEMINI_API_KEY: status["Cloud Providers"].append("Gemini")
    if GROQ_API_KEY: status["Cloud Providers"].append("Groq")
    if DEEPSEEK_API_KEY: status["Cloud Providers"].append("DeepSeek")
    if OPENROUTER_API_KEY: status["Cloud Providers"].append("OpenRouter")
    if NVIDIA_API_KEY: status["Cloud Providers"].append("NVIDIA")
    
    # Check Packages
    for pkg in ["openai", "google.generativeai", "groq", "dotenv", "ollama"]:
        try:
            __import__(pkg.replace(".generativeai", ""))
            status["Packages"].append(f"✅ {pkg}")
        except ImportError:
            status["Packages"].append(f"❌ {pkg}")
            
    # Check Ollama
    if ensure_ollama_ready():
        status["Local AI"] = f"✅ Ready ({OLLAMA_MODEL})"
    
    return status

# ========== CLOUD LLM WATERFALL (extended with NVIDIA) ==========
class CloudLLM:
    def __init__(self, logger=None):
        self.logger = logger
        self.providers = []
        # Store as tuples of (name, function) for logging
        if GEMINI_API_KEY:
            self.providers.append(("gemini", self._gemini))
        if GROQ_API_KEY:
            self.providers.append(("groq", self._groq))
        if DEEPSEEK_API_KEY:
            self.providers.append(("deepseek", self._deepseek))
        if OPENROUTER_API_KEY:
            self.providers.append(("openrouter", self._openrouter))
        if NVIDIA_API_KEY:
            self.providers.append(("nvidia", self._nvidia))
        if not self.providers:
            print("⚠️ No cloud API keys. Running with local only (Ollama).")
    
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
    
    def _deepseek(self, messages, temp):
        from openai import OpenAI
        client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")
        resp = client.chat.completions.create(model="deepseek-chat", messages=messages, temperature=temp)
        return resp.choices[0].message.content
    
    def _openrouter(self, messages, temp):
        import requests
        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        payload = {"model": "openrouter/auto", "messages": messages, "temperature": temp}
        r = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)
        return r.json()["choices"][0]["message"]["content"]
    
    def _nvidia(self, messages, temp):
        from openai import OpenAI
        client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key=NVIDIA_API_KEY)
        model = "qwen/qwen3-coder-480b-a35b-instruct" if len(messages[-1]["content"]) > 200 else "moonshotai/kimi-k2-instruct"
        resp = client.chat.completions.create(model=model, messages=messages, temperature=temp, max_tokens=2000)
        return resp.choices[0].message.content
    
    def chat(self, messages: list, temperature: float = 0.7, preferred: str = None) -> str:
        provider_dict = {name: func for name, func in self.providers}
        
        # Try preferred first
        if preferred and preferred in provider_dict:
            try:
                res = provider_dict[preferred](messages, temperature)
                if self.logger: self.logger.log_provider_hit(preferred, True)
                return res
            except Exception as e:
                if self.logger: self.logger.log_provider_hit(preferred, False, str(e))
        
        # Fallback waterfall
        for name, func in self.providers:
            if name == preferred: continue # already tried
            try:
                res = func(messages, temperature)
                if self.logger: self.logger.log_provider_hit(name, True)
                return res
            except Exception as e:
                if self.logger: self.logger.log_provider_hit(name, False, str(e))
                continue
        
        # Last resort: local Ollama
        return local_chat(messages, temperature) or "All LLMs failed. Check API keys or install Ollama."

# ========== LOCAL OLLAMA (refinement + fallback) ==========
def local_chat(messages: list, temperature: float = 0.7) -> Optional[str]:
    try:
        import ollama
        resp = ollama.chat(model=OLLAMA_MODEL, messages=messages, options={"temperature": temperature})
        return resp["message"]["content"]
    except Exception as e:
        print(f"⚠️ Ollama error: {e}")
        return None

def refine_with_ollama(text: str, instruction: str = "Make this concise and clear") -> str:
    """Refine any text using local model."""
    if not local_chat([{"role": "user", "content": "ping"}]):
        return text
    prompt = f"Refine the following text. {instruction}\n\nTEXT:\n{text}\n\nREFINED:"
    refined = local_chat([{"role": "user", "content": prompt}], temperature=0.3)
    return refined if refined else text

def ensure_ollama_ready():
    """Verify Ollama is running and has the required model."""
    try:
        import ollama
        print(f"🦙 Checking Ollama status ({OLLAMA_MODEL})...")
        
        # Check if server is up
        try:
            models = ollama.list()
        except Exception:
            print("⚠️ Ollama server not responding. Local fallback disabled.")
            return False

        # Check if model exists
        model_names = [m['name'] for m in models['models']]
        if OLLAMA_MODEL not in model_names and f"{OLLAMA_MODEL}:latest" not in model_names:
            print(f"📥 Pulling {OLLAMA_MODEL}... (this may take a few minutes)")
            ollama.pull(OLLAMA_MODEL)
            print(f"✅ {OLLAMA_MODEL} pulled successfully.")
        else:
            print(f"✅ Ollama ready with {OLLAMA_MODEL}.")
        return True
    except ImportError:
        print("⚠️ Ollama python package not installed.")
        return False
    except Exception as e:
        print(f"⚠️ Ollama check failed: {e}")
        return False

# ========== JULES ROUTER ==========
def jules_delegate(task: str, repo_path: str = ".") -> dict:
    try:
        result = run_cli_tool(
            ["jules", "remote", "new", "--repo", repo_path, "--session", task],
            timeout=30
        )
        if result.returncode == 0:
            return {"success": True, "session": result.stdout.strip()}
        return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ========== GEMINI CLI DEEP RESEARCH ==========
def gemini_research(query: str) -> str:
    try:
        result = run_cli_tool(["gemini", "-p", query], timeout=120)
        if result.returncode == 0:
            return result.stdout
        return f"Error: {result.stderr}"
    except Exception as e:
        return f"Error: {e}"

# ========== INTENT PARSER (now includes research and coding flags) ==========
def parse_intent(user_input: str) -> Dict:
    prompt = f"""Classify this request. Return JSON only.
Input: "{user_input}"

Fields:
- mode: one of "app", "content", "viral_short", "research", "coding_task"
- platform: for content/viral: "twitter/tiktok/youtube", for app: "web/cli"
- tone: "hype/educational/raw"
- complexity: "simple/medium/complex"
- missing: list of missing info (max 2)

If user asks to research, analyze, compare → mode="research"
If user asks to build a complete app with multiple steps → mode="coding_task" (will route to Jules)
If user asks for a video short → mode="viral_short"
If user asks for code snippet → mode="app"
Else mode="content"
"""
    try:
        resp = cloud.chat([{"role": "user", "content": prompt}], temperature=0.3, preferred="deepseek")
        match = re.search(r'\{.*\}', resp, re.DOTALL)
        if match:
            return json.loads(match.group())
    except:
        pass
    return {"mode": "content", "platform": "twitter", "tone": "raw", "complexity": "medium", "missing": []}

# ========== CONTENT GENERATOR ==========
def generate_content(idea: str, platform: str, tone: str) -> str:
    templates = {
        "twitter": f"Write viral Twitter thread (1/n,2/n,3/n) with hook, body, CTA. Tone: {tone}\nIdea: {idea}",
        "tiktok": f"Write 30-sec TikTok script with [VISUAL] [AUDIO] cues. Hook 3 sec. Tone: {tone}\nIdea: {idea}",
        "youtube": f"Write 60-sec YouTube Shorts script: 0:00 hook, 0:03-0:45 fast cuts, 0:45 CTA. Tone: {tone}\nIdea: {idea}",
    }
    prompt = templates.get(platform, templates["twitter"])
    raw = cloud.chat([{"role": "user", "content": prompt}], temperature=0.8)
    return refine_with_ollama(raw, instruction="Make it more viral, add emojis, shorten if needed")

# ========== APP GENERATOR ==========
def generate_app(idea: str, platform: str) -> str:
    prompt = f"""Generate a complete, runnable Python program for:
{idea}
Target: {platform} (cli/web)
- Single file, standard lib + Flask if web
- Error handling, test at bottom
- Return ONLY raw code."""
    code = cloud.chat([{"role": "user", "content": prompt}], temperature=0.5, preferred="groq")
    code = re.sub(r'```python\n?|```', '', code)
    return refine_with_ollama(code, instruction="Fix any obvious syntax errors, ensure it's runnable")

# ========== VIRAL SHORT GENERATION (YumCut + fallback) ==========
def generate_viral_short(idea: str) -> str:
    yumcut_dir = Path("yumcut")
    if yumcut_dir.exists() and (yumcut_dir / "package.json").exists():
        print("🎬 Launching YumCut...")
        subprocess.Popen(["npm", "run", "dev"], cwd=str(yumcut_dir), shell=True)
        return "YumCut started at http://localhost:3000"
    else:
        # Lightweight fallback (requires edge-tts, pollinations, ffmpeg)
        script = cloud.chat([{"role": "user", "content": f"Write a 60-second viral script for YouTube Shorts: {idea}"}])
        print("📝 Script generated, trying TTS...")
        try:
            import edge_tts, asyncio
            async def gen_tts():
                await edge_tts.Communicate(script, "en-US-JennyNeural").save("voiceover.mp3")
            asyncio.run(gen_tts())
            return f"Audio saved. Script:\n{script[:500]}...\n\nTo assemble video, run ffmpeg manually or install YumCut."
        except:
            return f"TTS failed. Install edge-tts. Script:\n{script[:500]}..."

# ========== MAIN ORCHESTRATOR ==========
def main():
    print("\n" + "="*70)
    print("🧠 2026 Vibe Coder Pro v2 - FINAL UNIFIED LAUNCHER")
    print("   Agents: NVIDIA(136), Groq, DeepSeek, OpenRouter, Gemini CLI, Jules, Ollama")
    print("   Skills: Modular framework active")
    print("   Windows: toggle file extensions, rename extensions")
    print("="*70)
    
    # Initialize Core Systems
    vlog = VibeLogger()
    print(f"\n{vlog.get_summary()}")
    print("\n🌐 Provider Health:")
    print(vlog.get_provider_health())
    
    # Ensure Ollama is ready
    ensure_ollama_ready()
    
    global cloud
    cloud = CloudLLM(logger=vlog)
    
    def router_ollama(p): return local_chat([{"role": "user", "content": p}], temperature=0.1)
    router = SkillRouter(ollama_client=router_ollama)
    loader = SkillLoader()

    # Show memory
    last = recall("last_idea")
    if last:
        print(f"💡 Last project: {last[:60]}...")
    
    # Optional: Windows file extension utility
    if sys.platform == "win32":
        print("\n📁 Windows utils: type 'showext' or 'hideext' or 'renameext oldfile.txt md'")
    
    while True:
        user_input = input("\n🎯 What would you like to create? (or 'exit') > ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("👋 Goodbye!")
            break
        
        start_time = time.time()
        
        # Windows file extension commands
        if user_input.lower() == "status":
            stat = get_system_status()
            print("\n🔍 SYSTEM DIAGNOSTICS:")
            print(f"📡 Providers: {', '.join(stat['Cloud Providers'])}")
            print(f"🦙 Local AI:  {stat['Local AI']}")
            print(f"📦 Packages:  {', '.join(stat['Packages'])}")
            
            print("\n🗺️ API ROUTING MAP:")
            rmap = get_routing_map()
            for k, v in rmap.items():
                print(f"  {k:18} -> {v}")
            continue
            
        if user_input.lower() == "showext":
            toggle_file_extensions(show=True)
            continue
        if user_input.lower() == "hideext":
            toggle_file_extensions(show=False)
            continue
        if user_input.lower().startswith("renameext "):
            parts = user_input.split()
            if len(parts) >= 3:
                try:
                    modify_file_extension(parts[1], parts[2])
                except Exception as e:
                    print(f"Error: {e}")
            else:
                print("Usage: renameext filename.txt new_ext (without dot)")
            continue
        
        # Skill Routing (Stage 2)
        active_skill_names = router.decide_skills(user_input)
        skill_instructions = ""
        est_tokens = 0
        if active_skill_names:
            print(f"🛠️ Activating skills: {', '.join(active_skill_names)}")
            for name in active_skill_names:
                skill = loader.get_skill(name)
                skill_instructions += f"\n--- SKILL: {name.upper()} ---\n"
                skill_instructions += loader.load_instructions(name) + "\n"
                est_tokens += skill.get("estimated_token_cost", 500)

        # Normal AI processing
        remember("last_idea", user_input)
        intent = parse_intent(user_input)
        mode = intent.get("mode", "content")
        print(f"📊 Mode: {mode} | Complexity: {intent.get('complexity','medium')}")
        
        # Inject skill instructions into user_input context
        full_context = user_input
        if skill_instructions:
            full_context = f"INSTRUCTIONS TO FOLLOW:\n{skill_instructions}\n\nUSER REQUEST: {user_input}"

        # Ask missing info
        if intent.get("missing"):
            for q in intent["missing"][:2]:
                ans = input(f"❓ {q} > ")
                full_context += f" [{q}: {ans}]"
        
        print("\n" + "-"*60)
        
        # Route
        if mode == "research":
            print("🔍 Deep research with Gemini CLI...")
            result = gemini_research(full_context)
            print(result)
            if len(result) > 2000:
                short = refine_with_ollama(result, "Summarize this research in 5 bullet points")
                print("\n✨ Refined summary:\n", short)
        
        elif mode == "coding_task" and intent.get("complexity") == "complex":
            print("🤖 Deploying Jules autonomous coding agent...")
            result = jules_delegate(full_context)
            if result["success"]:
                print(f"✅ Jules session started: {result['session']}")
            else:
                print(f"❌ Jules error: {result['error']}")
        
        elif mode == "viral_short":
            print("🎬 Generating viral short...")
            output = generate_viral_short(full_context)
            print(output)
        
        elif mode == "app":
            print("⚙️ Generating application...")
            code = generate_app(full_context, intent.get("platform", "cli"))
            filename = "generated_app.py"
            Path(filename).write_text(code)
            print(f"✅ Saved as {filename}")
            if input("Run now? (y/n) ").lower() == "y":
                subprocess.run([sys.executable, filename])
        
        else:  # content
            print("📝 Generating viral content...")
            content = generate_content(full_context, intent.get("platform","twitter"), intent.get("tone","raw"))
            print(content)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            Path(f"viral_{timestamp}.txt").write_text(content)
            print(f"💾 Saved to viral_{timestamp}.txt")
        
        # End logging
        duration = time.time() - start_time
        vlog.log_interaction(user_input, intent, active_skill_names, duration, est_tokens)
        
        print("-"*60)
        print("✨ Done. Memory updated.")
        print(vlog.get_summary())
        print("\n🌐 Provider Health:")
        print(vlog.get_provider_health())


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Interrupted")
    except Exception as e:
        print(f"\n❌ Fatal: {e}")
        print("Check that required packages are installed: pip install openai google-generativeai groq python-dotenv edge-tts ollama")