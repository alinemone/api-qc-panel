# 🏠 اجرای Local برای تست

## 3 روش برای اجرا:

---

## ✅ روش 1: با Script (ساده‌ترین) - توصیه می‌شود

### در Windows:
```cmd
run-local.bat
```

### در Linux/Mac:
```bash
chmod +x run-local.sh
./run-local.sh
```

این script خودکار:
- Virtual environment می‌سازه
- وابستگی‌ها رو نصب میکنه
- API رو اجرا میکنه روی `http://localhost:8000`

**بعد از اجرا تست کن:**
- مرورگر باز کن: http://localhost:8000
- مستندات: http://localhost:8000/docs
- Health check: http://localhost:8000/health

---

## ✅ روش 2: با Docker (بدون database)

اگه فقط میخوای ببینی API کار میکنه:

```bash
# Build
docker build -f Dockerfile.minimal -t qc-panel-api:test .

# اجرا (بدون database واقعی)
docker run -d \
  --name qc-panel-test \
  -p 8000:8000 \
  -e POSTGRES_HOST=fake \
  -e POSTGRES_DATABASE=fake \
  -e POSTGRES_USER=fake \
  -e POSTGRES_PASSWORD=fake \
  qc-panel-api:test

# لاگ ببین
docker logs -f qc-panel-test
```

**تست کن:**
```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

**توقف:**
```bash
docker stop qc-panel-test
docker rm qc-panel-test
```

---

## ✅ روش 3: با Docker Compose (با PostgreSQL)

اگه میخوای با database هم تست کنی:

```bash
# اجرا (API + PostgreSQL)
docker-compose up -d

# لاگ ببین
docker-compose logs -f api

# توقف
docker-compose down
```

**تست کن:**
```bash
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

---

## 🔍 تست‌های مهم:

### 1. چک کن API بالا اومده:
```bash
curl http://localhost:8000/
```
**باید ببینی:**
```json
{
  "message": "QC Panel API",
  "version": "1.0.0",
  "status": "running"
}
```

### 2. چک کن Health endpoint کار میکنه:
```bash
curl http://localhost:8000/health
```
**باید ببینی:**
```json
{
  "status": "healthy",
  "service": "qc-panel-api",
  "version": "1.0.0"
}
```

### 3. چک کن مستندات کار میکنه:
مرورگر باز کن: http://localhost:8000/docs

باید Swagger UI رو ببینی با لیست endpoint ها.

---

## ❌ مشکلات احتمالی:

### مشکل 1: Port 8000 قبلاً استفاده شده

```bash
# در Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# در Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### مشکل 2: Python نصب نیست

- Windows: https://www.python.org/downloads/
- Linux: `sudo apt install python3 python3-venv`
- Mac: `brew install python3`

### مشکل 3: Docker نصب نیست

- Windows/Mac: https://www.docker.com/products/docker-desktop
- Linux: `sudo apt install docker.io docker-compose`

### مشکل 4: Permission denied

```bash
# Linux/Mac
chmod +x run-local.sh
# یا
sudo chmod +x run-local.sh
```

---

## 📊 مقایسه روش‌ها:

| روش | مزیت | معایب |
|-----|------|-------|
| Script | خیلی سریع، بدون Docker | نیاز به Python روی سیستم |
| Docker (بدون DB) | مثل production | نمیشه endpoint های database رو تست کرد |
| Docker Compose | کامل با DB | کمی کندتر برای اجرا |

---

## 🎯 توصیه:

1. **اول Script رو امتحان کن** - سریع‌ترین راه
2. **اگه کار کرد** - یعنی کد مشکل نداره
3. **بعد Docker رو تست کن** - یعنی Docker image هم مشکل نداره
4. **در آخر به production deploy کن** - با اطمینان!

---

## 🐛 Debug:

اگه خطا گرفتی:

### در حالت Script:
```bash
# لاگ با جزئیات
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload --log-level debug
```

### در حالت Docker:
```bash
# ببین چه خطایی میده
docker logs qc-panel-test

# برو تو container
docker exec -it qc-panel-test /bin/bash

# داخل container تست کن
curl http://localhost:8000/
python3 -c "from main import app; print('OK')"
```

---

## ✅ بعد از تست موفق:

وقتی روی local کار کرد:
1. ✅ کد درسته
2. ✅ Dependencies درسته
3. ✅ Dockerfile درسته

حالا میتونی با اطمینان deploy کنی روی Kubernetes!

---

## 🆘 کمک سریع:

```bash
# همه چیز رو پاک کن و از اول شروع کن
docker-compose down -v
docker rm -f qc-panel-test 2>/dev/null
rm -rf venv
./run-local.sh
```

موفق باشی! 🚀
