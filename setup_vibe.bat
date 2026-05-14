@echo off
title 2026 Vibe Coder Pro - Ultimate Setup
color 0A
setlocal enabledelayedexpansion

:: =============================================
:: 2026 Vibe Coder Pro - Zero Budget Setup
:: =============================================

:PROGRESS
:: Use block chars to create a progress bar
set "progress_bar=[                    ]"
set "block=█"
set "space= "

:: Step 1: Check Python
cls
echo.
echo ================================================
echo           2026 VIBE CODER PRO SETUP
echo ================================================
echo.
echo [1/8] Checking Python installation...
:: Progress: 12% (1 block)
set "progress_bar=[█                   ]"
echo !progress_bar! - 12%%
timeout /t 1 /nobreak >nul

python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo.
    echo [!] Python not found! Please install Python 3.10+ first.
    echo     Download from: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
echo       [+] Python detected!

:: Step 2: Install Python packages
cls
echo.
echo ================================================
echo           2026 VIBE CODER PRO SETUP
echo ================================================
echo.
echo [2/8] Installing Python packages...
:: Progress: 25% (2 blocks)
set "progress_bar=[██                  ]"
echo !progress_bar! - 25%%
timeout /t 2 /nobreak >nul

pip install --upgrade pip >nul 2>&1
pip install google-generativeai openai groq requests flask python-dotenv >nul 2>&1
echo       [+] Core packages installed

:: Optional: install edge-tts for voice synthesis
pip install edge-tts >nul 2>&1
echo       [+] Edge TTS installed for voice synthesis

:: Step 3: Install Node.js tools
cls
echo.
echo ================================================
echo           2026 VIBE CODER PRO SETUP
echo ================================================
echo.
echo [3/8] Installing Node.js tools...
:: Progress: 37% (3 blocks)
set "progress_bar=[███                 ]"
echo !progress_bar! - 37%%
timeout /t 2 /nobreak >nul

where node >nul 2>&1
if errorlevel 1 (
    echo       [!] Node.js not found. Skipping Gemini/Jules install.
    echo       Download from: https://nodejs.org/
) else (
    npm install -g @google/gemini-cli >nul 2>&1
    npm install -g @google/jules >nul 2>&1
    echo       [+] Gemini CLI and Jules installed
)

:: Step 4: Clone YumCut (free AI video generator)
cls
echo.
echo ================================================
echo           2026 VIBE CODER PRO SETUP
echo ================================================
echo.
echo [4/8] Downloading YumCut AI video generator...
:: Progress: 50% (4 blocks)
set "progress_bar=[█████               ]"
echo !progress_bar! - 50%%
timeout /t 2 /nobreak >nul

if not exist "yumcut" (
    git clone https://github.com/IgorShadurin/app.yumcut.com.git yumcut >nul 2>&1
    echo       [+] YumCut cloned successfully
) else (
    echo       [*] YumCut already exists
)

:: Step 5: Set up YumCut
cls
echo.
echo ================================================
echo           2026 VIBE CODER PRO SETUP
echo ================================================
echo.
echo [5/8] Setting up YumCut...
:: Progress: 62% (5 blocks)
set "progress_bar=[███████             ]"
echo !progress_bar! - 62%%
timeout /t 3 /nobreak >nul

cd yumcut
if exist "package.json" (
    call npm install >nul 2>&1
    echo       [+] YumCut dependencies installed
)
cd ..

:: Step 6: Download quantized model for local LLM
cls
echo.
echo ================================================
echo           2026 VIBE CODER PRO SETUP
echo ================================================
echo.
echo [6/8] Downloading quantized LLM model...
:: Progress: 75% (6 blocks)
set "progress_bar=[██████████          ]"
echo !progress_bar! - 75%%
timeout /t 2 /nobreak >nul

if not exist "%USERPROFILE%\.cache\llama.cpp" mkdir "%USERPROFILE%\.cache\llama.cpp"
set "MODEL_PATH=%USERPROFILE%\.cache\llama.cpp\Phi-3-mini-4k-instruct-q4.gguf"

if not exist "!MODEL_PATH!" (
    echo       [+] Downloading Phi-3-mini model (1.8GB)...
    curl -L -o "!MODEL_PATH!" "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf" >nul 2>&1
    echo       [+] Model downloaded
) else (
    echo       [*] Model already exists
)

:: Step 7: Environment Variables
cls
echo.
echo ================================================
echo           2026 VIBE CODER PRO SETUP
echo ================================================
echo.
echo [7/8] Configuring environment variables...
:: Progress: 87% (7 blocks)
set "progress_bar=[█████████████       ]"
echo !progress_bar! - 87%%
timeout /t 2 /nobreak >nul

:: Create .env template
(
echo # 2026 Vibe Coder Pro - Environment Variables
echo # Copy this file to .env and add your keys
echo.
echo # Google Gemini (Get from: https://aistudio.google.com/app/apikey)
echo GEMINI_API_KEY=your_gemini_key_here
echo.
echo # Groq - Fastest inference (Get from: https://console.groq.com/keys)
echo GROQ_API_KEY=your_groq_key_here
echo.
echo # DeepSeek (Get from: https://platform.deepseek.com/api_keys)
echo DEEPSEEK_API_KEY=your_deepseek_key_here
echo.
echo # OpenRouter - Access to 65+ free models (Get from: https://openrouter.ai/keys)
echo OPENROUTER_API_KEY=your_openrouter_key_here
echo.
echo # Local LLM Settings
echo LLAMA_SERVER_URL=http://127.0.0.1:8080
echo LOCAL_MODEL_PATH=!MODEL_PATH!
) > .env.template

echo       [+] Created .env.template file

:: Step 8: Start local LLM server
cls
echo.
echo ================================================
echo           2026 VIBE CODER PRO SETUP
echo ================================================
echo.
echo [8/8] Starting local LLM server...
:: Progress: 100% (8 blocks)
set "progress_bar=[████████████████████]"
echo !progress_bar! - 100%%
timeout /t 2 /nobreak >nul

:: Check if llama.cpp is installed
where llama-server >nul 2>&1
if errorlevel 1 (
    echo       [!] llama.cpp not found. Skipping local server start.
    echo       Install from: https://github.com/ggerganov/llama.cpp
) else (
    start /B llama-server --model "!MODEL_PATH!" --port 8080 --host 127.0.0.1
    echo       [+] Local LLM server started on port 8080
)

:: Final success screen
cls
echo.
echo ================================================
echo     ✅ SETUP COMPLETE! 2026 VIBE CODER PRO READY
echo ================================================
echo.
echo [92m████████████████████████████████████████████████[0m
echo [92m██[0m 2026 VIBE CODER PRO - ZERO BUDGET AI SYSTEM [92m██[0m
echo [92m████████████████████████████████████████████████[0m
echo.
echo [93m▶ NEXT STEPS:[0m
echo.
echo   1. Edit the .env file with your API keys:
echo      notepad .env.template
echo.
echo   2. Rename .env.template to .env
echo      copy .env.template .env
echo.
echo   3. Run the orchestrator:
echo      python vibe_launcher.py
echo.
echo   4. For YumCut video generation:
echo      cd yumcut ^&^& npm run dev
echo.
echo ================================================
echo.
pause