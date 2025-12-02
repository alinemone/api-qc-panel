# راهنمای Logging

## سطوح Log:

سطح logging رو میتونی با environment variable تنظیم کنی:

```bash
# مقادیر ممکن: DEBUG, INFO, WARNING, ERROR, CRITICAL
export LOG_LEVEL=DEBUG

# یا در .env
LOG_LEVEL=DEBUG
```

## سطوح مختلف:

### DEBUG (خیلی جزئی)
همه چیز رو log میکنه:
- Database connection attempts
- Query execution
- Request/response details
- Function calls

```bash
LOG_LEVEL=DEBUG
```

خروجی نمونه:
```
2024-12-02 10:30:15 - main - DEBUG - Root endpoint called
2024-12-02 10:30:16 - database - DEBUG - Attempting to connect to database: postgres:5432/quality_control
2024-12-02 10:30:16 - database - INFO - Database connection established: postgres/quality_control
2024-12-02 10:30:16 - database - DEBUG - Executing query: SELECT * FROM users...
```

### INFO (عادی) - پیشفرض
اطلاعات مهم:
- Startup messages
- Route registration
- Database connections
- Request completion

```bash
LOG_LEVEL=INFO
```

خروجی نمونه:
```
2024-12-02 10:30:15 - main - INFO - Loading application settings...
2024-12-02 10:30:15 - main - INFO - Settings loaded - API will run on 0.0.0.0:8000
2024-12-02 10:30:15 - main - INFO - Creating FastAPI application...
2024-12-02 10:30:15 - main - INFO - Registering API routes...
```

### WARNING (هشدار)
فقط مشکلات:
- Database rollbacks
- Connection issues
- Deprecated features

```bash
LOG_LEVEL=WARNING
```

### ERROR (خطا)
فقط خطاها:
- Database errors
- Failed requests
- Exceptions

```bash
LOG_LEVEL=ERROR
```

خروجی نمونه:
```
2024-12-02 10:30:16 - database - ERROR - Database connection failed: could not connect to server
2024-12-02 10:30:16 - main - ERROR - Request failed: POST /api/auth/login Error: Database unavailable
```

---

## استفاده در Kubernetes:

### با ConfigMap:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: api-qcpanel-config
data:
  LOG_LEVEL: "INFO"  # یا DEBUG برای troubleshooting
```

### با Deployment:

```yaml
spec:
  containers:
  - name: api
    env:
    - name: LOG_LEVEL
      value: "DEBUG"  # برای debugging
```

---

## دیدن لاگ‌ها:

### Local:
```bash
# با script
./run-local.sh

# با docker
docker logs -f qc-panel-test

# با docker-compose
docker-compose logs -f api
```

### Kubernetes:
```bash
# لاگ‌های زنده
kubectl logs -f -l app=api-qcpanel

# لاگ‌های چند pod
kubectl logs -f -l app=api-qcpanel --all-containers=true

# لاگ از timestamp مشخص
kubectl logs --since=10m -l app=api-qcpanel

# لاگ با grep
kubectl logs -l app=api-qcpanel | grep ERROR
```

---

## لاگ‌های مهم برای Debug:

### Startup Issues:
```bash
kubectl logs POD_NAME | grep -A 20 "Loading application settings"
```

### Database Issues:
```bash
kubectl logs POD_NAME | grep -i "database"
```

### Request Issues:
```bash
kubectl logs POD_NAME | grep -i "request failed"
```

### All Errors:
```bash
kubectl logs POD_NAME | grep ERROR
```

---

## فرمت Log:

```
%(asctime)s - %(name)s - %(levelname)s - %(message)s

2024-12-02 10:30:15 - main - INFO - QC Panel API is starting...
│                     │      │      │
│                     │      │      └─ پیام
│                     │      └─ سطح (INFO/ERROR/DEBUG)
│                     └─ ماژول (main/database)
└─ زمان
```

---

## مثال‌های کاربردی:

### شروع API با DEBUG mode:
```bash
LOG_LEVEL=DEBUG python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Deploy با DEBUG در Kubernetes:
```bash
kubectl set env deployment/api-qcpanel LOG_LEVEL=DEBUG
kubectl rollout restart deployment/api-qcpanel
kubectl logs -f -l app=api-qcpanel
```

### فیلتر کردن لاگ‌ها:
```bash
# فقط ERROR ها
kubectl logs -l app=api-qcpanel | grep ERROR

# فقط database
kubectl logs -l app=api-qcpanel | grep database

# فقط request ها
kubectl logs -l app=api-qcpanel | grep "Incoming request"

# آخرین 50 خط
kubectl logs -l app=api-qcpanel --tail=50
```

---

## نکات مهم:

1. **در Production از INFO استفاده کن** - DEBUG خیلی لاگ میزنه
2. **برای Debug از DEBUG استفاده کن** - میبینی دقیقاً چه اتفاقی میفته
3. **لاگ‌ها رو save کن** - برای بررسی بعدی:
   ```bash
   kubectl logs POD_NAME > logs.txt
   ```
4. **Password در لاگ نیست** - من مراقب امنیت بودم!

---

## Troubleshooting:

### هیچ لاگی نمیبینی؟

```bash
# چک کن pod اصلاً بالا اومده
kubectl get pods -l app=api-qcpanel

# چک کن container در حال اجراست
kubectl describe pod POD_NAME

# چک کن log level
kubectl exec POD_NAME -- env | grep LOG_LEVEL
```

### خیلی کم لاگ میبینی?

```bash
# Log level رو DEBUG کن
kubectl set env deployment/api-qcpanel LOG_LEVEL=DEBUG
kubectl rollout restart deployment/api-qcpanel
```

### خیلی زیاد لاگ میبینی؟

```bash
# Log level رو INFO کن (default)
kubectl set env deployment/api-qcpanel LOG_LEVEL=INFO
kubectl rollout restart deployment/api-qcpanel
```
