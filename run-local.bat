@echo off
REM Local test script for Windows

echo ========================================
echo QC Panel API - Local Test
echo ========================================

cd /d "%~dp0"

echo.
echo [1/5] Checking Python...
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not found!
    pause
    exit /b 1
)

echo.
echo [2/5] Creating virtual environment...
if not exist venv (
    python -m venv venv
)

echo.
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [4/5] Installing dependencies...
pip install -q -r requirements.txt

echo.
echo [5/5] Starting server...
echo.
echo ==========================================
echo API will run at: http://localhost:8000
echo Docs at: http://localhost:8000/docs
echo Health check: http://localhost:8000/health
echo ==========================================
echo.
echo Press Ctrl+C to stop
echo.

REM Copy test env if .env doesn't exist
if not exist .env (
    echo Creating .env from .env.test...
    copy .env.test .env
)

REM Start uvicorn
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug

pause
