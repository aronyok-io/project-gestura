@echo off
setlocal
cd /d "%~dp0.."
if not exist .venv\Scripts\python.exe (
  echo Run scripts\setup_windows.bat first.
  pause
  exit /b 1
)
.venv\Scripts\python.exe main.py --check
if errorlevel 1 goto failed
.venv\Scripts\python.exe main.py
if errorlevel 1 goto failed
exit /b 0
:failed
echo Execution failed. Copy the error above and check logs\gestura.log.
pause
exit /b 1
