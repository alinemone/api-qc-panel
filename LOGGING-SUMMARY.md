# خلاصه تغییرات - Logging اضافه شد ✅

## چی اضافه شد:

### 1. Logging کامل در `main.py`:
- ✅ Log در startup/shutdown
- ✅ Log برای هر request (method, path, status, duration)
- ✅ Log برای registration routers
- ✅ Log برای CORS configuration
- ✅ Log برای database connection attempts
- ✅ Error logging برای failed requests

### 2. Logging کامل در `database.py`:
- ✅ Log برای database connection attempts
- ✅ Log برای successful connections
- ✅ Log برای failed connections با error details
- ✅ Log برای query execution
- ✅ Log برای transaction commit/rollback
- ✅ Log برای procedure calls

### 3. سطح Log قابل تنظیم:
- ✅ از environment variable: `LOG_LEVEL`
- ✅ مقادیر: DEBUG, INFO, WARNING, ERROR, CRITICAL
- ✅ پیشفرض: INFO

### 4. راهنمای کامل:
- ✅ `LOGGING-GUIDE.md` - راهنمای استفاده

---

## مثال خروجی Log:

### با LOG_LEVEL=INFO (عادی):

```
2024-12-02 10:30:15,123 - main - INFO - Logging configured with level: INFO
2024-12-02 10:30:15,125 - main - INFO - Loading application settings...
2024-12-02 10:30:15,127 - main - INFO - Settings loaded - API will run on 0.0.0.0:8000
2024-12-02 10:30:15,128 - main - INFO - Creating FastAPI application...
2024-12-02 10:30:15,130 - main - INFO - FastAPI application created
2024-12-02 10:30:15,131 - main - INFO - Configuring CORS middleware...
2024-12-02 10:30:15,132 - main - INFO - CORS configured for origins: ['http://localhost:3000', ...]
2024-12-02 10:30:15,133 - main - INFO - Registering API routes...
2024-12-02 10:30:15,134 - main - INFO -   - Auth routes registered
2024-12-02 10:30:15,135 - main - INFO -   - Users routes registered
...
2024-12-02 10:30:16,200 - main - INFO - ==================================================
2024-12-02 10:30:16,201 - main - INFO - QC Panel API is starting...
2024-12-02 10:30:16,202 - main - INFO - Version: 1.0.0
2024-12-02 10:30:16,203 - main - INFO - Host: 0.0.0.0:8000
2024-12-02 10:30:16,204 - main - INFO - CORS Origins: ['http://localhost:3000', ...]
2024-12-02 10:30:16,205 - main - INFO - Database Host: postgres
2024-12-02 10:30:16,206 - main - INFO - Database: quality_control
2024-12-02 10:30:16,207 - main - INFO - Schema: call
2024-12-02 10:30:16,208 - main - INFO - ==================================================
```

### وقتی request میاد:

```
2024-12-02 10:31:00,100 - main - INFO - Incoming request: GET /health
2024-12-02 10:31:00,105 - main - INFO - Request completed: GET /health Status: 200 Duration: 0.005s
```

### وقتی database connect میشه:

```
2024-12-02 10:31:10,200 - main - INFO - Detailed health check started
2024-12-02 10:31:10,201 - database - DEBUG - Attempting to connect to database: postgres:5432/quality_control
2024-12-02 10:31:10,350 - database - INFO - Database connection established: postgres/quality_control
2024-12-02 10:31:10,351 - main - INFO - Database connection successful
```

### وقتی database fail میشه:

```
2024-12-02 10:31:20,100 - main - INFO - Detailed health check started
2024-12-02 10:31:20,101 - database - DEBUG - Attempting to connect to database: wrong-host:5432/quality_control
2024-12-02 10:31:25,200 - database - ERROR - Database connection failed (OperationalError): could not translate host name "wrong-host" to address: Name or service not known
2024-12-02 10:31:25,201 - main - ERROR - Database connection failed: could not translate host name "wrong-host" to address: Name or service not known
```

### وقتی query اجرا میشه (با DEBUG):

