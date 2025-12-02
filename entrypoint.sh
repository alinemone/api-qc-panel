#!/bin/bash
set -e

echo "=========================================="
echo "QC Panel API - Starting"
echo "=========================================="

# Print environment info (without sensitive data)
echo "API_HOST: ${API_HOST:-0.0.0.0}"
echo "API_PORT: ${API_PORT:-8000}"
echo "POSTGRES_HOST: ${POSTGRES_HOST}"
echo "POSTGRES_DATABASE: ${POSTGRES_DATABASE}"
echo "=========================================="

# Test basic Python imports (don't test database connection)
echo "Testing Python imports..."
python3 << 'PYEOF'
import sys
print(f"Python version: {sys.version}")

try:
    import fastapi
    print("✓ FastAPI OK")
except ImportError as e:
    print(f"✗ FastAPI failed: {e}")
    sys.exit(1)

try:
    import uvicorn
    print("✓ Uvicorn OK")
except ImportError as e:
    print(f"✗ Uvicorn failed: {e}")
    sys.exit(1)

try:
    from config import get_settings
    settings = get_settings()
    print("✓ Config OK")
except Exception as e:
    print(f"✗ Config failed: {e}")
    sys.exit(1)

try:
    from main import app
    print("✓ Main app OK")
except Exception as e:
    print(f"✗ Main app failed: {e}")
    sys.exit(1)

print("✓ All imports successful!")
PYEOF

if [ $? -ne 0 ]; then
    echo "Import test failed. Exiting..."
    exit 1
fi

echo "=========================================="
echo "Starting Uvicorn server..."
echo "=========================================="

# Start uvicorn
exec uvicorn main:app \
    --host "${API_HOST:-0.0.0.0}" \
    --port "${API_PORT:-8000}" \
    --log-level info \
    --access-log

