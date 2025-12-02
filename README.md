# QC Panel API

Backend API برای پنل کنترل کیفیت (Quality Control Panel) که با FastAPI ساخته شده است.

## ویژگی‌ها

- 🚀 FastAPI framework برای performance بالا
- 🔐 احراز هویت با JWT
- 🗄️ PostgreSQL database
- 📊 مدیریت کاربران و نقش‌ها
- 💬 مدیریت مکالمات و بررسی‌ها
- 📈 داشبورد و لیدربورد
- 🔄 CORS پیکربندی شده
- 🐳 Docker support کامل

## پیش‌نیازها

- Python 3.11+
- PostgreSQL 15+
- Docker و Docker Compose (برای deployment)

## نصب و راه‌اندازی

### روش 1: اجرا مستقیم با Python

#### 1. کلون کردن پروژه

```bash
git clone <repository-url>
cd api-qc-panel
```

#### 2. ایجاد محیط مجازی

```bash
python -m venv venv
source venv/bin/activate  # در Linux/Mac
# یا
venv\Scripts\activate  # در Windows
```

#### 3. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

#### 4. تنظیم متغیرهای محیطی

فایل `.env.example` را کپی کرده و به `.env` تغییر نام دهید:

```bash
cp .env.example .env
```

سپس فایل `.env` را ویرایش کرده و اطلاعات خود را وارد کنید:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DATABASE=quality_control
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_SCHEMA=call

API_HOST=0.0.0.0
API_PORT=8000

CORS_ORIGINS=http://localhost:3000,http://localhost:5173

JWT_SECRET_KEY=your-very-secret-key-here
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
```

#### 5. اجرای اپلیکیشن

```bash
python main.py
# یا
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

API در آدرس `http://localhost:8000` در دسترس خواهد بود.

### روش 2: اجرا با Docker Compose (توصیه می‌شود)

این روش شامل PostgreSQL و API می‌شود و برای development مناسب است.

#### 1. تنظیم متغیرهای محیطی

فایل `.env` را بسازید (یا از `.env.example` کپی کنید):

```bash
cp .env.example .env
```

#### 2. اجرا با Docker Compose

```bash
docker-compose up -d
```

این دستور دو سرویس را اجرا می‌کند:
- PostgreSQL در پورت 5432
- FastAPI در پورت 8000

#### 3. مشاهده لاگ‌ها

```bash
docker-compose logs -f api
```

#### 4. توقف سرویس‌ها

```bash
docker-compose down
```

### روش 3: Build و Deploy با Docker

برای deploy روی سرور production:

#### 1. Build کردن Image

```bash
docker build -t qc-panel-api:latest .
```

#### 2. اجرای Container

```bash
docker run -d \
  --name qc-panel-api \
  -p 8000:8000 \
  --env-file .env \
  qc-panel-api:latest
```

#### 3. مشاهده لاگ‌ها

```bash
docker logs -f qc-panel-api
```

#### 4. توقف و حذف Container

```bash
docker stop qc-panel-api
docker rm qc-panel-api
```

## API Documentation

پس از اجرای برنامه، مستندات API در آدرس‌های زیر در دسترس است:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Endpoints اصلی

- `GET /` - اطلاعات اولیه API
- `GET /health` - بررسی سلامت سرویس و اتصال به دیتابیس
- `POST /api/auth/login` - ورود کاربر
- `GET /api/users` - دریافت لیست کاربران
- `GET /api/conversations` - دریافت لیست مکالمات
- `GET /api/dashboard/stats` - آمار داشبورد
- `GET /api/leaderboard` - لیدربورد

(برای مشاهده لیست کامل endpoints به `/docs` مراجعه کنید)

## ساختار پروژه

```
api-qc-panel/
├── routes/                 # API routes
│   ├── auth.py            # احراز هویت
│   ├── users.py           # مدیریت کاربران
│   ├── conversations.py   # مکالمات
│   ├── reviews.py         # بررسی‌ها
│   ├── comparison.py      # مقایسه‌ها
│   ├── dashboard.py       # داشبورد
│   ├── leaderboard.py     # لیدربورد
│   ├── agents.py          # مدیریت agents
│   └── settings.py        # تنظیمات
├── migrations/            # Database migrations
├── main.py               # نقطه ورود اپلیکیشن
├── config.py             # تنظیمات و config
├── database.py           # اتصال به دیتابیس
├── utils.py              # توابع کمکی
├── requirements.txt      # وابستگی‌های Python
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Docker Compose config
├── .env.example         # نمونه فایل محیطی
└── README.md           # این فایل
```

