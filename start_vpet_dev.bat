@echo off
chcp 65001 >nul
cd /d "%~dp0"
REM 开发入口：始终跑源码
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
echo 未找到 Python（pythonw / python）
pause
exit /b 1
