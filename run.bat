@echo off
chcp 65001 > nul
title Academic Admission Studio

echo ==============================================================
echo   🏛️ Academic Admission Studio - Laboratory Capacity ^& Roster
echo ==============================================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [!] Python is not installed or not in PATH.
    echo [*] Opening offline dashboard directly in browser...
    start "" offline_dashboard.html
    pause
    exit /b
)

echo [*] Checking dependencies...
python -c "import flask, openpyxl" >nul 2>&1
if %errorlevel% neq 0 (
    echo [*] Installing dependencies from requirements.txt...
    pip install -r requirements.txt --quiet
)

echo.
echo [*] Starting web dashboard at http://127.0.0.1:5050 ...
echo [*] Press Ctrl + C to stop the server.
echo.

start "" "http://127.0.0.1:5050"
python core\app.py
pause