```
2024-12-02 10:32:00,100 - database - DEBUG - Getting database connection from context manager
2024-12-02 10:32:00,101 - database - DEBUG - Attempting to connect to database: postgres:5432/quality_control
2024-12-02 10:32:00,250 - database - INFO - Database connection established: postgres/quality_control
2024-12-02 10:32:00,251 - database - DEBUG - Executing query: SELECT * FROM users WHERE username = %s... with params: ('admin',)
2024-12-02 10:32:00,300 - database - DEBUG - Query returned 1 row: True
2024-12-02 10:32:00,301 - database - DEBUG - Database transaction committed
2024-12-02 10:32:00,302 - database - DEBUG - Database connection closed
```

---

## چطور استفاده کنی:

### Local با DEBUG:

```bash
# روی Windows
set LOG_LEVEL=DEBUG
run-local.bat

# روی Linux/Mac
export LOG_LEVEL=DEBUG
./run-local.sh

# یا
LOG_LEVEL=DEBUG python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker با DEBUG:

```bash
docker run -d \
  --name qc-test \
  -p 8000:8000 \
  -e LOG_LEVEL=DEBUG \
  qc-panel-api:latest

# ببین لاگ
docker logs -f qc-test
```

### Kubernetes با DEBUG:

```bash
# تنظیم LOG_LEVEL در ConfigMap
kubectl edit configmap api-qcpanel-config
# اضافه کن: LOG_LEVEL: "DEBUG"

# یا مستقیم
kubectl set env deployment/api-qcpanel LOG_LEVEL=DEBUG

# Restart کن
kubectl rollout restart deployment/api-qcpanel

# ببین لاگ
kubectl logs -f -l app=api-qcpanel
```

---

## Troubleshooting با Log:

### مشکل: Pod Start نمیشه

```bash
kubectl logs POD_NAME | head -50
```

میبینی:
- کدوم قسمت از startup fail شده
- Database connect شده یا نه
- Router ها register شدن یا نه

### مشکل: Request ها fail میشن

```bash
kubectl logs POD_NAME | grep "Request failed"
```

میبینی:
- کدوم endpoint fail شده
- چه error ای گرفته
- چقدر طول کشیده

### مشکل: Database connect نمیشه

```bash
kubectl logs POD_NAME | grep -i database
```

میبینی:
- Host درسته یا نه
- Timeout خورده یا نه
- Error دقیق چیه

### مشکل: Performance کنده

```bash
kubectl logs POD_NAME | grep Duration
```

میبینی کدوم request ها چقدر طول میکشن.

---

## Deploy جدید:

حالا که logging اضافه شده:

```bash
cd /path/to/api-qc-panel

# 1. Build image جدید
docker build -f Dockerfile.minimal -t qc-panel-api:v-with-logging .

# 2. Tag
docker tag qc-panel-api:v-with-logging YOUR_REGISTRY/qc-panel-api:v-with-logging

# 3. Push
docker push YOUR_REGISTRY/qc-panel-api:v-with-logging

# 4. Update deployment
kubectl set image deployment/api-qcpanel \
  api-qcpanel=YOUR_REGISTRY/qc-panel-api:v-with-logging

# 5. Set LOG_LEVEL (اگه میخوای DEBUG)
kubectl set env deployment/api-qcpanel LOG_LEVEL=DEBUG

# 6. Delete old pods
kubectl delete pods -l app=api-qcpanel

# 7. ببین لاگ جدید
kubectl logs -f -l app=api-qcpanel
```

---

## مزایا:

1. ✅ **میبینی دقیقاً چه اتفاقی میفته** - از startup تا shutdown
2. ✅ **میبینی کجا خطا میده** - با line number و error message
3. ✅ **میبینی performance چطوره** - هر request چقدر طول میکشه
4. ✅ **میبینی database چی میگه** - connection success/fail
5. ✅ **قابل تنظیمه** - DEBUG برای dev، INFO برای prod
6. ✅ **امنه** - Password در لاگ نیست

---

## نکات مهم:

1. **در Production**: `LOG_LEVEL=INFO` استفاده کن (کمتر لاگ)
2. **برای Debug**: `LOG_LEVEL=DEBUG` استفاده کن (همه چیز)
3. **لاگ رو Save کن**: `kubectl logs POD > logs.txt`
4. **Password safe هست**: در لاگ نمیاد

---

## آماده برای Deploy! 🚀

حالا:
- ✅ کد با logging کامل
- ✅ میتونی ببینی کجا خطا میده
- ✅ میتونی performance رو track کنی
- ✅ میتونی database issues رو debug کنی

**بالا ببرش و لاگ‌ها رو بهم بفرست!** 📊
