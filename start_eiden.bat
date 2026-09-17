@echo off
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_eiden.ps1"
exit /b %ERRORLEVEL%
