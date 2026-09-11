@echo off
chcp 65001 >nul
cd /d "%~dp0"
REM Prefer source. Force release: set USE_RELEASE=1
REM --pet：直接开宠，不关已有实例
set VPET_KIND=eiden
if /I "%USE_RELEASE%"=="1" goto :release
where pythonw >nul 2>&1
if %ERRORLEVEL%==0 (
  start "" pythonw "%~dp0vpet_app.py" --pet --kind eiden
  exit /b 0
)
where python >nul 2>&1
if %ERRORLEVEL%==0 (
  start "" python "%~dp0vpet_app.py" --pet --kind eiden
  exit /b 0
)
:release
if exist "%~dp0release\Vpet\Vpet.exe" (
  start "" "%~dp0release\Vpet\Vpet.exe" --pet --kind eiden
  exit /b 0
)
echo Python / release\Vpet\Vpet.exe not found
pause
exit /b 1
