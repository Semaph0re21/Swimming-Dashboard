@echo off
title Fitness Dashboard
cd /d "%~dp0"

echo ============================================================
echo Starting Fitness Dashboard...
echo Garmin -^> Intervals.icu -^> Personal Training Engine
echo ============================================================
echo.

if exist ".venv\Scripts\python.exe" (
    set "PYTHON_BIN=.venv\Scripts\python.exe"
) else (
    set "PYTHON_BIN=python"
)

start "" http://localhost:8501
"%PYTHON_BIN%" -m streamlit run app.py --server.headless=false --server.port=8501
