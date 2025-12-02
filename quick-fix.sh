#!/bin/bash
# Quick Fix Script for OOM and async errors

echo "=========================================="
echo "QC Panel API - Quick Fix Deployment"
echo "=========================================="

# رنگ‌ها
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_step() {
    echo -e "\n${GREEN}[STEP]${NC} $1\n"
}

print_info() {
    echo -e "${YELLOW}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# دریافت اطلاعات
read -p "Enter your Docker registry (e.g., registry.example.com): " REGISTRY
read -p "Enter namespace (default: default): " NAMESPACE
NAMESPACE=${NAMESPACE:-default}

IMAGE_NAME="qc-panel-api"
IMAGE_TAG="fix-$(date +%Y%m%d-%H%M%S)"
FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

print_step "1. Building new Docker image..."
print_info "Image: ${FULL_IMAGE}"

docker build -f Dockerfile.simple -t ${IMAGE_NAME}:${IMAGE_TAG} .
if [ $? -ne 0 ]; then
    print_error "Build failed!"
    exit 1
fi

print_step "2. Tagging image..."
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${FULL_IMAGE}

print_step "3. Pushing to registry..."
docker push ${FULL_IMAGE}
if [ $? -ne 0 ]; then
    print_error "Push failed! Check registry credentials"
    exit 1
fi

print_step "4. Updating Kubernetes deployment..."

# Update image
kubectl set image deployment/api-qcpanel \
    api-qcpanel=${FULL_IMAGE} \
    -n ${NAMESPACE}

# Patch memory limits
print_step "5. Updating memory limits to 512Mi..."
kubectl patch deployment api-qcpanel -n ${NAMESPACE} --type='json' -p='[
  {
    "op": "replace",
    "path": "/spec/template/spec/containers/0/resources/limits/memory",
    "value": "512Mi"
  },
  {
    "op": "replace",
    "path": "/spec/template/spec/containers/0/resources/requests/memory",
    "value": "256Mi"
  }
]'

# Update probes
print_step "6. Updating startup probe (more time)..."
kubectl patch deployment api-qcpanel -n ${NAMESPACE} --type='json' -p='[
  {
    "op": "replace",
    "path": "/spec/template/spec/containers/0/startupProbe/failureThreshold",
    "value": 30
  },
  {
    "op": "replace",
    "path": "/spec/template/spec/containers/0/startupProbe/initialDelaySeconds",
    "value": 10
  }
]'

print_step "7. Deleting old pods to force restart..."
kubectl delete pods -n ${NAMESPACE} -l app=api-qcpanel

print_step "8. Waiting for new pods to be ready..."
sleep 5
kubectl rollout status deployment/api-qcpanel -n ${NAMESPACE} --timeout=300s

if [ $? -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo -e "${GREEN}✓ Deployment successful!${NC}"
    echo "=========================================="

    print_step "Pod status:"
    kubectl get pods -n ${NAMESPACE} -l app=api-qcpanel

    print_step "Recent logs:"
    kubectl logs -n ${NAMESPACE} -l app=api-qcpanel --tail=20

    echo ""
    print_info "To follow logs: kubectl logs -f -n ${NAMESPACE} -l app=api-qcpanel"
    print_info "To check memory: kubectl top pods -n ${NAMESPACE} -l app=api-qcpanel"
else
    echo ""
    echo "=========================================="
    echo -e "${RED}✗ Deployment failed!${NC}"
    echo "=========================================="

    print_step "Pod status:"
    kubectl get pods -n ${NAMESPACE} -l app=api-qcpanel

    print_step "Error logs:"
    kubectl logs -n ${NAMESPACE} -l app=api-qcpanel --tail=50

    print_step "Previous pod logs:"
    kubectl logs -n ${NAMESPACE} -l app=api-qcpanel --previous --tail=50 2>/dev/null || echo "No previous logs"

    exit 1
fi
