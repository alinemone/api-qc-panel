# 🔴 مشکل: Pod در حالت Connecting گیر کرده

## چرا stuck میشه؟

3 دلیل اصلی:
1. **Health Probe Failing** - Health check fail میشه و Kubernetes فکر میکنه pod ready نیست
2. **Slow Startup** - Application خیلی کند start میشه
3. **Database Connection** - نمیتونه به database وصل بشه

---

## ✅ راه‌حل قطعی (3 روش):

### 🚀 روش 1: Deploy نسخه Debug (سریع‌ترین)

این نسخه بدون health check پیچیده و با memory بیشتر:

```bash
# 1. Build image minimal
docker build -f Dockerfile.minimal -t qc-panel-api:debug .

# 2. Tag و push
docker tag qc-panel-api:debug YOUR_REGISTRY/qc-panel-api:debug
docker push YOUR_REGISTRY/qc-panel-api:debug

# 3. آپدیت image در k8s-deployment-debug.yaml
nano k8s-deployment-debug.yaml
# تغییر بده: image: YOUR_REGISTRY/qc-panel-api:debug

# 4. Delete deployment قدیمی
kubectl delete deployment api-qcpanel

# 5. Deploy نسخه debug
kubectl apply -f k8s-deployment-debug.yaml

# 6. چک کن
kubectl get pods -l app=api-qcpanel-debug
kubectl logs -f -l app=api-qcpanel-debug
```

---

### 🔍 روش 2: Debug کردن Pod فعلی

اول بفهم دقیقاً کجا گیر کرده:

```bash
# اجرای script debug
chmod +x debug-pod.sh
./debug-pod.sh

# یا دستی:
POD_NAME=$(kubectl get pods -l app=api-qcpanel -o jsonpath='{.items[0].metadata.name}')

# 1. چک کن pod چه وضعیتی داره
kubectl describe pod $POD_NAME | grep -A 20 "Events:"

# 2. ببین چرا ready نیست
kubectl get pod $POD_NAME -o jsonpath='{.status.conditions[*]}' | python3 -m json.tool

# 3. لاگ رو ببین
kubectl logs $POD_NAME --tail=100

# 4. تست کن health endpoint
kubectl exec $POD_NAME -- curl -s http://localhost:8000/health

# 5. تست کن که app اصلاً start شده؟
kubectl exec $POD_NAME -- curl -s http://localhost:8000/
```

---

### ⚡ روش 3: Fix سریع با Patch

اگه فهمیدی مشکل چیه، سریع fix کن:

#### مشکل 1: Health Probe Fail میشه

```bash
# Disable startup probe
kubectl patch deployment api-qcpanel --type='json' -p='[
  {"op":"remove","path":"/spec/template/spec/containers/0/startupProbe"}
]'

# یا زمان بیشتر بده
kubectl patch deployment api-qcpanel --type='json' -p='[
  {"op":"replace","path":"/spec/template/spec/containers/0/startupProbe/failureThreshold","value":60},
  {"op":"replace","path":"/spec/template/spec/containers/0/readinessProbe/failureThreshold","value":60}
]'
```

#### مشکل 2: Memory کمه (OOM)

```bash
kubectl patch deployment api-qcpanel --type='json' -p='[
  {"op":"replace","path":"/spec/template/spec/containers/0/resources/limits/memory","value":"1Gi"}
]'
```

#### مشکل 3: Image قدیمیه

```bash
# Force update image
kubectl set image deployment/api-qcpanel \
  api-qcpanel=YOUR_REGISTRY/qc-panel-api:debug

# Delete pod های قدیمی
kubectl delete pods -l app=api-qcpanel
```

---

## 📋 چک‌لیست Debug:

اجرا کن و نتیجه رو بررسی کن:

```bash
# 1. Pod اصلاً ساخته شده؟
kubectl get pods -l app=api-qcpanel
# Expected: باید 1 یا چند pod ببینی

# 2. Pod چه statusی داره؟
kubectl get pods -l app=api-qcpanel -o wide
# اگه: Pending → منابع کافی نیست
# اگه: CrashLoopBackOff → application کرش میکنه
# اگه: Running اما 0/1 ready → health check fail میشه

# 3. چرا ready نیست؟
POD=$(kubectl get pods -l app=api-qcpanel -o jsonpath='{.items[0].metadata.name}')
kubectl describe pod $POD | grep -i "ready\|health\|probe"
# اگه "Readiness probe failed" → probe مشکل داره

# 4. لاگ چی میگه؟
kubectl logs $POD --tail=50
# باید ببینی: "Starting Uvicorn server"
# اگه error بود، مشکل در application هست

# 5. Application start شده؟
kubectl exec $POD -- curl -s http://localhost:8000/ 2>&1
# اگه جواب داد → app کار میکنه، مشکل probe هست
# اگه error → app start نشده

# 6. Health endpoint کار میکنه؟
kubectl exec $POD -- curl -s http://localhost:8000/health
# باید بگه: {"status":"healthy",...}

# 7. Memory usage چقدره؟
kubectl top pod $POD
# اگه نزدیک limit هست → OOM خواهد شد
```

