@echo off
echo Starting Stream Scheduler Manager...
echo.

REM Change to the script directory
cd /d "%~dp0"

REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Run the Python script
python StreamSchedulerManager.py

REM Keep the window open if there's an error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo An error occurred. Press any key to exit...
    pause > nul
)
