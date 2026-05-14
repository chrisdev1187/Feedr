import json
import logging
import time
from pathlib import Path
from datetime import datetime

class VibeLogger:
    def __init__(self, log_dir="logs", telemetry_file="telemetry.json"):
        self.root_dir = Path(__file__).parent.parent
        self.log_dir = self.root_dir / log_dir
        self.telemetry_path = self.root_dir / telemetry_file
        
        self.log_dir.mkdir(exist_ok=True)
        
        # Setup session logging
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"session_{session_id}.log"
        
        logging.basicConfig(
            filename=str(self.log_file),
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("VibeCoder")
        
        self.telemetry = self.load_telemetry()

    def load_telemetry(self):
        if self.telemetry_path.exists():
            try:
                data = json.loads(self.telemetry_path.read_text())
                # Ensure provider field exists for migration
                if "providers" not in data:
                    data["providers"] = {}
                return data
            except:
                return self.default_telemetry()
        return self.default_telemetry()

    def default_telemetry(self):
        return {
            "total_requests": 0,
            "total_tokens_est": 0,
            "execution_time_avg": 0.0,
            "providers": {}, # Track gemini, groq, etc.
            "modes": {},
            "skills_activated": {}
        }

    def save_telemetry(self):
        self.telemetry_path.write_text(json.dumps(self.telemetry, indent=2))

    def log_provider_hit(self, provider_name, success, error_msg=None):
        """Track success/fail and actual errors (404, 429, etc)"""
        if provider_name not in self.telemetry["providers"]:
            self.telemetry["providers"][provider_name] = {"success": 0, "fail": 0, "last_error": None}
        
        if success:
            self.telemetry["providers"][provider_name]["success"] += 1
        else:
            self.telemetry["providers"][provider_name]["fail"] += 1
            self.telemetry["providers"][provider_name]["last_error"] = error_msg
            self.logger.error(f"Provider {provider_name} failed: {error_msg}")
        
        self.save_telemetry()

    def log_interaction(self, user_input, intent, skills, duration, tokens):
        # Update Telemetry
        self.telemetry["total_requests"] += 1
        self.telemetry["total_tokens_est"] += tokens
        
        # Calculate new average duration
        prev_avg = self.telemetry.get("execution_time_avg", 0.0)
        n = self.telemetry["total_requests"]
        self.telemetry["execution_time_avg"] = (prev_avg * (n - 1) + duration) / n
        
        mode = intent.get("mode", "unknown")
        self.telemetry["modes"][mode] = self.telemetry["modes"].get(mode, 0) + 1
        
        for skill in skills:
            self.telemetry["skills_activated"][skill] = self.telemetry["skills_activated"].get(skill, 0) + 1
            
        self.save_telemetry()
        
        # Log to file
        self.logger.info(f"Input: {user_input}")
        self.logger.info(f"Intent: {intent}")
        self.logger.info(f"Skills: {skills}")
        self.logger.info(f"Stats: {duration:.2f}s, {tokens} tokens")
        self.logger.info("-" * 40)

    def get_summary(self):
        t = self.telemetry
        summary = (f"📊 Requests: {t['total_requests']} | "
                   f"⚡ Avg: {t['execution_time_avg']:.1f}s | "
                   f"🪙 Tokens: {t['total_tokens_est']}")
        return summary

    def get_provider_health(self):
        health = []
        for p, stats in self.telemetry.get("providers", {}).items():
            status = "✅" if stats["fail"] == 0 or (stats["success"] > stats["fail"]) else "⚠️"
            if stats["last_error"]:
                health.append(f"{status} {p}: {stats['success']}s/{stats['fail']}f (Last: {stats['last_error']})")
            else:
                health.append(f"{status} {p}: {stats['success']}s/{stats['fail']}f")
        return "\n".join(health) if health else "No provider data yet."

if __name__ == "__main__":
    vlog = VibeLogger()
    vlog.log_provider_hit("gemini", True)
    vlog.log_provider_hit("groq", False, "404 Not Found")
    print(vlog.get_provider_health())
