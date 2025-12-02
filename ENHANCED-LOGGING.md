# لاگ‌های جدید اضافه شده - خیلی بیشتر! 🔍

## ✅ لاگ‌های اضافه شده:

### 1. در `main.py`:

#### در Lifespan Startup:
```
LIFESPAN: Starting application startup sequence...
LIFESPAN: Startup complete, application ready!
```
اگه خطا بخوره:
```
LIFESPAN: Startup failed with error: ...
Full traceback: ...
```

#### بعد از Middleware:
```
Request logging middleware registered
```

#### در آخر فایل (مهم!):
```
MODULE LOADED: main.py initialization complete
Application is ready to receive requests
Waiting for Uvicorn to start the server...
Signal handlers registered (SIGTERM, SIGINT)
```

#### اگه signal بیاد:
```
SIGNAL RECEIVED: SIGTERM (signal 15)
Application is terminating...
```

### 2. در `entrypoint.sh`:

#### System Info:
```
System Information:
Python 3.11.x
Working directory: /app
User: appuser
Python path: /usr/local/bin/python3
```

#### Import Tests (با traceback):
```
Testing main application import...
✓ Config OK
✓ Main app OK
```
اگه fail بشه:
```
✗ Main app import failed: ...
Full traceback...
```

#### Uvicorn Start:
```
Starting Uvicorn server...
Command: uvicorn main:app --host 0.0.0.0 --port 8000
Log level: info
```

#### Exit Code:
```
Uvicorn exited with code: 0
```
اگه fail بشه:
```
ERROR: Uvicorn failed to start or crashed
Uvicorn exited with code: 137
```

---

## 🎯 حالا چی میتونی ببینی:

### قبل (لاگ قبلی):
```
✓ All routes registered successfully
[سکوت...]
```

### حالا (لاگ جدید):
```
✓ All routes registered successfully
Request logging middleware registered
==================================================
MODULE LOADED: main.py initialization complete
Application is ready to receive requests
Waiting for Uvicorn to start the server...
==================================================
Signal handlers registered (SIGTERM, SIGINT)
==================================================
Starting Uvicorn server...
Command: uvicorn main:app --host 0.0.0.0 --port 8000
==================================================
==================================================
LIFESPAN: Starting application startup sequence...
==================================================
QC Panel API is starting...
Version: 1.0.0
...
LIFESPAN: Startup complete, application ready!
==================================================
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 🔍 مراحل Debug:

الان وقتی deploy میکنی، دقیقاً میبینی **کدوم مرحله fail میشه**:

### مرحله 1: Import Test
```
Testing Python imports...
✓ FastAPI (fastapi) OK
✓ Uvicorn (uvicorn) OK
✓ PostgreSQL driver (psycopg2) OK
✓ Pydantic (pydantic) OK
Testing main application import...
✓ Config OK
✓ Main app OK
✓ All imports successful!
```
**اگه اینجا fail بشه** → مشکل import یا dependency

### مرحله 2: Module Load
```
MODULE LOADED: main.py initialization complete
Signal handlers registered
```
**اگه اینجا fail بشه** → مشکل در کد Python

### مرحله 3: Uvicorn Start
```
Starting Uvicorn server...
Command: uvicorn main:app --host 0.0.0.0 --port 8000
```
**اگه اینجا fail بشه** → مشکل Uvicorn

### مرحله 4: Lifespan Startup
```
LIFESPAN: Starting application startup sequence...
LIFESPAN: Startup complete, application ready!
```
**اگه اینجا fail بشه** → مشکل در lifespan event

### مرحله 5: Uvicorn Ready
```
INFO:     Started server process [1]
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```
**اگه اینجا fail بشه** → مشکل در binding port یا...

### مرحله 6: اگه Kill بشه
```
SIGNAL RECEIVED: SIGTERM (signal 15)
Application is terminating...
Uvicorn exited with code: 137
```
**این یعنی** → OOM یا Kubernetes kill کرده

---

## 📋 دستورات Deploy:

```bash
cd C:\Users\mfakhriyan\Desktop\api-qc-panel