## توسعه

### اضافه کردن Migration جدید

```bash
python run_migration.py
```

### اجرای تست‌ها

فایل‌های تست با پیشوند `test-` و `check-` در روت پروژه قرار دارند:

```bash
python test-api-response.py
python test-agent-metrics.py
```

## نکات امنیتی

⚠️ **مهم**: قبل از deploy در production:

1. حتماً `JWT_SECRET_KEY` را به یک کلید قوی و منحصر به فرد تغییر دهید
2. رمز عبور دیتابیس را تغییر دهید
3. `CORS_ORIGINS` را فقط برای دامنه‌های مجاز تنظیم کنید
4. از HTTPS استفاده کنید
5. فایل `.env` را هرگز commit نکنید

## مشکلات رایج

### خطای اتصال به دیتابیس

اطمینان حاصل کنید که:
- PostgreSQL در حال اجرا است
- اطلاعات اتصال در `.env` صحیح است
- دیتابیس `quality_control` و schema `call` وجود دارد

### خطای CORS

اگر فرانت شما نمی‌تواند به API متصل شود:
- آدرس فرانت را به `CORS_ORIGINS` در `.env` اضافه کنید
- مطمئن شوید که پورت‌ها مطابقت دارند

### Container کرش می‌کند یا لاگ ندارد

اگر Docker container بلافاصله متوقف می‌شود:

#### 1. بررسی لاگ‌ها:

```bash
# لاگ‌های container
docker logs qc-panel-api

# لاگ‌های جزئی‌تر
docker logs --tail 100 qc-panel-api

# اگر container متوقف شده
docker ps -a | grep qc-panel
docker logs <container-id>
```

#### 2. اجرای تست دستی:

```bash
# وارد container شوید
docker run -it --rm --env-file .env qc-panel-api:latest /bin/bash

# سپس import ها را تست کنید:
python -c "from routes import auth; print('OK')"
python -c "from config import get_settings; print('OK')"
python -c "from database import get_db_connection; print('OK')"
```

#### 3. استفاده از deploy script:

```bash
chmod +x deploy.sh
./deploy.sh
```

این script به شما کمک می‌کند:
- Build و deploy کنید
- لاگ‌ها را مشاهده کنید
- API را تست کنید
- مشکلات را debug کنید

#### 4. بررسی متغیرهای محیطی:

```bash
# بررسی اینکه متغیرها درست ست شده‌اند
docker exec qc-panel-api env | grep POSTGRES
docker exec qc-panel-api env | grep API
```

#### 5. مشکلات رایج:

**Import Error: No module named 'routes'**
- فایل `routes/__init__.py` خالی نباشد
- در Dockerfile، `COPY routes/ ./routes/` درست انجام شده باشد

**Health check failing**
- health check بعد از 40 ثانیه شروع می‌شود
- اگر API کند راه‌اندازی می‌شود، این زمان را افزایش دهید

**Database connection error**
- اگر از Kubernetes استفاده می‌کنید، مطمئن شوید که DNS resolution درست کار می‌کند
- تست کنید: `docker exec qc-panel-api ping <postgres-host>`
- port forward برای تست: `kubectl port-forward svc/<postgres-service> 5432:5432`

### Debug Mode

برای debugging بیشتر، می‌توانید container را با override کردن entrypoint اجرا کنید:

```bash
# اجرای interactive برای debug
docker run -it --rm \
  --env-file .env \
  -p 8000:8000 \
  qc-panel-api:latest \
  /bin/bash

# سپس دستی uvicorn را اجرا کنید:
uvicorn main:app --host 0.0.0.0 --port 8000 --log-level debug
```

### دریافت کمک

اگر همچنان مشکل دارید:

1. لاگ‌های کامل را جمع‌آوری کنید:
```bash
docker logs qc-panel-api > logs.txt 2>&1
```

2. بررسی کنید که تمام فایل‌های لازم در image هستند:
```bash
docker run --rm qc-panel-api:latest ls -la
docker run --rm qc-panel-api:latest ls -la routes/
```

3. environment variables را بررسی کنید (بدون اطلاعات حساس)

## پشتیبانی

برای گزارش مشکلات یا پیشنهادات، Issue ایجاد کنید.

## لایسنس

[لایسنس پروژه را اینجا ذکر کنید]
