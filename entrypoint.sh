#!/bin/bash
set -e

echo "=========================================="
echo "Starting QC Panel API"
echo "=========================================="

# Print environment info (without sensitive data)
echo "API_HOST: ${API_HOST:-0.0.0.0}"
echo "API_PORT: ${API_PORT:-8000}"
echo "POSTGRES_HOST: ${POSTGRES_HOST:-not set}"
echo "POSTGRES_DATABASE: ${POSTGRES_DATABASE:-not set}"
echo "=========================================="

# Test Python imports
echo "Testing Python imports..."
python -c "
import sys
print('Python version:', sys.version)

try:
    import fastapi
    print('✓ FastAPI imported successfully')
except ImportError as e:
    print('✗ FastAPI import failed:', e)
    sys.exit(1)

try:
    import uvicorn
    print('✓ Uvicorn imported successfully')
except ImportError as e:
    print('✗ Uvicorn import failed:', e)
    sys.exit(1)

try:
    from config import get_settings
    settings = get_settings()
    print('✓ Config loaded successfully')
except Exception as e:
    print('✗ Config load failed:', e)
    sys.exit(1)

try:
    from database import get_db_connection
    print('✓ Database module loaded successfully')
except Exception as e:
    print('✗ Database module load failed:', e)
    sys.exit(1)

try:
    from routes import auth, users, conversations
    print('✓ Routes loaded successfully')
except Exception as e:
    print('✗ Routes load failed:', e)
    sys.exit(1)

print('✓ All imports successful!')
"

if [ $? -ne 0 ]; then
    echo "Failed to import required modules. Exiting..."
    exit 1
fi

echo "=========================================="
echo "Starting Uvicorn server..."
echo "=========================================="

# Start uvicorn with proper error handling
exec uvicorn main:app \
    --host "${API_HOST:-0.0.0.0}" \
    --port "${API_PORT:-8000}" \
    --log-level info \
    --access-log \
    --no-use-colors
