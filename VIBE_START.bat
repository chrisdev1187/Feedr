@echo off
title 🚀 VIBE START - 2026 Vibe Coder Pro v2
color 0B
set PYTHON_EXE="C:\Users\carl\AppData\Local\Python\pythoncore-3.14-64\python.exe"
set APP_DIR="C:\Users\carl\OneDrive\Desktop\tup - dont delete"

echo.
echo  [ VIBE CODER PRO v2 ]
echo  Initializing Unified Launcher...
echo.

cd /d %APP_DIR%
%PYTHON_EXE% vibe_launcher.py

if errorlevel 1 (
    echo.
    echo  [!] System crashed or Python not found.
    echo  Check path: %PYTHON_EXE%
    pause
)
pause
