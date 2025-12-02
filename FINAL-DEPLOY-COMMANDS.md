# تمام دستورات لازم برای Deploy قطعی

## 🚨 اون لاگی که میبینی = Image قدیمیه!

اگه این error ها رو میبینی یعنی **هنوز image جدید deploy نشده**:
```
Exit code 137
'NoneType' object has no attribute 'send'
```

---

## ✅ راه‌حل قطعی (کپی-پیست کن):

### مرحله 1: مطمئن شو فایل‌های جدید داری

```bash
cd /path/to/api-qc-panel

# چک کن که این فایل‌ها وجود دارن و جدید هستن
ls -lh main.py Dockerfile.minimal force-deploy.sh

# ببین main.py تاریخ امروز داره؟
stat main.py
```

اگه فایل‌ها جدید نیستن:
```bash
# از git pull کن
git pull

# یا فایل‌ها رو دستی کپی کن از کامپیوتر محلی
scp main.py Dockerfile.minimal force-deploy.sh server:/path/to/api-qc-panel/
```

---

### مرحله 2: استفاده از Script اتوماتیک (توصیه می‌شه)

```bash
chmod +x force-deploy.sh
./force-deploy.sh

# بهت می‌پرسه:
# Registry: مثلاً harbor.example.com/myproject
# Namespace: default یا namespace خودت
# Confirm: yes
```

این script:
- ✅ Build میکنه image جدید
- ✅ Push میکنه
- ✅ Delete میکنه deployment قدیمی
- ✅ Deploy میکنه deployment جدید
- ✅ Verify میکنه image درسته
- ✅ لاگ رو نشون میده

---

### مرحله 3: دستی (اگه script کار نکرد)

```bash
# 1. Set variables
REGISTRY="your-registry.com/project"  # تغییر بده!
NAMESPACE="default"  # تغییر بده اگه لازمه
IMAGE_TAG="v$(date +%Y%m%d-%H%M%S)"

# 2. Build
docker build -f Dockerfile.minimal -t qc-panel-api:${IMAGE_TAG} .

# 3. Tag
docker tag qc-panel-api:${IMAGE_TAG} ${REGISTRY}/qc-panel-api:${IMAGE_TAG}

# 4. Push
docker push ${REGISTRY}/qc-panel-api:${IMAGE_TAG}

# 5. Delete old deployment
kubectl delete deployment api-qcpanel -n ${NAMESPACE}

# 6. Create new deployment
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-qcpanel
  namespace: ${NAMESPACE}
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
        image: ${REGISTRY}/qc-panel-api:${IMAGE_TAG}
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: api-qcpanel-config
            optional: true
        - secretRef:
            name: api-qcpanel-secrets
            optional: true
        resources:
          limits:
            memory: "1Gi"
            cpu: "1000m"
          requests:
            memory: "512Mi"
            cpu: "250m"
        livenessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 90
          periodSeconds: 30
          failureThreshold: 5
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 60
          periodSeconds: 10
          failureThreshold: 10
---
apiVersion: v1
kind: Service
metadata:
  name: api-qcpanel
  namespace: ${NAMESPACE}
spec:
  type: ClusterIP
  selector:
    app: api-qcpanel
  ports:
  - port: 8000
    targetPort: 8000
EOF

# 7. Wait and check
sleep 10
kubectl get pods -n ${NAMESPACE} -l app=api-qcpanel

# 8. Verify image
POD=$(kubectl get pods -n ${NAMESPACE} -l app=api-qcpanel -o jsonpath='{.items[0].metadata.name}')
echo "Pod: $POD"
echo "Using image:"
kubectl get pod $POD -n ${NAMESPACE} -o jsonpath='{.spec.containers[0].image}'
echo ""

# 9. Check logs
kubectl logs -f $POD -n ${NAMESPACE}
```

---

## 🔍 چک کن که Image جدیده:

بعد از deploy، این رو اجرا کن:

