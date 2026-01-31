# Week 4 Async Workflow - Postman Test Guide

## 🎯 Test Objective

Verify that bill upload returns immediately (HTTP 202) and processing happens in background.

---

## ✅ Prerequisites (All Running)

- ✅ **Redis**: `docker-compose up -d redis`
- ✅ **Celery Worker**: `celery -A app.celery_app worker --loglevel=info --pool=solo`
  - Task registered: `app.tasks.ai_tasks.process_bill_image_task`
- ✅ **FastAPI**: `python -m uvicorn main:app --reload`
  - Running on: http://127.0.0.1:8000

---

## 📝 Test Steps

### Step 1: Get Authentication Token

**Request:**
```http
POST http://127.0.0.1:8000/api/v1/auth/login
Content-Type: application/json

{
  "email": "your-email@example.com",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**Save the `access_token` for next steps.**

---

### Step 2: Upload Bill (Async)

**Request:**
```http
POST http://127.0.0.1:8000/api/v1/expenses/bill
Authorization: Bearer {your-access-token}
Content-Type: multipart/form-data

Form Data:
- image: [select a bill image file]
- group_id: {your-group-uuid}
```

**Expected Response (HTTP 202 ACCEPTED):**
```json
{
  "id": "abc-123-def-456",
  "status": "PROCESSING",
  "message": "Bill is being processed. Poll /api/v1/expenses/{id}/status for updates.",
  "created_at": "2026-01-31T00:45:00"
}
```

**⏱️ Response Time:** < 500ms (instant!)

**Save the `id` for polling.**

---

### Step 3: Poll Status (Immediately)

**Request:**
```http
GET http://127.0.0.1:8000/api/v1/expenses/{expense-id}/status
Authorization: Bearer {your-access-token}
```

**Expected Response (PROCESSING):**
```json
{
  "expense_id": "abc-123-def-456",
  "status": "PROCESSING",
  "updated_at": "2026-01-31T00:45:01"
}
```

---

### Step 4: Poll Status (After 5-10 seconds)

**Request:** (Same as Step 3)

**Expected Response (READY):**
```json
{
  "expense_id": "abc-123-def-456",
  "status": "READY",
  "subtotal": "59.00",
  "tax": "10.62",
  "total_amount": "69.62",
  "items_count": 5,
  "updated_at": "2026-01-31T00:45:10"
}
```

---

## 🔍 What to Observe

### 1. Celery Worker Logs

You should see:
```
[INFO] Task app.tasks.ai_tasks.process_bill_image_task[...] received
[INFO] Starting AI processing for expense abc-123-def-456
[INFO] OCR Success: 340 characters
[INFO] LLM Success: 5 items extracted
[INFO] Successfully processed expense abc-123-def-456
[INFO] Task app.tasks.ai_tasks.process_bill_image_task[...] succeeded
```

### 2. FastAPI Logs

You should see:
```
INFO: POST /api/v1/expenses/bill - 202 Accepted
INFO: GET /api/v1/expenses/{id}/status - 200 OK
INFO: GET /api/v1/expenses/{id}/status - 200 OK
```

### 3. Database

Check the expense record:
```sql
SELECT id, status, subtotal, tax, total_amount, created_at, updated_at
FROM expenses
WHERE id = 'abc-123-def-456';
```

**Status progression:**
- Initially: `PROCESSING`, `subtotal=NULL`, `tax=NULL`, `total_amount=NULL`
- After task: `READY`, `subtotal=59.00`, `tax=10.62`, `total_amount=69.62`

---

## ✅ Success Criteria

1. ✅ **Instant Response**: POST /bill returns in < 500ms
2. ✅ **HTTP 202**: Status code is 202 ACCEPTED (not 201)
3. ✅ **PROCESSING Status**: Initial poll shows PROCESSING
4. ✅ **Background Processing**: Celery worker logs show task execution
5. ✅ **READY Status**: After 5-10s, poll shows READY with data
6. ✅ **Data Extracted**: Items, subtotal, tax, total populated

---

## ❌ Failure Scenarios

### Scenario 1: Task Enqueue Fails

**Symptom:** POST /bill returns HTTP 500

**Response:**
```json
{
  "detail": "Failed to enqueue processing task. Please try again."
}
```

**Check:**
- Is Redis running? `docker ps | grep redis`
- Is Celery worker running?

### Scenario 2: Task Fails (Permanent Error)

**Symptom:** Status shows FAILED

**Response:**
```json
{
  "expense_id": "abc-123-def-456",
  "status": "FAILED",
  "error_message": "AI processing failed. Please try uploading the image again.",
  "updated_at": "2026-01-31T00:45:05"
}
```

**Check Celery logs for error details.**

### Scenario 3: Task Retries (Transient Error)

**Celery logs:**
```
[WARNING] Transient error processing expense abc-123 (attempt 1/3): OCR timeout
[INFO] Retrying in 30 seconds...
```

**Status remains PROCESSING during retries.**

---

## 🧪 Test Images

Use these test images from `backend/test_images/`:
- `sample_bill.png` - Restaurant bill with discount
- `sample_bill_1.png` - Grocery receipt
- `sample_bill_2.png` - Coffee shop bill
- `sample_bill_3.png` - Indian restaurant bill

---

## 📊 Performance Comparison

| Metric | Week 3 (Sync) | Week 4 (Async) |
|--------|---------------|----------------|
| API Response Time | 5-15 seconds | < 500ms |
| HTTP Status | 201 Created | 202 Accepted |
| Frontend Behavior | Waits/freezes | Polls status |
| Concurrent Uploads | 1 at a time | Unlimited |

---

## 🎉 Expected Outcome

**Week 4 async implementation is successful if:**

1. ✅ API returns immediately (< 500ms)
2. ✅ Status polling works correctly
3. ✅ Background task processes bill successfully
4. ✅ Retry logic works on transient errors
5. ✅ Idempotency guard prevents double-processing

**You should see a dramatic improvement in user experience!** 🚀
