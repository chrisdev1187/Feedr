@echo off
title 2026 Vibe Coder Pro v2 - Final Setup
color 0A

echo.
echo ============================================================
echo    🧠 2026 VIBE CODER PRO v2 — FINAL UNIFIED SYSTEM
echo ============================================================
echo.
echo This will:
echo   1. Install all Python dependencies
echo   2. Install Node.js tools (Jules, Gemini CLI)
echo   3. Setup Ollama (local refinement)
echo   4. Create .env template
echo   5. Optionally enable file extensions in Windows
echo.

:: 1. Python packages
echo [1/5] Installing Python packages...
pip install --upgrade pip
pip install openai google-generativeai groq python-dotenv edge-tts ollama flask requests pystray Pillow

:: 2. Node.js tools
echo [2/5] Installing Google Jules and Gemini CLI...
call npm install -g @google/jules
call npm install -g @google/gemini-cli

:: 3. Ollama
echo [3/5] Setting up Ollama (local model)...
where ollama >nul 2>&1
if errorlevel 1 (
    echo Downloading Ollama installer...
    curl -fsSL -o ollama_installer.exe https://ollama.com/download/OllamaSetup.exe
    start /wait ollama_installer.exe /S
    del ollama_installer.exe
)
ollama pull llama3.2:3b

:: 4. .env template
echo [4/5] Creating .env template...
(
echo # === 2026 Vibe Coder Pro v2 ===
echo NVIDIA_API_KEY=nvapi-YOUR_KEY
echo GEMINI_API_KEY=
echo GROQ_API_KEY=
echo DEEPSEEK_API_KEY=
echo OPENROUTER_API_KEY=
echo OLLAMA_MODEL=llama3.2:3b
) > .env.template
echo. >> .env.template
echo # Get NVIDIA key: https://build.nvidia.com/settings/api-keys >> .env.template
echo # Get Groq: https://console.groq.com/keys >> .env.template
echo # Get DeepSeek: https://platform.deepseek.com/api_keys >> .env.template
echo # Get OpenRouter: https://openrouter.ai/keys >> .env.template

:: 5. File extensions (optional)
echo [5/5] Windows file extensions...
choice /C YN /M "Show file extensions in Explorer now? (Y/N)"
if errorlevel 2 goto :skip_ext
if errorlevel 1 (
    reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced" /v HideFileExt /t REG_DWORD /d 0 /f
    taskkill /f /im explorer.exe
    start explorer.exe
    echo ✅ File extensions are now visible.
)
:skip_ext

echo.
echo ============================================================
echo   ✅ SETUP COMPLETE — SYSTEM READY
echo ============================================================
echo.
echo Next steps:
echo   1. Edit .env.template and rename to .env
echo   2. Authenticate: gemini          (browser login)
echo   3. Authenticate: jules auth      (GitHub)
echo   4. Run: python vibe_launcher_v2_final.py
echo.
pause