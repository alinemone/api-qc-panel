# حل مشکل Exit Code 137 (Out of Memory) و Crash Loop

## مشکل شما:
- Container با exit code 137 کشته میشه = **Out of Memory (OOM)**
- Error: `'NoneType' object has no attribute 'send'` = مشکل **async/await**

## تغییراتی که انجام شد:

### 1. Fix کردن Async/Await ✅
فایل `main.py` رو آپدیت کردم:
- Health check endpoint حالا به درستی async هست
- Database connection رو در thread pool اجرا می‌کنه
- Startup event اضافه شد که در startup database رو چک نمی‌کنه

### 2. Kubernetes Deployment Files ✅
فایل‌های زیر رو ساختم:
- `k8s-deployment.yaml` - با memory limits مناسب
- `k8s-config.yaml` - ConfigMap و Secrets
- `k8s-hpa.yaml` - Auto-scaling
- `k8s-deploy.sh` - Script اتوماتیک deployment

## راه حل فوری: 🚀

### مرحله 1: Update کردن Deployment با Memory بیشتر

```bash
kubectl edit deployment api-qcpanel
```

و resource limits رو تغییر بدید:

```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"  # ← قبلاً کمتر بود، این رو افزایش دهید
    cpu: "500m"
```

### مرحله 2: Fix کردن Probes

```yaml
startupProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 30  # ← 150 ثانیه زمان برای startup

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30  # ← زمان بیشتر قبل از اولین check
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

### مرحله 3: Rebuild و Redeploy

```bash
# 1. Build image جدید با fix ها
docker build -f Dockerfile.simple -t your-registry/qc-panel-api:latest .

# 2. Push کن
docker push your-registry/qc-panel-api:latest

# 3. Restart deployment
kubectl rollout restart deployment/api-qcpanel

# 4. لاگ ببین
kubectl logs -f deployment/api-qcpanel
```

## استفاده از فایل‌های جدید Kubernetes:

### نصب سریع:

```bash
# 1. آپدیت کن secrets در k8s-config.yaml
nano k8s-config.yaml

# 2. Apply کن
kubectl apply -f k8s-config.yaml
kubectl apply -f k8s-deployment.yaml
kubectl apply -f k8s-hpa.yaml

# 3. چک کن
kubectl get pods -l app=api-qcpanel
kubectl logs -f deployment/api-qcpanel
```

### استفاده از Script:

```bash
chmod +x k8s-deploy.sh
./k8s-deploy.sh

# یا با namespace مشخص
./k8s-deploy.sh your-namespace your-registry.com
```

## Debug در Kubernetes:

### 1. بررسی چرا OOM شده:

```bash
# Status pod
kubectl describe pod <pod-name>

# بررسی events
kubectl get events --sort-by='.lastTimestamp' | grep api-qcpanel

# Memory usage فعلی
kubectl top pod -l app=api-qcpanel
```

### 2. دیدن لاگ‌های کامل:

```bash
# لاگ pod فعلی
kubectl logs -l app=api-qcpanel --tail=200

# لاگ pod قبلی (اگه کرش کرده)
kubectl logs -l app=api-qcpanel --previous

# لاگ همه containers
kubectl logs -l app=api-qcpanel --all-containers=true
```

### 3. تست دستی داخل Pod:

```bash
# وارد pod شو
kubectl exec -it deployment/api-qcpanel -- /bin/bash

# داخل pod تست کن
curl http://localhost:8000/
curl http://localhost:8000/health
python3 -c "from main import app; print('OK')"
```

### 4. بررسی Resource Usage:

```bash
# Usage فعلی
kubectl top pods -l app=api-qcpanel

# Metrics server رو چک کن
kubectl get pods -n kube-system | grep metrics

# Resource limits deployment
kubectl describe deployment api-qcpanel | grep -A 10 "Limits"
```

## تنظیمات پیشنهادی Resource:

### برای Traffic کم:
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "250m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

### برای Traffic متوسط:
```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "500m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

### برای Traffic زیاد:
```yaml
resources:
  requests:
    memory: "1Gi"
    cpu: "1000m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

## چک لیست نهایی:

- [ ] `main.py` رو آپدیت کردید (async/await fix)
- [ ] Docker image جدید build کردید
- [ ] Memory limits رو افزایش دادید (حداقل 512Mi)
- [ ] startupProbe زمان بیشتری داره (failureThreshold: 30)
- [ ] Database host در ConfigMap درست است
- [ ] Secrets رو آپدیت کردید
- [ ] Image جدید رو push کردید
- [ ] Deployment رو restart کردید
- [ ] لاگ‌ها رو چک کردید

## اگه باز هم مشکل داشتید:

```bash
# لاگ‌های کامل رو جمع کنید
kubectl logs -l app=api-qcpanel --previous > crash.log
kubectl describe pod -l app=api-qcpanel > pod-describe.log
kubectl get events --sort-by='.lastTimestamp' > events.log
kubectl top pod -l app=api-qcpanel > resources.log

# و این فایل‌ها رو بررسی کنید
```

## نکات مهم:

1. **Exit code 137 = OOM Kill** - همیشه یعنی memory کم بوده
2. **'NoneType' send error** - مشکل async/await بود، fix شد
3. **Startup time** - FastAPI + Database connection می‌تونه تا 30-60 ثانیه طول بکشه
4. **Health checks** - باید زمان کافی برای startup بدید

حالا باید کار کنه! 🚀
