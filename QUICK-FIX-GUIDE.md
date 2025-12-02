# 🚨 راهنمای فوری حل مشکل - OOM و Async Error

## مشکل شما:
```
Exit code 137 → Out of Memory
'NoneType' object has no attribute 'send' → Async error
```

**دلیل**: شما هنوز از image قدیمی استفاده می‌کنید که این مشکلات رو داره!

---

## ✅ راه‌حل قطعی (گام به گام):

### گام 1️⃣: آپلود فایل‌های جدید به سرور

فایل‌های زیر رو که من fix کردم، به سرور انتقال بده:

```bash
# روی کامپیوتر محلی خودت
scp main.py your-server:/path/to/api-qc-panel/
scp Dockerfile.simple your-server:/path/to/api-qc-panel/
scp quick-fix.sh your-server:/path/to/api-qc-panel/

# یا همه فایل‌ها رو یکجا
scp -r * your-server:/path/to/api-qc-panel/
```

**یا اگه Git استفاده می‌کنی:**
```bash
# روی کامپیوتر محلی
git add .
git commit -m "Fix OOM and async issues"
git push

# روی سرور
cd /path/to/api-qc-panel
git pull
```

### گام 2️⃣: Build کردن Image جدید

```bash
# روی سرور یا جایی که Docker داری
cd /path/to/api-qc-panel

# Build با Dockerfile.simple
docker build -f Dockerfile.simple -t qc-panel-api:fixed .
```

### گام 3️⃣: Tag و Push به Registry

```bash
# Tag کن
docker tag qc-panel-api:fixed YOUR_REGISTRY/qc-panel-api:fixed

# Login به registry (اگه نکردی)
docker login YOUR_REGISTRY

# Push کن
docker push YOUR_REGISTRY/qc-panel-api:fixed
```

**مثال واقعی:**
```bash
# مثلاً اگه registry شما harbor.example.com هست
docker tag qc-panel-api:fixed harbor.example.com/myproject/qc-panel-api:fixed
docker push harbor.example.com/myproject/qc-panel-api:fixed
```

### گام 4️⃣: Update کردن Kubernetes Deployment

```bash
# Update image
kubectl set image deployment/api-qcpanel \
  api-qcpanel=YOUR_REGISTRY/qc-panel-api:fixed

# Update memory limit به 512Mi
kubectl patch deployment api-qcpanel --type='json' -p='[
  {
    "op": "replace",
    "path": "/spec/template/spec/containers/0/resources/limits/memory",
    "value": "512Mi"
  }
]'

# Update startup probe
kubectl patch deployment api-qcpanel --type='json' -p='[
  {
    "op": "replace",
    "path": "/spec/template/spec/containers/0/startupProbe/failureThreshold",
    "value": 30
  }
]'
```

### گام 5️⃣: Delete کردن Pod های قدیمی

```bash
# حذف pod های قدیمی تا pod های جدید با image جدید ساخته بشن
kubectl delete pods -l app=api-qcpanel

# صبر کن تا جدیدا بیان بالا
kubectl get pods -l app=api-qcpanel -w
```

### گام 6️⃣: چک کردن لاگ‌ها

```bash
# لاگ‌های زنده
kubectl logs -f -l app=api-qcpanel

# باید این پیام‌ها رو ببینی:
# ✓ FastAPI OK
# ✓ Uvicorn OK
# ✓ Config OK
# ✓ Main app OK
# Starting Uvicorn server...
```

---

## 🎯 راه سریع‌تر: استفاده از Script

من یه script آماده کردم که همه کارا رو خودکار انجام میده:

```bash
# روی سرور
cd /path/to/api-qc-panel
chmod +x quick-fix.sh
./quick-fix.sh
```

Script می‌پرسه:
1. Registry address چیه؟
2. Namespace چیه؟

و بعد خودش همه چیز رو انجام میده!

---

## 🔍 بررسی که مشکل حل شده:

### 1. چک کردن Pod ها:
```bash
kubectl get pods -l app=api-qcpanel

# باید ببینی:
# NAME                          READY   STATUS    RESTARTS
# api-qcpanel-xxxxx-yyyyy       1/1     Running   0
```

### 2. چک کردن Memory:
```bash
kubectl top pods -l app=api-qcpanel

# باید memory زیر 512Mi باشه
```

### 3. چک کردن لاگ:
```bash
kubectl logs -l app=api-qcpanel --tail=50

# نباید error ببینی
# باید "Starting Uvicorn server..." ببینی
```

### 4. تست API:
```bash
# Port forward کن
kubectl port-forward svc/api-qcpanel 8000:8000

# در terminal دیگه test کن
curl http://localhost:8000/
curl http://localhost:8000/health
```

---

## ❌ اگه هنوز کار نکرد:

### چک کن که image واقعاً update شده:

```bash
# ببین deployment از چه image ای استفاده میکنه
kubectl describe deployment api-qcpanel | grep Image

# باید image جدیدت رو ببینی
```

### چک کن که pod از image جدید استفاده میکنه:

```bash
kubectl describe pod -l app=api-qcpanel | grep Image

# باید همون image جدید باشه
```

### اگه از image قدیمی استفاده میکنه:

```bash
# Pod های قدیمی رو force delete کن
kubectl delete pods -l app=api-qcpanel --force --grace-period=0

# Deployment رو restart کن
kubectl rollout restart deployment/api-qcpanel
```

---

## 📝 چک‌لیست:

- [ ] فایل `main.py` جدید رو روی سرور آپلود کردی
- [ ] فایل `Dockerfile.simple` جدید رو روی سرور آپلود کردی
- [ ] Image جدید رو build کردی
- [ ] Image رو به registry push کردی
- [ ] Deployment رو update کردی با image جدید
- [ ] Memory limit رو به 512Mi افزایش دادی
- [ ] Pod های قدیمی رو delete کردی
- [ ] Pod های جدید running هستن (با `kubectl get pods`)
- [ ] لاگ‌ها error نداره (با `kubectl logs`)
- [ ] API جواب میده (با `curl` یا port-forward)

---

## 🆘 کمک فوری:

اگه گیر کردی، این دستورات رو اجرا کن و خروجی رو بهم بده:

```bash
# 1. وضعیت deployment
kubectl describe deployment api-qcpanel > deployment.txt

# 2. وضعیت pod
kubectl describe pod -l app=api-qcpanel > pods.txt

# 3. لاگ pod فعلی
kubectl logs -l app=api-qcpanel --tail=100 > current-logs.txt

# 4. لاگ pod قبلی
kubectl logs -l app=api-qcpanel --previous --tail=100 > previous-logs.txt 2>&1

# 5. Events
kubectl get events --sort-by='.lastTimestamp' | grep api-qcpanel > events.txt
```

و این 5 فایل رو بهم بفرست.

---

## 💡 نکات مهم:

1. **حتماً از image جدید استفاده کن** - image قدیمی این bug ها رو داره
2. **حتماً memory رو به 512Mi برسون** - وگرنه OOM میشه
3. **Pod های قدیمی رو حذف کن** - تا pod های جدید با image جدید ساخته بشن
4. **صبور باش** - startup تا 1-2 دقیقه طول می‌کشه

موفق باشی! 🚀
