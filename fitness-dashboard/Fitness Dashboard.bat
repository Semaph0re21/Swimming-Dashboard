@echo off
title Fitness Dashboard
cd /d "%~dp0"

echo ============================================================
echo Starting Fitness Dashboard...
echo Garmin -^> Intervals.icu -^> Personal Training Engine
echo ============================================================
echo.

if exist ".venv\Scripts\python.exe" (
    start "" http://localhost:8501
    ".venv\Scripts\python.exe" -m streamlit run app.py --server.headless=false --server.port=8501
) else (
    echo [ERROR] Virtual environment not found in .venv.
    echo Please make sure the Python environment is set up.
    pause
)
