@echo off
echo Starting Any Downloader Tool...

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH! Please install Python 3.
    pause
    exit /b
)

:: Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

:: Activate venv and install requirements
call .venv\Scripts\activate.bat
echo Installing dependencies...
pip install -r requirements.txt

:: Run the app
echo Launching in your web browser...
python main.py

pause
