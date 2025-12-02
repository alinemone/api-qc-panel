#!/bin/bash
# Debug script to find why pod is stuck in connecting state

set -e

echo "=========================================="
echo "QC Panel API - Debug Analyzer"
echo "=========================================="

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_section() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Get parameters
NAMESPACE="${1:-default}"
POD_LABEL="${2:-app=api-qcpanel}"

print_section "1. Pod Status"
PODS=$(kubectl get pods -n ${NAMESPACE} -l ${POD_LABEL} -o name 2>/dev/null)

if [ -z "$PODS" ]; then
    print_error "No pods found with label ${POD_LABEL}"
    exit 1
fi

echo "Found pods:"
kubectl get pods -n ${NAMESPACE} -l ${POD_LABEL}

# Get the first pod name
POD_NAME=$(kubectl get pods -n ${NAMESPACE} -l ${POD_LABEL} -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -z "$POD_NAME" ]; then
    print_error "Could not get pod name"
    exit 1
fi

print_success "Checking pod: ${POD_NAME}"

# Check pod phase
PHASE=$(kubectl get pod ${POD_NAME} -n ${NAMESPACE} -o jsonpath='{.status.phase}')
echo "Pod phase: ${PHASE}"

# Check container status
print_section "2. Container Status"
kubectl get pod ${POD_NAME} -n ${NAMESPACE} -o jsonpath='{range .status.containerStatuses[*]}Container: {.name}
State: {.state}
Ready: {.ready}
RestartCount: {.restartCount}
{end}' && echo ""

# Check conditions
print_section "3. Pod Conditions"
kubectl get pod ${POD_NAME} -n ${NAMESPACE} -o jsonpath='{range .status.conditions[*]}{.type}: {.status} - {.message}
{end}'

# Check events
print_section "4. Recent Events"
kubectl get events -n ${NAMESPACE} \
    --field-selector involvedObject.name=${POD_NAME} \
    --sort-by='.lastTimestamp' | tail -20

# Check logs
print_section "5. Container Logs (last 50 lines)"
kubectl logs ${POD_NAME} -n ${NAMESPACE} --tail=50 2>&1 || print_warning "Could not get logs"

# Check previous logs if container restarted
RESTART_COUNT=$(kubectl get pod ${POD_NAME} -n ${NAMESPACE} -o jsonpath='{.status.containerStatuses[0].restartCount}')
if [ "$RESTART_COUNT" -gt 0 ]; then
    print_section "6. Previous Container Logs"
    kubectl logs ${POD_NAME} -n ${NAMESPACE} --previous --tail=50 2>&1 || print_warning "Could not get previous logs"
fi

# Check describe
print_section "7. Pod Description"
kubectl describe pod ${POD_NAME} -n ${NAMESPACE} | grep -A 20 "Events:" || echo "No events section found"

# Check probes
print_section "8. Health Probe Configuration"
kubectl get pod ${POD_NAME} -n ${NAMESPACE} -o jsonpath='{.spec.containers[0].livenessProbe}' | python3 -m json.tool 2>/dev/null || echo "No liveness probe"
echo ""
kubectl get pod ${POD_NAME} -n ${NAMESPACE} -o jsonpath='{.spec.containers[0].readinessProbe}' | python3 -m json.tool 2>/dev/null || echo "No readiness probe"
echo ""
kubectl get pod ${POD_NAME} -n ${NAMESPACE} -o jsonpath='{.spec.containers[0].startupProbe}' | python3 -m json.tool 2>/dev/null || echo "No startup probe"

# Check resources
print_section "9. Resource Usage"
kubectl top pod ${POD_NAME} -n ${NAMESPACE} 2>&1 || print_warning "Could not get resource usage (metrics-server may not be installed)"

# Check resource limits
print_section "10. Resource Limits"
kubectl get pod ${POD_NAME} -n ${NAMESPACE} -o jsonpath='{.spec.containers[0].resources}' | python3 -m json.tool 2>/dev/null || echo "No resource limits"

# Try to exec into pod
print_section "11. Pod Accessibility Test"
kubectl exec ${POD_NAME} -n ${NAMESPACE} -- echo "Pod is accessible" 2>&1 && print_success "Pod exec works" || print_error "Cannot exec into pod"

# Try to curl health endpoint from within pod
print_section "12. Internal Health Check"
kubectl exec ${POD_NAME} -n ${NAMESPACE} -- curl -s -f http://localhost:8000/health 2>&1 && print_success "Health endpoint accessible" || print_error "Health endpoint not accessible"

