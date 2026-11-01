@echo off
setlocal
cd /d "%~dp0.."
py -3.12 -m venv .venv
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m pip check
if errorlevel 1 goto failed
.venv\Scripts\python.exe main.py --check
if errorlevel 1 goto failed
echo Setup complete. Run scripts\run_windows.bat.
pause
exit /b 0
:failed
echo Setup failed. Copy the error shown above for troubleshooting.
pause
exit /b 1
