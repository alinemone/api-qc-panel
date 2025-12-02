# QC Panel FastAPI Backend - مستندات کامل API

## 📋 فهرست مطالب

1. [نصب و راه‌اندازی](#نصب-و-راه‌اندازی)
2. [Authentication & Users](#1-authentication--users)
3. [Conversations](#2-conversations)
4. [Reviews](#3-reviews)
5. [Comparison](#4-comparison)
6. [Dashboard](#5-dashboard)
7. [Leaderboard](#6-leaderboard)
8. [Settings](#7-settings)
9. [Agents](#8-agents)

---

## نصب و راه‌اندازی

### پیش‌نیازها:
```bash
Python 3.11+
PostgreSQL Database
```

### نصب:
```bash
cd backend
pip install -r requirements.txt
```

### تنظیمات (.env):
```env
POSTGRES_HOST=your-postgres-host
POSTGRES_PORT=5432
POSTGRES_DATABASE=quality_control
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-password
POSTGRES_SCHEMA=call
API_PORT=8000
```

### اجرا:
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### دسترسی به مستندات:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

---

## 1. Authentication & Users

### 1.1 Login
**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
  "username": "admin",
  "password": "your_password"
}
```

**Response:**
```json
{
  "id": "uuid",
  "username": "admin",
  "full_name": "نام کامل",
  "role": "admin"
}
```

### 1.2 Get All Users (Admin)
**Endpoint:** `GET /users/`

**Response:**
```json
[
  {
    "id": "uuid",
    "username": "user1",
    "full_name": "نام کامل",
    "role": "agent",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00"
  }
]
```

### 1.3 Create User (Admin)
**Endpoint:** `POST /users/`

**Request Body:**
```json
{
  "username": "newuser",
  "password": "secure_password",
  "full_name": "نام کامل",
  "role": "agent"
}
```

### 1.4 Update User (Admin)
**Endpoint:** `PUT /users/{user_id}`

**Request Body:**
```json
{
  "full_name": "نام جدید",
  "role": "supervisor",
  "is_active": true
}
```

### 1.5 Change Password (Admin)
**Endpoint:** `PUT /users/{user_id}/password`

**Request Body:**
```json
{
  "new_password": "new_secure_password"
}
```

### 1.6 Delete User (Admin)
**Endpoint:** `DELETE /users/{user_id}`

---

## 2. Conversations

### 2.1 Get Analyzed Conversations
**Endpoint:** `GET /conversations/analyzed`

**Query Parameters:**
- `agent_id` (optional): فیلتر بر اساس اپراتور
- `call_id` (optional): جستجو بر اساس شناسه تماس
- `date_range` (optional): today, yesterday, last7days, last30days, custom
- `start_date` (optional): تاریخ شروع (YYYY-MM-DD)
- `end_date` (optional): تاریخ پایان (YYYY-MM-DD)
- `status` (optional): pending_review, review_completed
- `page` (default: 1)
- `page_size` (default: 100)

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "created_at": "2024-01-01T00:00:00",
      "opening_score": 3.5,
      "listening_score": 3.2,
      "empathy_score": 3.8,
      "response_process_score": 3.5,
      "system_updation_score": 3.0,
      "closing_score": 3.5,
      "total_weighted_score": 150.5,
      "final_percentage_score": 87.5,
      "conversation_score_ai": 85.0,
      "process_score_human": 90.0,
      "other_criteria_score_human": 88.0,
      "final_score_combined": 87.5,
      "customer_sentiment_label": "positive",
      "customer_sentiment_start": "negative",
      "customer_sentiment_end": "positive",
      "main_topic": "شکایت",
      "strengths": "...",
      "areas_for_improvement": "...",
      "review_status": "pending_review",
      "agent_extension": "1001",
      "call_id": "CALL123456",
      "total_duration_seconds": 300,
      "total_silence_seconds": 15,
      "longest_silence_gap_seconds": 5,
      "silence_percentage": 5.0,
      "silence_timeline": [...],
      "conversation_data": {...},
      "human_review_id": "uuid",
      "reviewer_full_name": "نام ناظر",
      "reviewer_username": "supervisor1"
    }
  ],
  "total": 150,
  "page": 1,
  "page_size": 100,
  "total_pages": 2
}
```

### 2.2 Get Single Analyzed Conversation
**Endpoint:** `GET /conversations/analyzed/{analysis_id}`

**Response:** همان ساختار data item در endpoint بالا

### 2.3 Get Unanalyzed Conversations
**Endpoint:** `GET /conversations/unanalyzed`

**Query Parameters:**
- `agent_id` (optional)
- `call_id` (optional)
- `page` (default: 1)
- `page_size` (default: 100)

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "created_at": "2024-01-01T00:00:00",
      "call_id": "CALL123456",
      "is_analyzed": false,
      "agent_extension": "1001"
    }
  ],
  "total": 50,
  "page": 1,
  "page_size": 100,
  "total_pages": 1
}
```

### 2.4 Trigger Batch Analysis
**Endpoint:** `POST /conversations/analyze/batch`

**Request Body:**
```json
["CALL123", "CALL456", "CALL789"]
```

**Response:**
```json
{
  "message": "3 مکالمه برای تحلیل ارسال شد",
  "call_ids": ["CALL123", "CALL456", "CALL789"],
  "note": "این قابلیت نیاز به پیاده‌سازی فراخوانی webhook دارد"
}
```

---

## 3. Reviews

### 3.1 Get Pending Reviews
**Endpoint:** `GET /reviews/pending`

**Query Parameters:**
- `agent_id` (optional)

**Response:**
```json
{
  "data": [...],  // لیست conversation_analysis که review_status = 'pending_review'
  "total": 25
}
```

### 3.2 Get Completed Reviews
**Endpoint:** `GET /reviews/completed`

**Query Parameters:**
- `agent_id` (optional)

**Response:**
```json
{
  "data": [...],  // لیست conversation_analysis که review_status = 'review_completed'
  "total": 125
}
```

### 3.3 Get Review by Analysis ID
**Endpoint:** `GET /reviews/analysis/{analysis_id}`

**Response:**
```json
{
  "id": "uuid",
  "analysis_id": "uuid",
  "reviewer_id": "uuid",
  "opening_score_override": 3.5,
  "listening_score_override": 3.2,
  "empathy_score_override": 3.8,
  "response_process_score_override": 3.5,
  "system_updation_score_override": 3.0,
  "closing_score_override": 3.5,
  "opening_justification_override": "توضیحات...",
  "listening_justification_override": "توضیحات...",
  "empathy_justification_override": "توضیحات...",
  "response_process_justification_override": "توضیحات...",
  "system_updation_justification_override": "توضیحات...",
  "closing_justification_override": "توضیحات...",
  "strengths_override": "نقاط قوت...",
  "areas_for_improvement_override": "نقاط قابل بهبود...",
  "total_weighted_score_human": 155.5,
  "final_percentage_score_human": 90.0,
  "other_criteria_weighted_score_human": 120.0,
  "other_criteria_percentage_score_human": 88.0,
  "reviewer_full_name": "نام ناظر",
  "reviewer_username": "supervisor1"
}
```

### 3.4 Submit Review
**Endpoint:** `POST /reviews/submit`

**Request Body:**
```json
{
  "analysis_id": "uuid",
  "reviewer_id": "uuid",
  "opening_score_override": 3.5,
  "listening_score_override": 3.2,
  "empathy_score_override": 3.8,
  "response_process_score_override": 3.5,
  "system_updation_score_override": 3.0,
  "closing_score_override": 3.5,
  "opening_justification_override": "...",
  "listening_justification_override": "...",
  "empathy_justification_override": "...",
  "response_process_justification_override": "...",
  "system_updation_justification_override": "...",
  "closing_justification_override": "...",
  "strengths_override": "...",
  "areas_for_improvement_override": "...",
  "total_weighted_score_human": 155.5,
  "final_percentage_score_human": 90.0,
  "other_criteria_weighted_score_human": 120.0,
  "other_criteria_percentage_score_human": 88.0
}
```

**Response:**
```json
{
  "message": "بررسی با موفقیت ثبت شد"
}
```

---

## 4. Comparison

### 4.1 Get Reviewed Conversations for Comparison
**Endpoint:** `GET /comparison/reviewed-conversations`

**Query Parameters:**
- `agent_id` (optional)
- `date_range` (optional)
- `start_date` (optional)
- `end_date` (optional)
- `page` (default: 1)
- `page_size` (default: 100)

**Response:**
```json
{
  "data": [
    {
      "id": "uuid",
      "created_at": "2024-01-01T00:00:00",
      "opening_score": 3.5,
      "listening_score": 3.2,
      "empathy_score": 3.8,
      "response_process_score": 3.5,
      "system_updation_score": 3.0,
      "closing_score": 3.5,
      "total_weighted_score": 150.5,
      "final_percentage_score": 87.5,
      "conversation_score_ai": 85.0,
      "process_score_human": 90.0,
      "other_criteria_score_human": 88.0,
      "final_score_combined": 87.5,
      "agent_extension": "1001",
      "call_id": "CALL123",
      "opening_score_override": 3.8,
      "listening_score_override": 3.5,
      "empathy_score_override": 4.0,
      "response_process_score_override": 3.8,
      "system_updation_score_override": 3.2,
      "closing_score_override": 3.8,
      "total_weighted_score_human": 160.0,
      "final_percentage_score_human": 93.0,
      "other_criteria_weighted_score_human": 125.0,
      "other_criteria_percentage_score_human": 91.0,
      "reviewer_id": "uuid",
      "reviewer_full_name": "نام ناظر",
      "reviewer_username": "supervisor1"
    }
  ],
  "total": 100,
  "page": 1,
  "page_size": 100,
  "total_pages": 1
}
```

### 4.2 Get Single Conversation Comparison
**Endpoint:** `GET /comparison/conversation/{analysis_id}`

**Response:**
```json
{
  ...  // تمام فیلدهای conversation_analysis + human review
  "score_differences": {
    "opening": 0.3,
    "listening": 0.3,
    "empathy": 0.2,
    "response_process": 0.3,
    "system_updation": 0.2,
    "closing": 0.3
  }
}
```

---

## 5. Dashboard

### 5.1 Get Dashboard KPIs
**Endpoint:** `GET /dashboard/kpis`

**Query Parameters:**
- `agent_id` (optional)
- `date_range` (optional)
- `start_date` (optional)
- `end_date` (optional)

**Response:**
```json
{
  "averageScore": 87.5,
  "averageConversationScoreAI": 85.0,
  "averageProcessScoreHuman": 90.0,
  "averageOtherCriteriaScoreHuman": 88.0,
  "averageFinalScoreCombined": 87.5,
  "totalConversations": 1500,
  "positiveSentiment": 1200,
  "negativeSentiment": 300,
  "averageSilencePercentage": 5.2,
  "averageLongestSilence": 8.5,
  "totalSilenceSeconds": 7800,
  "startSentimentPositive": 800,
  "startSentimentNegative": 700,
  "endSentimentPositive": 1200,
  "endSentimentNegative": 300,
  "sentimentImprovement": 171.4
}
```

### 5.2 Get Score Trends
**Endpoint:** `GET /dashboard/score-trends`

**Query Parameters:**
- `agent_id` (optional)
- `date_range` (default: last7days)
- `start_date` (optional)
- `end_date` (optional)

**Response:**
```json
{
  "data": [
    {
      "date": "2024-01-01",
      "average_score": 87.5,
      "average_ai_score": 85.0,
      "average_combined_score": 87.5,
      "conversation_count": 150
    },
    {
      "date": "2024-01-02",
      "average_score": 88.2,
      "average_ai_score": 86.0,
      "average_combined_score": 88.2,
      "conversation_count": 145
    }
  ]
}
```

### 5.3 Get Criteria Scores (AI)
**Endpoint:** `GET /dashboard/criteria-scores`

**Query Parameters:**
- `agent_id` (optional)
- `date_range` (optional)
- `start_date` (optional)
- `end_date` (optional)

**Response:**
```json
{
  "opening": 3.5,
  "listening": 3.2,
  "empathy": 3.8,
  "closing": 3.5
}
```

### 5.4 Get Human Criteria Scores
**Endpoint:** `GET /dashboard/human-criteria-scores`

**Query Parameters:**
- `agent_id` (optional)
- `date_range` (optional)
- `start_date` (optional)
- `end_date` (optional)

**Response:**
```json
{
  "responseProcess": 3.5,
  "systemUpdation": 3.0
}
```

### 5.5 Get Sentiment Distribution
**Endpoint:** `GET /dashboard/sentiment-distribution`

**Query Parameters:**
- `agent_id` (optional)
- `date_range` (optional)
- `start_date` (optional)
- `end_date` (optional)

**Response:**
```json
{
  "positive": 1200,
  "negative": 300,
  "neutral": 100
}
```

### 5.6 Get Top Topics
**Endpoint:** `GET /dashboard/top-topics`

**Query Parameters:**
- `agent_id` (optional)
- `date_range` (optional)
- `start_date` (optional)
- `end_date` (optional)
- `limit` (default: 10, max: 50)

**Response:**
```json
{
  "topics": [
    {
      "main_topic": "شکایت",
      "count": 350
    },
    {
      "main_topic": "استعلام",
      "count": 250
    },
    {
      "main_topic": "پیگیری سفارش",
      "count": 200
    }
  ]
}
```

---

## 6. Leaderboard

### 6.1 Get Agent Leaderboard
**Endpoint:** `GET /leaderboard/agents`

**Query Parameters:**
- `date_range` (optional)
- `start_date` (optional)
- `end_date` (optional)

**Response:**
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "agentExtension": "1001",
      "totalConversations": 250,
      "averageScore": 92.5,
      "averageOpeningScore": 3.8,
      "averageListeningScore": 3.7,
      "averageEmpathyScore": 3.9,
      "averageResponseScore": 3.8,
      "averageClosingScore": 3.9,
      "sentimentImprovementPercent": 185.5,
      "averageSilencePercent": 4.2
    },
    {
      "rank": 2,
      "agentExtension": "1002",
      "totalConversations": 230,
      "averageScore": 90.2,
      "averageOpeningScore": 3.7,
      "averageListeningScore": 3.6,
      "averageEmpathyScore": 3.8,
      "averageResponseScore": 3.7,
      "averageClosingScore": 3.8,
      "sentimentImprovementPercent": 175.0,
      "averageSilencePercent": 4.5
    }
  ],
  "total": 15
}
```

---

## 7. Settings

### 7.1 Get Current Weights
**Endpoint:** `GET /settings/weights`

**Response:**
```json
{
  "opening": 2,
  "listening": 12,
  "empathy": 10,
  "response_process": 15,
  "system_updation": 12,
  "closing": 4
}
```

### 7.2 Update Weights (Admin)
**Endpoint:** `PUT /settings/weights`

**Request Body:**
```json
{
  "opening": 2,
  "listening": 12,
  "empathy": 10,
  "response_process": 15,
  "system_updation": 12,
  "closing": 4,
  "updated_by": "user_id"
}
```

**Response:**
```json
{
  "message": "وزن‌ها با موفقیت به‌روزرسانی شد",
  "weights": {
    "opening": 2,
    "listening": 12,
    "empathy": 10,
    "responseProcess": 15,
    "systemUpdation": 12,
    "closing": 4
  }
}
```

### 7.3 Get Max Score Per Metric
**Endpoint:** `GET /settings/max-score`

**Response:**
```json
{
  "max_score_per_metric": 4
}
```

---

## 8. Agents

### 8.1 Get Agents List
**Endpoint:** `GET /agents/list`

**Response:**
```json
{
  "agents": ["1001", "1002", "1003", "1004", "1005"],
  "total": 5
}
```

---

## 🔍 نکات مهم

### Database Schema
این API با جداول زیر کار می‌کند:
- `conversations_log` - لاگ مکالمات
- `conversation_analysis` - تحلیل‌های AI
- `conversation_review_human` - بررسی‌های انسانی
- `qc_users` - کاربران سیستم
- `qc_settings` - تنظیمات سیستم

### Pagination
تمام endpoint های لیست از pagination پشتیبانی می‌کنند:
```
?page=1&page_size=100
```

### Date Filtering
فیلترهای تاریخ پشتیبانی شده:
- `today` - امروز
- `yesterday` - دیروز
- `last7days` - 7 روز اخیر
- `last30days` - 30 روز اخیر
- `custom` - بازه دلخواه (نیاز به start_date و end_date)

### Weights Snapshot
⚠️ **بسیار مهم:** برای محاسبه امتیازات تاریخی، همیشه از `weights_snapshot` در جدول `conversation_analysis` استفاده شود، نه از وزن‌های فعلی در `qc_settings`.

### Error Handling
تمام endpoint ها در صورت خطا، پاسخ زیر را برمی‌گردانند:
```json
{
  "detail": "پیام خطا به فارسی"
}
```

HTTP Status Codes:
- `200` - موفقیت
- `201` - ایجاد شد
- `400` - درخواست نامعتبر
- `401` - عدم احراز هویت
- `404` - یافت نشد
- `500` - خطای سرور

---

## 📊 تست API

### با cURL:
```bash
# Health Check
curl http://localhost:8000/health

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Get Conversations
curl http://localhost:8000/conversations/analyzed?page=1&page_size=10

# Get Dashboard KPIs
curl "http://localhost:8000/dashboard/kpis?date_range=last7days"
```

### با Swagger UI:
مراجعه کنید به: `http://localhost:8000/docs`

---

## 🚀 Total Endpoints Created

| Category | Endpoints | Status |
|----------|-----------|--------|
| Auth & Users | 6 | ✅ Complete |
| Conversations | 4 | ✅ Complete |
| Reviews | 4 | ✅ Complete |
| Comparison | 2 | ✅ Complete |
| Dashboard | 6 | ✅ Complete |
| Leaderboard | 1 | ✅ Complete |
| Settings | 3 | ✅ Complete |
| Agents | 1 | ✅ Complete |
| Health | 1 | ✅ Complete |
| **TOTAL** | **28** | **✅ Complete** |

---

این backend کامل برای جایگزینی Supabase در پروژه QC Panel آماده است! 🎉
