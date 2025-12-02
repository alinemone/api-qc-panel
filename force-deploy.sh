#!/bin/bash
# Force Deploy New Image - No Mistakes

set -e

echo "=========================================="
echo "FORCE DEPLOY NEW IMAGE"
echo "=========================================="

# رنگ‌ها
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() {
    echo -e "\n${GREEN}>>> $1${NC}\n"
}

print_error() {
    echo -e "${RED}ERROR: $1${NC}"
    exit 1
}

# دریافت اطلاعات
echo "Enter your Docker registry (e.g., registry.example.com/project):"
read -p "Registry: " REGISTRY

if [ -z "$REGISTRY" ]; then
    print_error "Registry cannot be empty!"
fi

read -p "Kubernetes namespace (default: default): " NAMESPACE
NAMESPACE=${NAMESPACE:-default}

IMAGE_TAG="v-$(date +%Y%m%d-%H%M%S)"
IMAGE_NAME="qc-panel-api"
FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"

echo ""
echo "Will deploy:"
echo "  Image: ${FULL_IMAGE}"
echo "  Namespace: ${NAMESPACE}"
echo ""
read -p "Continue? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "Cancelled"
    exit 0
fi

# ========================================
print_step "1. Checking current deployment"
kubectl get deployment api-qcpanel -n ${NAMESPACE} 2>/dev/null && HAS_DEPLOYMENT=1 || HAS_DEPLOYMENT=0

if [ $HAS_DEPLOYMENT -eq 1 ]; then
    echo "Current deployment image:"
    kubectl get deployment api-qcpanel -n ${NAMESPACE} -o jsonpath='{.spec.template.spec.containers[0].image}'
    echo ""
fi

# ========================================
print_step "2. Building NEW image"
echo "Using Dockerfile.minimal..."

if [ ! -f "Dockerfile.minimal" ]; then
    print_error "Dockerfile.minimal not found! Make sure you have the latest files."
fi

if [ ! -f "main.py" ]; then
    print_error "main.py not found!"
fi

docker build -f Dockerfile.minimal -t ${IMAGE_NAME}:${IMAGE_TAG} . || print_error "Build failed!"

echo -e "${GREEN}✓ Build successful${NC}"

# ========================================
print_step "3. Tagging image"
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${FULL_IMAGE} || print_error "Tag failed!"

# ========================================
print_step "4. Pushing to registry"
echo "Pushing ${FULL_IMAGE}..."
docker push ${FULL_IMAGE} || print_error "Push failed! Check registry credentials (docker login)"

echo -e "${GREEN}✓ Image pushed successfully${NC}"

# ========================================
print_step "5. Preparing Kubernetes deployment"

# Create temp deployment file
cat > /tmp/qcpanel-deploy-new.yaml <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-qcpanel
  labels:
    app: api-qcpanel
spec:
  replicas: 1
  selector:
    matchLabels:
      app: api-qcpanel
  template:
    metadata:
      labels:
        app: api-qcpanel
    spec:
      containers:
      - name: api-qcpanel
        image: ${FULL_IMAGE}
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
          name: http
        envFrom:
        - configMapRef:
            name: api-qcpanel-config
            optional: true
        - secretRef:
            name: api-qcpanel-secrets
            optional: true
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        # NO STARTUP PROBE - let it start freely
        livenessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 90
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 5
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 10
      restartPolicy: Always
---
apiVersion: v1
kind: Service
metadata:
  name: api-qcpanel
  labels:
    app: api-qcpanel
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
    name: http
  selector:
    app: api-qcpanel
EOF

echo "Deployment file created at /tmp/qcpanel-deploy-new.yaml"

# ========================================
print_step "6. Deleting old deployment"
kubectl delete deployment api-qcpanel -n ${NAMESPACE} 2>/dev/null && echo "Old deployment deleted" || echo "No old deployment found"

# Wait a bit
sleep 3

# ========================================
print_step "7. Deploying NEW deployment"
kubectl apply -f /tmp/qcpanel-deploy-new.yaml -n ${NAMESPACE} || print_error "Deployment failed!"

echo -e "${GREEN}✓ Deployment applied${NC}"

# ========================================
print_step "8. Waiting for pods to be created"
sleep 5

POD_NAME=""
for i in {1..30}; do
    POD_NAME=$(kubectl get pods -n ${NAMESPACE} -l app=api-qcpanel -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")
    if [ ! -z "$POD_NAME" ]; then
        echo "Pod created: ${POD_NAME}"
        break
    fi
    echo "Waiting for pod... ($i/30)"
    sleep 2
done

if [ -z "$POD_NAME" ]; then
    print_error "Pod was not created!"
fi

# ========================================
print_step "9. Verifying image"
ACTUAL_IMAGE=$(kubectl get pod ${POD_NAME} -n ${NAMESPACE} -o jsonpath='{.spec.containers[0].image}')
echo "Pod is using image: ${ACTUAL_IMAGE}"

if [ "${ACTUAL_IMAGE}" != "${FULL_IMAGE}" ]; then
    echo -e "${RED}WARNING: Image mismatch!${NC}"
    echo "Expected: ${FULL_IMAGE}"
    echo "Actual: ${ACTUAL_IMAGE}"
else
    echo -e "${GREEN}✓ Image is correct!${NC}"
fi

# ========================================
print_step "10. Following logs (Ctrl+C to exit)"
echo "Watching pod: ${POD_NAME}"
echo "You should see:"
echo "  - Python version"
echo "  - ✓ FastAPI OK"
echo "  - ✓ Uvicorn OK"
echo "  - ✓ Config OK"
echo "  - ✓ Main app OK"
echo "  - Starting Uvicorn server..."
echo ""
echo "If you see old errors (Exit 137, NoneType), something is wrong!"
echo ""

sleep 3
kubectl logs -f ${POD_NAME} -n ${NAMESPACE}
