#!/bin/bash

# QC Panel API Deployment Helper Script

set -e

echo "=========================================="
echo "QC Panel API Deployment Helper"
echo "=========================================="

# Function to check if .env exists
check_env_file() {
    if [ ! -f .env ]; then
        echo "⚠️  Warning: .env file not found!"
        echo "Creating .env from .env.example..."
        if [ -f .env.example ]; then
            cp .env.example .env
            echo "✓ Created .env file. Please edit it with your configuration."
            echo ""
            read -p "Press Enter after editing .env file..."
        else
            echo "✗ .env.example not found. Cannot continue."
            exit 1
        fi
    else
        echo "✓ .env file found"
    fi
}

# Function to build Docker image
build_image() {
    echo ""
    echo "=========================================="
    echo "Building Docker image..."
    echo "=========================================="
    docker build -t qc-panel-api:latest .
    if [ $? -eq 0 ]; then
        echo "✓ Docker image built successfully"
    else
        echo "✗ Docker build failed"
        exit 1
    fi
}

# Function to stop and remove existing container
cleanup_container() {
    echo ""
    echo "=========================================="
    echo "Cleaning up existing container..."
    echo "=========================================="
    if docker ps -a | grep -q qc-panel-api; then
        echo "Stopping and removing existing container..."
        docker stop qc-panel-api 2>/dev/null || true
        docker rm qc-panel-api 2>/dev/null || true
        echo "✓ Cleanup complete"
    else
        echo "No existing container found"
    fi
}

# Function to run container
run_container() {
    echo ""
    echo "=========================================="
    echo "Starting container..."
    echo "=========================================="
    docker run -d \
        --name qc-panel-api \
        -p 8000:8000 \
        --env-file .env \
        --restart unless-stopped \
        qc-panel-api:latest

    if [ $? -eq 0 ]; then
        echo "✓ Container started successfully"
    else
        echo "✗ Failed to start container"
        exit 1
    fi
}

# Function to show logs
show_logs() {
    echo ""
    echo "=========================================="
    echo "Container logs (waiting for startup)..."
    echo "=========================================="
    sleep 2
    docker logs qc-panel-api
    echo ""
    echo "=========================================="
    echo "Following logs (Ctrl+C to exit)..."
    echo "=========================================="
    docker logs -f qc-panel-api
}

# Function to check container status
check_status() {
    echo ""
    echo "=========================================="
    echo "Container status:"
    echo "=========================================="
    docker ps -a | grep qc-panel-api || echo "Container not found"
    echo ""
    echo "Recent logs:"
    echo "=========================================="
    docker logs --tail 50 qc-panel-api 2>&1 || echo "No logs available"
}

# Function to test API
test_api() {
    echo ""
    echo "=========================================="
    echo "Testing API endpoints..."
    echo "=========================================="
    sleep 3

    echo "Testing root endpoint..."
    curl -s http://localhost:8000/ | python -m json.tool || echo "✗ Root endpoint failed"

    echo ""
    echo "Testing health endpoint..."
    curl -s http://localhost:8000/health | python -m json.tool || echo "✗ Health endpoint failed"
}

# Main menu
show_menu() {
    echo ""
    echo "=========================================="
    echo "What would you like to do?"
    echo "=========================================="
    echo "1) Full deploy (build + run)"
    echo "2) Build only"
    echo "3) Run only"
    echo "4) Show logs"
    echo "5) Check status"
    echo "6) Test API"
    echo "7) Stop container"
    echo "8) Restart container"
    echo "9) Exit"
    echo ""
    read -p "Enter choice [1-9]: " choice

    case $choice in
        1)
            check_env_file
            build_image
            cleanup_container
            run_container
            show_logs
            ;;
        2)
            build_image
            ;;
        3)
            check_env_file
            cleanup_container
            run_container
            show_logs
            ;;
        4)
            show_logs
            ;;
        5)
            check_status
            show_menu
            ;;
        6)
            test_api
            show_menu
            ;;
        7)
            cleanup_container
            show_menu
            ;;
        8)
            docker restart qc-panel-api
            echo "✓ Container restarted"
            show_logs
            ;;
        9)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice"
            show_menu
            ;;
    esac
}

# Run main menu
show_menu
