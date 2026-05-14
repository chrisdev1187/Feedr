@echo off
title 🛠️ VIBE UPDATE - Dependency Manager
color 0D
set PYTHON_EXE="C:\Users\carl\AppData\Local\Python\pythoncore-3.14-64\python.exe"

echo.
echo  [ VIBE UPDATE ]
echo  Installing/Updating System Dependencies...
echo.

%PYTHON_EXE% -m pip install --upgrade pip
%PYTHON_EXE% -m pip install openai google-generativeai groq python-dotenv edge-tts ollama flask requests pystray Pillow

echo.
echo  [+] Done. You can now run VIBE_START.bat
echo.
pause
