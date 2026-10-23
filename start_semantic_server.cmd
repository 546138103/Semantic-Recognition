@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
set PYTHONUTF8=1
set PYTHONDONTWRITEBYTECODE=1
".venv\Scripts\python.exe" -B -u semantic_server.py %*
set SEMANTIC_EXIT=%ERRORLEVEL%
pause
exit /b %SEMANTIC_EXIT%
