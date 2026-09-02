@echo off
REM Check if virtual environment exists, create if missing
if not exist ".venv\" (
    echo Creating virtual environment...
    python -m venv .venv
)

REM Activate the virtual environment
call .venv\Scripts\activate.bat

REM Install dependencies only once
if not exist ".venv\installed.flag" (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo done > .venv\installed.flag
)

REM Run your Python script
python script/local_setup.py

pause