```bash
POD=$(kubectl get pods -l app=api-qcpanel -o jsonpath='{.items[0].metadata.name}')

echo "=== POD INFO ==="
kubectl get pod $POD

echo -e "\n=== IMAGE BEING USED ==="
kubectl get pod $POD -o jsonpath='{.spec.containers[0].image}'

echo -e "\n\n=== LOGS (should be NEW) ==="
kubectl logs $POD --tail=20
```

### اگه Image جدیده، باید این لاگ‌ها رو ببینی:

```
==========================================
Testing Python imports...
Python version: 3.11.x
✓ FastAPI OK
✓ Uvicorn OK
✓ Config OK
✓ Main app OK
✓ All imports successful!
==========================================
Starting Uvicorn server...
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### اگه Image قدیمیه، باز این error ها رو میبینی:

```
Exit code 137
'NoneType' object has no attribute 'send'
```

---

## ❌ اگه هنوز image قدیمیه:

### چک 1: Image واقعاً push شده؟

```bash
# لیست images در registry
docker images | grep qc-panel-api

# اگه داری از private registry استفاده می‌کنی، login کن
docker login YOUR_REGISTRY
```

### چک 2: Kubernetes میتونه image رو pull کنه؟

```bash
POD=$(kubectl get pods -l app=api-qcpanel -o jsonpath='{.items[0].metadata.name}')

# ببین event ها چی میگن
kubectl describe pod $POD | grep -i "image\|pull"

# اگه ImagePullBackOff بود:
# - چک کن image name درسته
# - چک کن registry credentials درسته
# - اگه private registry هست، imagePullSecret اضافه کن
```

### چک 3: Pod واقعاً جدیده؟

```bash
# ببین pod creation time
kubectl get pods -l app=api-qcpanel -o wide

# اگه pod قدیمیه (چند ساعت یا روز Age داره)، force delete کن
kubectl delete pods -l app=api-qcpanel --force --grace-period=0

# یا deployment رو restart کن
kubectl rollout restart deployment/api-qcpanel
```

### چک 4: از Deployment درستی استفاده می‌کنی؟

```bash
# ببین چند تا deployment داری
kubectl get deployments

# شاید 2 تا deployment داری و از قدیمی استفاده میکنی؟
# اگه api-qcpanel-debug یا اسم دیگه ای داری، اونا رو delete کن
kubectl delete deployment api-qcpanel-old
kubectl delete deployment api-qcpanel-debug
```

---

## 🎯 تست نهایی:

وقتی pod بالا اومد:

```bash
POD=$(kubectl get pods -l app=api-qcpanel -o jsonpath='{.items[0].metadata.name}')

# 1. Test health endpoint
kubectl exec $POD -- curl -s http://localhost:8000/health

# باید ببینی:
# {"status":"healthy","service":"qc-panel-api","version":"1.0.0"}

# 2. Test root endpoint
kubectl exec $POD -- curl -s http://localhost:8000/

# باید ببینی:
# {"message":"QC Panel API","version":"1.0.0","status":"running"}

# 3. Port forward و test از خارج
kubectl port-forward $POD 8000:8000 &
curl http://localhost:8000/health
```

---

## 💡 نکات مهم:

1. **حتماً Dockerfile.minimal استفاده کن** - نه Dockerfile یا Dockerfile.simple
2. **حتماً deployment قدیمی رو delete کن** - قبل از deploy جدید
3. **حتماً image tag جدید استفاده کن** - نه latest
4. **حتماً بعد از deploy، image رو verify کن** - با `kubectl get pod -o jsonpath`

---

## 🆘 اگه باز هم کار نکرد:

این دستورات رو بزن و output رو بهم بده:

```bash
# 1. List all deployments
kubectl get deployments --all-namespaces | grep qc

# 2. List all pods
kubectl get pods --all-namespaces | grep qc

# 3. Describe pod
POD=$(kubectl get pods -l app=api-qcpanel -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod $POD > pod-describe.txt

# 4. Check image
kubectl get pod $POD -o yaml | grep -A 3 "image:" > pod-image.txt

# 5. Get logs
kubectl logs $POD > pod-logs.txt

# این 3 فایل رو بهم بفرست
cat pod-describe.txt
cat pod-image.txt
cat pod-logs.txt
```

موفق باشی! 🚀
