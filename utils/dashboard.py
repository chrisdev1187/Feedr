from flask import Flask, render_template_string, jsonify
import json
from pathlib import Path

app = Flask(__name__)
ROOT_DIR = Path(__file__).parent.parent
TELEMETRY_PATH = ROOT_DIR / "telemetry.json"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Vibe Coder Pro - Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #0f172a; color: #f8fafc; padding: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        .card { background: #1e293b; padding: 20px; border-radius: 12px; border: 1px solid #334155; }
        .stat { font-size: 2em; font-weight: bold; color: #38bdf8; }
        h1 { color: #f472b6; }
        .skill-tag { display: inline-block; background: #334155; padding: 4px 8px; border-radius: 4px; margin: 2px; font-size: 0.8em; }
        .health-success { color: #4ade80; }
        .health-fail { color: #f87171; }
    </style>
</head>
<body>
    <h1>🧠 Vibe Coder Pro Dashboard</h1>
    <div class="grid">
        <div class="card">
            <h3>🚀 Total Requests</h3>
            <div class="stat">{{ data.total_requests }}</div>
        </div>
        <div class="card">
            <h3>🪙 Est. Tokens Used</h3>
            <div class="stat">{{ data.total_tokens_est }}</div>
        </div>
        <div class="card">
            <h3>⚡ Avg Speed</h3>
            <div class="stat">{{ data.execution_time_avg | round(2) }}s</div>
        </div>
    </div>
    
    <h2 style="margin-top: 30px;">🌐 Provider Health</h2>
    <div class="grid">
        {% for provider, stats in data.providers.items() %}
        <div class="card">
            <h3>{{ provider | capitalize }}</h3>
            <p>Success: <span class="health-success">{{ stats.success }}</span></p>
            <p>Failures: <span class="health-fail">{{ stats.fail }}</span></p>
            {% if stats.last_error %}
            <p style="font-size: 0.8em; color: #94a3b8;">Last Error: {{ stats.last_error }}</p>
            {% endif %}
        </div>
        {% endfor %}
    </div>

    <div class="grid" style="margin-top: 20px;">
        <div class="card">
            <h3>📊 Modes Activity</h3>
            <ul>
            {% for mode, count in data.modes.items() %}
                <li>{{ mode }}: {{ count }}</li>
            {% endfor %}
            </ul>
        </div>
        <div class="card">
            <h3>🛠️ Skills Activated</h3>
            {% for skill, count in data.skills_activated.items() %}
                <span class="skill-tag">{{ skill }}: {{ count }}</span>
            {% endfor %}
        </div>
    </div>
    
    <script>
        setTimeout(() => location.reload(), 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    if TELEMETRY_PATH.exists():
        data = json.loads(TELEMETRY_PATH.read_text())
    else:
        data = {"total_requests": 0, "total_tokens_est": 0, "execution_time_avg": 0, "providers": {}, "modes": {}, "skills_activated": {}}
    return render_template_string(HTML_TEMPLATE, data=data)

if __name__ == '__main__':
    print("🚀 Dashboard running at http://localhost:5000")
    app.run(port=5000, debug=False)
