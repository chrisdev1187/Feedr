@echo off
title 📊 VIBE DASHBOARD - Telemetry UI
color 0E
set PYTHON_EXE="C:\Users\carl\AppData\Local\Python\pythoncore-3.14-64\python.exe"
set APP_DIR="C:\Users\carl\OneDrive\Desktop\tup - dont delete"

echo.
echo  [ VIBE DASHBOARD ]
echo  Launching Flask Telemetry Service...
echo.

cd /d %APP_DIR%
start http://localhost:5000
%PYTHON_EXE% utils\dashboard.py

pause
