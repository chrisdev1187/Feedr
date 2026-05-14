
# 2026 Vibe Coder Pro: Unified AI Assistant

> **Zero Budget. Pure Python. LLM Waterfall. Memory-Enhanced. Now with Viral Video Generation.**

## 🎯 What This Project Is

A single unified system that turns any idea into production-ready output:

- **Viral Content** (Twitter threads, TikTok scripts, YouTube Shorts)
- **Working Apps** (web or CLI tools, auto-tested and self-healing)
- **Full Videos** (via YumCut integration)

## 🏗️ Architecture
[USER INPUT] → [INTENT PARSER] → [ROUTER] → [APP/CONTENT/VIDEO MODE]
↓ ↓
[MEMORY] [LLM WATERFALL]
↓
[Gemini → Groq → DeepSeek → Ollama]

text

## 🔧 Components

### Core System (`vibe_launcher.py`)
- **Intent Parser**: Figures out what you want (app/content/video)
- **LLM Waterfall**: Round-robin across free APIs (auto-fallback on rate limits)
- **Memory Layer**: Remembers past projects and preferences
- **App Generator**: Creates, tests, and fixes Python applications
- **Content Generator**: Platform-specific viral templates

### Setup Script (`setup_vibe.bat`)
- One-command environment setup with progress bar
- Installs dependencies, clones YumCut, downloads local models
- Creates `.env.template` for API keys

### Video Generation (YumCut Integration)
- Cloned automatically during setup
- Accessible via `yumcut` directory
- REST API available for automation

## 📊 Free Tier Limits (2026)

| Service | Daily Limit | Best Use |
|---------|-------------|----------|
| Gemini 2.5 Flash | 1,500 req/day | Creative writing, long context |
| Groq Llama3 70B | 7,000 req/day | Fast code generation |
| DeepSeek Chat | 500 req/day | Structured JSON, reasoning |
| Ollama (local) | Unlimited | Offline fallback |

## 🚀 Quick Start

1. **Run Setup**:
   ```bash
   setup_vibe.bat

## 🧠 The Full System: How It All Fits Together

When your friend runs `setup_vibe.bat`, the progress bar will guide them through every step, which is a major quality-of-life improvement over manual setup.

After the installation, the `vibe_launcher.py` script becomes the command center. Based on your feedback, the system now asks a clear, upfront question: **"What would you like to create? (app/content/viral_short)"**

Then, based on that answer:

*   **For Apps or Text Content:** The original `vibe_launcher.py` takes over, leveraging the LLM waterfall to generate code or social media posts, using local models for quick summaries.
*   **For Viral Shorts:** The system can now take a different path. It can either call the `yumcut` directory's API or provide a clear instruction to your friend: `cd yumcut && npm run dev`. This is the most practical approach, as it uses a dedicated, powerful tool for video generation without us having to reinvent it.

The `project.md` file is the source of truth, providing the API key links, setup instructions, and a clear overview of the system's capabilities.

---

## 🚀 Next Steps for Your Friend

Here's the exact flow for your friend to get started.

1.  **Save the Code:** Create the three files from this guide: `vibe_launcher.py`, `setup_vibe.bat`, and `project.md`.
2.  **Run the Installer:** Double-click `setup_vibe.bat`. Watch the progress bar animate as the system installs everything.
3.  **Add API Keys:** Follow the instructions in the final success screen to edit the `.env` file with keys from the provided links.
4.  **Launch the System:** Run `python vibe_launcher.py`.
5.  **Use the System:** Tell the AI what you want to build. For viral shorts, you can either use the integrated prompt or switch to the `yumcut` folder for the dedicated web interface.

This setup gives your friend a polished, professional-grade tool that is both powerful and easy to share on GitHub. It combines the best of our previous plans with the user-friendly installer and the powerful video capabilities of YumCut.