---

## 🎯 سناریوهای مختلف:

### سناریو A: Pod در "0/1 Running" گیر کرده

**علت**: Health probe fail میشه

**حل**:
```bash
# Deploy بدون probe
kubectl apply -f k8s-deployment-debug.yaml
```

### سناریو B: Pod دائم Restart میشه

**علت**: OOM یا application crash

**حل**:
```bash
# Memory افزایش
kubectl patch deployment api-qcpanel --type='json' -p='[
  {"op":"replace","path":"/spec/template/spec/containers/0/resources/limits/memory","value":"1Gi"}
]'

# لاگ ببین
kubectl logs -l app=api-qcpanel --previous
```

### سناریو C: Pod هیچوقت Ready نمیشه

**علت**: Startup خیلی طول میکشه یا database مشکل داره

**حل**:
```bash
# زمان بیشتر به startup بده
kubectl patch deployment api-qcpanel --type='json' -p='[
  {"op":"replace","path":"/spec/template/spec/containers/0/startupProbe/initialDelaySeconds","value":60},
  {"op":"replace","path":"/spec/template/spec/containers/0/startupProbe/failureThreshold","value":60}
]'
```

### سناریو D: "ImagePullBackOff"

**علت**: Image رو نمیتونه pull کنه

**حل**:
```bash
# چک کن image درسته
kubectl describe pod -l app=api-qcpanel | grep "Image:"

# چک کن image pull secret
kubectl get secret

# اگه registry private هست، secret اضافه کن
kubectl create secret docker-registry regcred \
  --docker-server=YOUR_REGISTRY \
  --docker-username=YOUR_USERNAME \
  --docker-password=YOUR_PASSWORD
```

---

## 🆘 هنوز کار نکرد؟

### گام 1: Debug کامل

```bash
chmod +x debug-pod.sh
./debug-pod.sh > debug-output.txt
cat debug-output.txt
```

### گام 2: Test محلی

```bash
# Port forward کن
kubectl port-forward svc/api-qcpanel 8000:8000 &

# Test کن
curl http://localhost:8000/
curl http://localhost:8000/health

# اگه کار کرد = probe مشکل داره
# اگه کار نکرد = application مشکل داره
```

### گام 3: Test دستی در Pod

```bash
POD=$(kubectl get pods -l app=api-qcpanel -o jsonpath='{.items[0].metadata.name}')

# وارد pod شو
kubectl exec -it $POD -- /bin/bash

# داخل pod:
curl http://localhost:8000/
curl http://localhost:8000/health
python3 -c "from main import app; print('OK')"
python3 -c "from database import get_db_connection; get_db_connection()"
```

---

## 🔧 فایل‌های جدید:

1. **`main.py`** - Health check ساده بدون database ✅
2. **`Dockerfile.minimal`** - خیلی ساده، بدون complexity ✅
3. **`k8s-deployment-debug.yaml`** - بدون startup probe، memory زیاد ✅
4. **`debug-pod.sh`** - Script جامع debug ✅

---

## 💡 نکات کلیدی:

1. **همیشه لاگ رو ببین** - `kubectl logs -f POD_NAME`
2. **همیشه describe رو ببین** - `kubectl describe pod POD_NAME`
3. **همیشه exec کن و test کن** - `kubectl exec POD_NAME -- curl localhost:8000/health`
4. **از deployment-debug استفاده کن** - ساده‌تر و بدون مشکل probe

---

## ✅ دستورات نهایی (کپی-پیست):

```bash
# همه فایل‌ها رو آپدیت کن
git pull  # یا scp files

# Build minimal
docker build -f Dockerfile.minimal -t YOUR_REGISTRY/qc-panel-api:debug .
docker push YOUR_REGISTRY/qc-panel-api:debug

# آپدیت k8s-deployment-debug.yaml با registry خودت
sed -i 's|your-registry|YOUR_ACTUAL_REGISTRY|g' k8s-deployment-debug.yaml

# Delete قدیمی
kubectl delete deployment api-qcpanel

# Deploy جدید
kubectl apply -f k8s-deployment-debug.yaml

# چک کن
kubectl get pods -l app=api-qcpanel-debug
kubectl logs -f -l app=api-qcpanel-debug

# اگه بالا اومد
kubectl port-forward svc/api-qcpanel-debug 8000:8000
curl http://localhost:8000/health
```

موفق باشی! 🚀
