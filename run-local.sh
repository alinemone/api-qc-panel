#!/bin/bash
# Local test script for Linux/Mac

set -e

echo "=========================================="
echo "QC Panel API - Local Test"
echo "=========================================="

cd "$(dirname "$0")"

echo ""
echo "[1/5] Checking Python..."
python3 --version || python --version

echo ""
echo "[2/5] Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv || python -m venv venv
fi

echo ""
echo "[3/5] Activating virtual environment..."
source venv/bin/activate

echo ""
echo "[4/5] Installing dependencies..."
pip install -q -r requirements.txt

echo ""
echo "[5/5] Starting server..."
echo ""
echo "=========================================="
echo "API will run at: http://localhost:8000"
echo "Docs at: http://localhost:8000/docs"
echo "Health check: http://localhost:8000/health"
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Copy test env if .env doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env from .env.test..."
    cp .env.test .env
fi

# Start uvicorn
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