# 1. Build
docker build -f Dockerfile.minimal -t qc-panel-api:debug-v2 .

# 2. Test local
docker run --rm -p 8000:8000 -e LOG_LEVEL=DEBUG qc-panel-api:debug-v2

# اگه local کار کرد:

# 3. Tag
docker tag qc-panel-api:debug-v2 YOUR_REGISTRY/qc-panel-api:debug-v2

# 4. Push
docker push YOUR_REGISTRY/qc-panel-api:debug-v2

# 5. Deploy
kubectl set image deployment/api-qcpanel \
  api-qcpanel=YOUR_REGISTRY/qc-panel-api:debug-v2

# 6. Set DEBUG
kubectl set env deployment/api-qcpanel LOG_LEVEL=DEBUG

# 7. Delete pods
kubectl delete pods -l app=api-qcpanel

# 8. چک کن
kubectl logs -f -l app=api-qcpanel
```

---

## 🎯 چیزهایی که باید ببینی:

1. ✅ Import test pass میشه
2. ✅ Module loaded message
3. ✅ Signal handlers registered
4. ✅ Starting Uvicorn server...
5. ✅ LIFESPAN: Starting application...
6. ✅ LIFESPAN: Startup complete!
7. ✅ Uvicorn running on http://...

**اگه یکی از اینا نیومد → اونجا مشکل هست!**

---

## 📊 مثال خروجی کامل:

```log
==========================================
QC Panel API - Starting (Enhanced Logging)
==========================================
API_HOST: 0.0.0.0
API_PORT: 8000
POSTGRES_HOST: prod-crm-psql...
LOG_LEVEL: DEBUG
==========================================
System Information:
Python 3.11.6
Working directory: /app
User: appuser
Python path: /usr/local/bin/python3
==========================================
Testing Python imports...
Python version: 3.11.6
✓ FastAPI (fastapi) OK
✓ Uvicorn (uvicorn) OK
✓ PostgreSQL driver (psycopg2) OK
✓ Pydantic (pydantic) OK
Testing main application import...
2025-12-02 09:00:00 - __main__ - INFO - Logging configured with level: DEBUG
2025-12-02 09:00:00 - __main__ - INFO - Loading application settings...
2025-12-02 09:00:00 - __main__ - INFO - Creating FastAPI application...
2025-12-02 09:00:00 - __main__ - INFO - Registering API routes...
2025-12-02 09:00:00 - __main__ - INFO - All routes registered successfully
2025-12-02 09:00:00 - __main__ - INFO - Request logging middleware registered
2025-12-02 09:00:00 - __main__ - INFO - ==================================================
2025-12-02 09:00:00 - __main__ - INFO - MODULE LOADED: main.py initialization complete
2025-12-02 09:00:00 - __main__ - INFO - ==================================================
2025-12-02 09:00:00 - __main__ - INFO - Signal handlers registered (SIGTERM, SIGINT)
✓ Config OK
✓ Main app OK
✓ All imports successful!
==========================================
Starting Uvicorn server...
Command: uvicorn main:app --host 0.0.0.0 --port 8000
==========================================
2025-12-02 09:00:01 - __main__ - INFO - LIFESPAN: Starting application startup sequence...
2025-12-02 09:00:01 - __main__ - INFO - QC Panel API is starting...
2025-12-02 09:00:01 - __main__ - INFO - LIFESPAN: Startup complete, application ready!
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

---

## ⚠️ اگه این لاگ‌ها رو ندیدی:

### فقط تا "All routes registered" میاد:
→ مشکل در آخر main.py یا entrypoint

### "Module loaded" میاد ولی "Starting Uvicorn" نمیاد:
→ entrypoint.sh اجرا نمیشه یا break میخوره

### "Starting Uvicorn" میاد ولی "LIFESPAN" نمیاد:
→ Uvicorn start میشه ولی app load نمیشه

### همه میاد ولی بعد kill میشه:
→ OOM یا signal kill

---

**حالا deploy کن و تمام لاگ رو بهم بفرست!** 📊

با این همه لاگ، 100% میفهمیم کجا مشکل داره! 🎯
