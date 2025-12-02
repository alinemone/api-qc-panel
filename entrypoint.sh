#!/bin/bash
set -e

echo "=========================================="
echo "QC Panel API - Starting (Enhanced Logging)"
echo "=========================================="

# Print environment info (without sensitive data)
echo "API_HOST: ${API_HOST:-0.0.0.0}"
echo "API_PORT: ${API_PORT:-8000}"
echo "POSTGRES_HOST: ${POSTGRES_HOST}"
echo "POSTGRES_DATABASE: ${POSTGRES_DATABASE}"
echo "LOG_LEVEL: ${LOG_LEVEL:-INFO}"
echo "=========================================="

# Print Python and system info
echo "System Information:"
python3 --version
echo "Working directory: $(pwd)"
echo "User: $(whoami)"
echo "Python path: $(which python3)"
echo "=========================================="

# Test basic Python imports (don't test database connection)
echo "Testing Python imports..."
python3 << 'PYEOF'
import sys
import traceback

print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")

modules_to_test = [
    ('fastapi', 'FastAPI'),
    ('uvicorn', 'Uvicorn'),
    ('psycopg2', 'PostgreSQL driver'),
    ('pydantic', 'Pydantic'),
]

all_ok = True
for module_name, description in modules_to_test:
    try:
        __import__(module_name)
        print(f"✓ {description} ({module_name}) OK")
    except ImportError as e:
        print(f"✗ {description} ({module_name}) failed: {e}")
        all_ok = False
        sys.exit(1)

# Test main app import
try:
    print("Testing main application import...")
    from config import get_settings
    print("✓ Config OK")

    from main import app
    print("✓ Main app OK")
    print("✓ All imports successful!")
except Exception as e:
    print(f"✗ Main app import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

PYEOF

if [ $? -ne 0 ]; then
    echo "Import test failed. Exiting..."
    exit 1
fi

echo "=========================================="
echo "Starting Uvicorn server..."
echo "=========================================="
echo "Command: uvicorn main:app --host ${API_HOST:-0.0.0.0} --port ${API_PORT:-8000}"
echo "Log level: ${LOG_LEVEL:-info}"
echo "=========================================="

# Trap signals
trap 'echo "ENTRYPOINT: Received SIGTERM, shutting down..."; exit 0' SIGTERM
trap 'echo "ENTRYPOINT: Received SIGINT, shutting down..."; exit 0' SIGINT

# Start uvicorn with explicit error handling
set +e
python3 -m uvicorn main:app \
    --host "${API_HOST:-0.0.0.0}" \
    --port "${API_PORT:-8000}" \
    --log-level "${LOG_LEVEL:-info}" \
    --access-log \
    --no-use-colors
EXIT_CODE=$?
set -e

echo "=========================================="
echo "Uvicorn exited with code: ${EXIT_CODE}"
echo "=========================================="

if [ ${EXIT_CODE} -ne 0 ]; then
    echo "ERROR: Uvicorn failed to start or crashed"
    exit ${EXIT_CODE}
fi

exit 0

