# راهنمای حل مشکل Container Crash

اگر container شما کرش می‌کنه و دائم restart میشه، این مراحل رو دنبال کنید:

## مرحله 1: دیدن لاگ‌های واقعی

```bash
# لاگ‌های container در حال اجرا
docker logs qc-panel-api

# لاگ‌های container متوقف شده
docker ps -a
docker logs <container-id>

# دنبال کردن لاگ‌ها به صورت real-time
docker logs -f qc-panel-api

# 100 خط آخر لاگ
docker logs --tail 100 qc-panel-api
```

## مرحله 2: تست با Dockerfile ساده

اگر container دائم کرش میکنه، از `Dockerfile.simple` استفاده کنید:

```bash
# Build با Dockerfile ساده
docker build -f Dockerfile.simple -t qc-panel-api:simple .

# اجرا
docker run -d \
  --name qc-panel-api \
  -p 8000:8000 \
  --env-file .env \
  qc-panel-api:simple

# چک کردن لاگ
docker logs -f qc-panel-api
```

این نسخه ساده‌تر است و مشکلات entrypoint script را ندارد.

## مرحله 3: Debug دستی

```bash
# وارد container شوید (interactive mode)
docker run -it --rm \
  --env-file .env \
  -p 8000:8000 \
  qc-panel-api:latest \
  /bin/bash

# حالا داخل container هستید. تست کنید:

# 1. چک کنید فایل‌ها وجود دارند
ls -la
ls -la routes/

# 2. Python imports را تست کنید
python3 -c "from config import get_settings; print('Config OK')"
python3 -c "from main import app; print('Main OK')"
python3 -c "from routes import auth; print('Routes OK')"

# 3. دستی uvicorn را اجرا کنید
uvicorn main:app --host 0.0.0.0 --port 8000 --log-level debug
```

## مرحله 4: بررسی متغیرهای محیطی

```bash
# بررسی environment variables
docker exec qc-panel-api env

# بررسی database config
docker exec qc-panel-api env | grep POSTGRES

# تست اتصال به database
docker exec qc-panel-api python3 -c "
from database import get_db_connection
try:
    conn = get_db_connection()
    print('Database connection OK')
    conn.close()
except Exception as e:
    print(f'Database error: {e}')
"
```

## مرحله 5: مشکلات رایج و حل‌ها

### مشکل 1: ModuleNotFoundError: No module named 'routes'

**علت**: فایل‌های routes کپی نشده یا `__init__.py` مشکل دارد

**حل**:
```bash
# چک کنید routes در image هست
docker run --rm qc-panel-api:latest ls -la routes/

# چک کنید __init__.py پر است
docker run --rm qc-panel-api:latest cat routes/__init__.py
```

### مشکل 2: Database connection error

**علت**: نمی‌تواند به PostgreSQL وصل شود

**حل**:
```bash
# تست اتصال به database host
docker run --rm --env-file .env qc-panel-api:latest ping -c 3 $POSTGRES_HOST

# اگر از Kubernetes استفاده می‌کنید
kubectl port-forward svc/your-postgres-service 5432:5432
# سپس در .env تنظیم کنید: POSTGRES_HOST=localhost
```

### مشکل 3: Permission denied for entrypoint.sh

**علت**: Line endings یا permission مشکل دارد

**حل 1** - استفاده از Dockerfile.simple (توصیه می‌شود):
```bash
docker build -f Dockerfile.simple -t qc-panel-api:latest .
```

**حل 2** - Fix کردن line endings:
```bash
# در ویندوز
dos2unix entrypoint.sh

# یا
sed -i 's/\r$//' entrypoint.sh

# سپس rebuild
docker build -t qc-panel-api:latest .
```

### مشکل 4: Health check failing

**علت**: API کند راه‌اندازی می‌شود یا به خطا می‌خورد

**حل**:
```bash
# Health check را disable کنید برای test
docker run -d \
  --name qc-panel-api \
  --no-healthcheck \
  -p 8000:8000 \
  --env-file .env \
  qc-panel-api:latest

# بعد از اینکه مطمئن شدید کار می‌کند، health check را enable کنید
```

### مشکل 5: Import errors یا Python errors

**علت**: وابستگی‌ها نصب نشده یا مشکل در کد

**حل**:
```bash
# بررسی وابستگی‌ها
docker run --rm qc-panel-api:latest pip list

# تست import به صورت جداگانه
docker run --rm qc-panel-api:latest python3 -c "
import sys
print('Python:', sys.version)
import fastapi
import uvicorn
import psycopg2
import pydantic
print('All imports OK')
"
```

## مرحله 6: اگر همچنان کار نکرد

### Build کامل از نو:

```bash
# پاک کردن همه چیز
docker stop qc-panel-api 2>/dev/null || true
docker rm qc-panel-api 2>/dev/null || true
docker rmi qc-panel-api:latest 2>/dev/null || true

# Build با no-cache
docker build --no-cache -f Dockerfile.simple -t qc-panel-api:latest .

# اجرا با لاگ جزئی
docker run -d \
  --name qc-panel-api \
  -p 8000:8000 \
  --env-file .env \
  qc-panel-api:latest

# مشاهده لاگ
docker logs -f qc-panel-api
```

### Test سریع بدون Docker:

```bash
# اگر Python و PostgreSQL محلی دارید
python3 -m venv venv
source venv/bin/activate  # در Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 main.py
```

## نکات مهم

1. **همیشه لاگ‌ها را ببینید** - بدون لاگ نمی‌شود مشکل را پیدا کرد
2. **از Dockerfile.simple استفاده کنید** - ساده‌تر و مطمئن‌تر است
3. **Environment variables را چک کنید** - خیلی از مشکلات از اینجا میاد
4. **Database connectivity را تست کنید** - اگه DB در دسترس نیست، API کار نمی‌کنه

## دریافت کمک

اگر همچنان مشکل دارید، لاگ‌های زیر را جمع‌آوری کنید:

```bash
# 1. لاگ container
docker logs qc-panel-api > container.log 2>&1

# 2. لیست فایل‌ها در image
docker run --rm qc-panel-api:latest find /app -type f > files.log

# 3. Environment variables (بدون password!)
docker run --rm qc-panel-api:latest env | grep -v PASSWORD > env.log

# 4. Python version و packages
docker run --rm qc-panel-api:latest pip list > packages.log
```

و این فایل‌ها را همراه با شرح مشکل ارسال کنید.
