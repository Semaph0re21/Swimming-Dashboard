@echo off
powershell.exe -ExecutionPolicy Bypass -File "%~dp0create_desktop_shortcut.ps1"
echo.
echo Desktop shortcut created successfully!
pause