# Try to curl root endpoint
kubectl exec ${POD_NAME} -n ${NAMESPACE} -- curl -s http://localhost:8000/ 2>&1 | head -5 && print_success "Root endpoint accessible" || print_error "Root endpoint not accessible"

# Check database connectivity from pod
print_section "13. Database Connectivity Test"
POSTGRES_HOST=$(kubectl get pod ${POD_NAME} -n ${NAMESPACE} -o jsonpath='{.spec.containers[0].env[?(@.name=="POSTGRES_HOST")].value}')
if [ ! -z "$POSTGRES_HOST" ]; then
    echo "Testing connection to: ${POSTGRES_HOST}"
    kubectl exec ${POD_NAME} -n ${NAMESPACE} -- ping -c 2 ${POSTGRES_HOST} 2>&1 && print_success "Can reach database host" || print_error "Cannot reach database host"
else
    print_warning "POSTGRES_HOST not set in environment"
fi

# Analyze and provide suggestions
print_section "14. Analysis & Suggestions"

# Check if stuck in initialization
READY=$(kubectl get pod ${POD_NAME} -n ${NAMESPACE} -o jsonpath='{.status.containerStatuses[0].ready}')
STARTED=$(kubectl get pod ${POD_NAME} -n ${NAMESPACE} -o jsonpath='{.status.containerStatuses[0].started}')

if [ "$READY" != "true" ] || [ "$STARTED" != "true" ]; then
    print_error "Container is not ready"

    # Check if it's probe failure
    PROBE_FAILURE=$(kubectl get events -n ${NAMESPACE} --field-selector involvedObject.name=${POD_NAME} | grep -i "probe\|health" || true)
    if [ ! -z "$PROBE_FAILURE" ]; then
        print_warning "Health probe failures detected!"
        echo "$PROBE_FAILURE"
        echo ""
        echo "SOLUTION:"
        echo "1. Increase initialDelaySeconds in probes"
        echo "2. Increase failureThreshold in probes"
        echo "3. Use simpler health check endpoint: /health instead of /health/detailed"
        echo "4. Or deploy without probes: kubectl apply -f k8s-deployment-debug.yaml"
    fi

    # Check if it's OOM
    OOM_CHECK=$(kubectl get events -n ${NAMESPACE} --field-selector involvedObject.name=${POD_NAME} | grep -i "oom\|memory" || true)
    if [ ! -z "$OOM_CHECK" ]; then
        print_error "Out of Memory detected!"
        echo "$OOM_CHECK"
        echo ""
        echo "SOLUTION:"
        echo "1. Increase memory limit to 1Gi:"
        echo "   kubectl patch deployment api-qcpanel -n ${NAMESPACE} --type='json' -p='[{\"op\":\"replace\",\"path\":\"/spec/template/spec/containers/0/resources/limits/memory\",\"value\":\"1Gi\"}]'"
    fi

    # Check if it's database connection
    DB_ERROR=$(kubectl logs ${POD_NAME} -n ${NAMESPACE} --tail=100 2>&1 | grep -i "database\|postgres\|connection" || true)
    if [ ! -z "$DB_ERROR" ]; then
        print_warning "Database connection issues detected"
        echo "$DB_ERROR" | head -10
        echo ""
        echo "SOLUTION:"
        echo "1. Check database host is reachable"
        echo "2. Check database credentials in secrets"
        echo "3. Use simple deployment that doesn't check DB on startup"
    fi
fi

print_section "15. Quick Fix Commands"

echo "# Delete and restart pod:"
echo "kubectl delete pod ${POD_NAME} -n ${NAMESPACE}"
echo ""
echo "# Patch to increase memory:"
echo "kubectl patch deployment api-qcpanel -n ${NAMESPACE} --type='json' -p='[{\"op\":\"replace\",\"path\":\"/spec/template/spec/containers/0/resources/limits/memory\",\"value\":\"1Gi\"}]'"
echo ""
echo "# Deploy debug version (no probes):"
echo "kubectl apply -f k8s-deployment-debug.yaml"
echo ""
echo "# Port forward to test locally:"
echo "kubectl port-forward ${POD_NAME} -n ${NAMESPACE} 8000:8000"
echo ""
echo "# Follow logs:"
echo "kubectl logs -f ${POD_NAME} -n ${NAMESPACE}"

print_section "Done"
