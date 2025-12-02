#!/bin/bash

# Kubernetes Deployment Script for QC Panel API

set -e

echo "=========================================="
echo "QC Panel API - Kubernetes Deployment"
echo "=========================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="default"
IMAGE_NAME="qc-panel-api"
IMAGE_TAG="latest"
REGISTRY=""  # Set your registry here

# Function to print colored messages
print_info() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl not found. Please install kubectl first."
        exit 1
    fi
    print_info "kubectl found"
}

# Function to check if connected to cluster
check_cluster() {
    if ! kubectl cluster-info &> /dev/null; then
        print_error "Not connected to Kubernetes cluster"
        exit 1
    fi
    print_info "Connected to cluster: $(kubectl config current-context)"
}

# Function to build Docker image
build_image() {
    echo ""
    echo "=========================================="
    echo "Building Docker image..."
    echo "=========================================="

    docker build -f Dockerfile.simple -t ${IMAGE_NAME}:${IMAGE_TAG} .

    if [ $? -eq 0 ]; then
        print_info "Image built successfully"
    else
        print_error "Image build failed"
        exit 1
    fi
}

# Function to tag and push image
push_image() {
    if [ -z "$REGISTRY" ]; then
        print_warning "REGISTRY not set. Skipping push."
        print_warning "Set REGISTRY variable in this script or export REGISTRY=your-registry.com"
        return
    fi

    echo ""
    echo "=========================================="
    echo "Pushing image to registry..."
    echo "=========================================="

    docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
    docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

    if [ $? -eq 0 ]; then
        print_info "Image pushed successfully"
    else
        print_error "Image push failed"
        exit 1
    fi
}

# Function to apply ConfigMap and Secrets
apply_config() {
    echo ""
    echo "=========================================="
    echo "Applying ConfigMap and Secrets..."
    echo "=========================================="

    if [ -f k8s-config.yaml ]; then
        print_warning "Please update k8s-config.yaml with your actual secrets before applying!"
        read -p "Have you updated the secrets? (yes/no): " answer
        if [ "$answer" != "yes" ]; then
            print_error "Please update secrets first"
            exit 1
        fi

        kubectl apply -f k8s-config.yaml -n ${NAMESPACE}
        print_info "ConfigMap and Secrets applied"
    else
        print_error "k8s-config.yaml not found"
        exit 1
    fi
}

# Function to apply deployment
apply_deployment() {
    echo ""
    echo "=========================================="
    echo "Applying Deployment..."
    echo "=========================================="

    if [ -f k8s-deployment.yaml ]; then
        # Update image in deployment if registry is set
        if [ ! -z "$REGISTRY" ]; then
            sed -i "s|image:.*|image: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}|g" k8s-deployment.yaml
        fi

        kubectl apply -f k8s-deployment.yaml -n ${NAMESPACE}
        print_info "Deployment applied"
    else
        print_error "k8s-deployment.yaml not found"
        exit 1
    fi
}

# Function to apply HPA
apply_hpa() {
    echo ""
    echo "=========================================="
    echo "Applying HPA..."
    echo "=========================================="

    if [ -f k8s-hpa.yaml ]; then
        kubectl apply -f k8s-hpa.yaml -n ${NAMESPACE}
        print_info "HPA applied"
    else
        print_warning "k8s-hpa.yaml not found, skipping HPA"
    fi
}

# Function to wait for deployment
wait_for_deployment() {
    echo ""
    echo "=========================================="
    echo "Waiting for deployment to be ready..."
    echo "=========================================="

    kubectl rollout status deployment/api-qcpanel -n ${NAMESPACE} --timeout=300s

    if [ $? -eq 0 ]; then
        print_info "Deployment is ready"
    else
        print_error "Deployment failed to become ready"
        echo ""
        print_warning "Recent pod logs:"
        kubectl logs -n ${NAMESPACE} -l app=api-qcpanel --tail=50
        exit 1
    fi
}

# Function to show status
show_status() {
    echo ""
    echo "=========================================="
    echo "Deployment Status"
    echo "=========================================="

    echo ""
    echo "Pods:"
    kubectl get pods -n ${NAMESPACE} -l app=api-qcpanel

    echo ""
    echo "Services:"
    kubectl get svc -n ${NAMESPACE} -l app=api-qcpanel

    echo ""
    echo "HPA:"
    kubectl get hpa -n ${NAMESPACE} api-qcpanel-hpa 2>/dev/null || echo "HPA not found"
}

# Function to show logs
show_logs() {
    echo ""
    echo "=========================================="
    echo "Recent logs:"
    echo "=========================================="
    kubectl logs -n ${NAMESPACE} -l app=api-qcpanel --tail=100
}

# Function to delete deployment
delete_deployment() {
    echo ""
    echo "=========================================="
    echo "Deleting deployment..."
    echo "=========================================="

    kubectl delete -f k8s-deployment.yaml -n ${NAMESPACE} 2>/dev/null || true
    kubectl delete -f k8s-hpa.yaml -n ${NAMESPACE} 2>/dev/null || true
    kubectl delete -f k8s-config.yaml -n ${NAMESPACE} 2>/dev/null || true

    print_info "Deployment deleted"
}

# Main menu
show_menu() {
    echo ""
    echo "=========================================="
    echo "What would you like to do?"
    echo "=========================================="
    echo "1) Full deployment (build + push + deploy)"
    echo "2) Build image only"
    echo "3) Deploy only (skip build)"
    echo "4) Update deployment (rolling update)"
    echo "5) Show status"
    echo "6) Show logs"
    echo "7) Delete deployment"
    echo "8) Exit"
    echo ""
    read -p "Enter choice [1-8]: " choice

    case $choice in
        1)
            check_kubectl
            check_cluster
            build_image
            push_image
            apply_config
            apply_deployment
            apply_hpa
            wait_for_deployment
            show_status
            ;;
        2)
            build_image
            show_menu
            ;;
        3)
            check_kubectl
            check_cluster
            apply_config
            apply_deployment
            apply_hpa
            wait_for_deployment
            show_status
            ;;
        4)
            check_kubectl
            check_cluster
            kubectl rollout restart deployment/api-qcpanel -n ${NAMESPACE}
            wait_for_deployment
            show_status
            ;;
        5)
            check_kubectl
            check_cluster
            show_status
            show_menu
            ;;
        6)
            check_kubectl
            check_cluster
            show_logs
            show_menu
            ;;
        7)
            check_kubectl
            check_cluster
            delete_deployment
            show_menu
            ;;
        8)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice"
            show_menu
            ;;
    esac
}

# Check for namespace argument
if [ ! -z "$1" ]; then
    NAMESPACE=$1
    print_info "Using namespace: ${NAMESPACE}"
fi

# Check for registry argument
if [ ! -z "$2" ]; then
    REGISTRY=$2
    print_info "Using registry: ${REGISTRY}"
fi

# Run main menu
show_menu
