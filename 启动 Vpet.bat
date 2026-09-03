@echo off
chcp 65001 >nul
cd /d "%~dp0"
REM Prefer source. Force release: set USE_RELEASE=1
if /I "%USE_RELEASE%"=="1" goto :release
where pythonw >nul 2>&1
if %ERRORLEVEL%==0 (
  start "" pythonw "%~dp0vpet_app.py"
  exit /b 0
)
where python >nul 2>&1
if %ERRORLEVEL%==0 (
  start "" python "%~dp0vpet_app.py"
  exit /b 0
)
:release
if exist "%~dp0release\Vpet\Vpet.exe" (
  start "" "%~dp0release\Vpet\Vpet.exe"
  exit /b 0
)
echo Python / release\Vpet\Vpet.exe not found
pause
exit /b 1
