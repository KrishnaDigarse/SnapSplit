# Async AI Pipeline Architecture

## Overview

Week 4 converts the AI bill scanning pipeline from **synchronous blocking** execution to **asynchronous non-blocking** execution using Celery workers.

## Why Async?

### Week 3 (Synchronous) Problems:

1. **Blocking Requests** - API waits 5-15 seconds for AI processing
2. **Poor UX** - Frontend freezes during upload
3. **Timeout Risk** - Long processing may exceed HTTP timeouts
4. **No Scalability** - Can't process multiple bills concurrently
5. **No Retry** - Transient failures (network, OCR) cause permanent failure

### Week 4 (Asynchronous) Benefits:

1. ✅ **Instant Response** - API returns immediately (< 100ms)
2. ✅ **Better UX** - Frontend can show progress/loading state
3. ✅ **No Timeouts** - Processing happens in background
4. ✅ **Scalable** - Multiple workers process bills in parallel
5. ✅ **Fault Tolerant** - Automatic retries on transient errors
6. ✅ **Monitoring** - Track task progress and failures

## Architecture Diagram

```
┌─────────────┐
│   Frontend  │
└──────┬──────┘
       │ 1. POST /api/v1/expenses/bill
       │    (with image file)
       ▼
┌─────────────────────────────────────┐
│         FastAPI Server              │
│  ┌──────────────────────────────┐   │
│  │  1. Validate image           │   │
│  │  2. Save to disk             │   │
│  │  3. Create expense (PROCESSING)│  │
│  │  4. Enqueue Celery task      │   │
│  │  5. Return 202 ACCEPTED      │   │
│  └──────────────────────────────┘   │
└──────────┬──────────────────────────┘
           │ 2. Enqueue task
           ▼
    ┌──────────────┐
    │    Redis     │  ← Message Broker
    │   (Queue)    │     & Result Backend
    └──────┬───────┘
           │ 3. Worker pulls task
           ▼
┌─────────────────────────────────────┐
│       Celery Worker                 │
│  ┌──────────────────────────────┐   │
│  │  process_bill_image_task     │   │
│  │  ┌────────────────────────┐  │   │
│  │  │ 1. Check idempotency   │  │   │
│  │  │ 2. Run OCR             │  │   │
│  │  │ 3. Run LLM             │  │   │
│  │  │ 4. Validate data       │  │   │
│  │  │ 5. Create items/splits │  │   │
│  │  │ 6. Update status       │  │   │
│  │  │    → READY or FAILED   │  │   │
│  │  └────────────────────────┘  │   │
│  └──────────────────────────────┘   │
└─────────────────────────────────────┘
           │ 4. Update database
           ▼
    ┌──────────────┐
    │  PostgreSQL  │
    │  (Database)  │
    └──────┬───────┘
           │ 5. Frontend polls
           ▼
┌─────────────────────────────────────┐
│   GET /api/v1/expenses/{id}/status  │
│   Returns: PROCESSING | READY | FAILED
└─────────────────────────────────────┘
```

## Task Lifecycle

### 1. Task Creation (API Endpoint)

```python
# POST /api/v1/expenses/bill
expense = Expense(
    status=ExpenseStatus.PROCESSING,
    subtotal=None,  # NULL until AI completes
    tax=None,
    total_amount=None
)
db.add(expense)
db.commit()

# Enqueue task
task = process_bill_image_task.delay(
    expense_id=str(expense.id),
    image_path=file_path,
    group_id=str(group_uuid)
)

# Return immediately
return {
    "id": str(expense.id),
    "status": "PROCESSING",
    "message": "Poll /api/v1/expenses/{id}/status"
}
```

### 2. Task Execution (Celery Worker)

```python
@celery_app.task(max_retries=3, retry_backoff=30)
def process_bill_image_task(expense_id, image_path, group_id):
    # Idempotency guard
    if expense.status != ExpenseStatus.PROCESSING:
        return {"status": "skipped"}
    
    # Run AI pipeline (Week 3 code - unchanged)
    process_bill_image(db, expense_id, image_path, group_id)
    
    # Update status
    expense.status = ExpenseStatus.READY
    db.commit()
```

### 3. Status Polling (Frontend)

```javascript
// Upload bill
const response = await fetch('/api/v1/expenses/bill', {
    method: 'POST',
    body: formData
});

const { id } = await response.json();

// Poll status every 2 seconds
const interval = setInterval(async () => {
    const status = await fetch(`/api/v1/expenses/${id}/status`);
    const data = await status.json();
    
    if (data.status === 'READY') {
        clearInterval(interval);
        // Show success, display expense
    } else if (data.status === 'FAILED') {
        clearInterval(interval);
        // Show error
    }
}, 2000);
```

## Retry Strategy

### Retry Logic

```python
autoretry_for=(OCRError, LLMError, ConnectionError, TimeoutError)
dont_autoretry_for=(ValidationError, ValueError, FileNotFoundError)
max_retries=3
retry_backoff=30  # 30s, 90s, 300s
```

### Retry Timeline

| Attempt | Delay | Total Time | Errors Retried |
|---------|-------|------------|----------------|
| 1       | 0s    | 0s         | Initial attempt |
| 2       | 30s   | 30s        | OCR/LLM/Network |
| 3       | 90s   | 120s       | OCR/LLM/Network |
| 4       | 300s  | 420s       | OCR/LLM/Network |

**After 3 retries:** Expense marked as `FAILED`

### Error Categories

**Transient (Retry):**
- OCR errors (Tesseract timeout)
- LLM errors (Groq API rate limit)
- Network errors (connection timeout)
- Timeout errors

**Permanent (No Retry):**
- Validation errors (bad data structure)
- Value errors (invalid image format)
- File not found (image deleted)

## Idempotency

### Why It Matters

Tasks may be retried due to:
- Worker crash
- Network failure
- Manual retry

Without idempotency guard, a task could:
- Process the same bill twice
- Create duplicate items
- Overwrite existing data

### Implementation

```python
# Check if already processed
if expense.status != ExpenseStatus.PROCESSING:
    logger.warning(f"Expense {expense_id} already processed")
    return {"status": "skipped"}

# Safe to process
process_bill_image(...)
```

## Failure Handling

### Scenario 1: OCR Fails (Transient)

```
Attempt 1: OCR timeout → Retry in 30s
Attempt 2: OCR timeout → Retry in 90s
Attempt 3: OCR success → READY
```

### Scenario 2: Invalid Image (Permanent)

```
Attempt 1: ValidationError → FAILED (no retry)
```

### Scenario 3: Worker Crash

```
Attempt 1: Worker crashes mid-task
Worker restarts → Task requeued
Attempt 2: Idempotency guard → Skips if already processed
```

## Status Transitions

```
PROCESSING → READY    (Success)
PROCESSING → FAILED   (Permanent error or max retries)
PROCESSING → PROCESSING (Retry in progress)
```

**Invalid transitions (prevented by idempotency guard):**
```
READY → PROCESSING  ❌
FAILED → PROCESSING ❌
```

## Comparison: Week 3 vs Week 4

| Aspect | Week 3 (Sync) | Week 4 (Async) |
|--------|---------------|----------------|
| **Response Time** | 5-15 seconds | < 100ms |
| **HTTP Status** | 201 Created | 202 Accepted |
| **Frontend** | Waits for result | Polls for result |
| **Scalability** | 1 request at a time | Parallel processing |
| **Retry** | No retry | 3 retries with backoff |
| **Monitoring** | No visibility | Celery monitoring |
| **Failure Recovery** | Manual retry | Automatic retry |

## Database Schema

**No changes required!** We reuse existing fields:

```python
class Expense:
    status: ExpenseStatus  # PROCESSING, READY, FAILED
    subtotal: Decimal | None  # NULL during PROCESSING
    tax: Decimal | None
    total_amount: Decimal | None
```

**Why NULL instead of 0?**
- Clearer semantics (0 could mean "free bill")
- Frontend can distinguish "pending" from "zero"
- No schema changes needed

## Monitoring

### Celery Flower

Web UI for monitoring tasks:
```bash
pip install flower
celery -A app.celery_app flower
```

Access: http://localhost:5555

### Logs

```bash
# Worker logs
celery -A app.celery_app worker --loglevel=info

# Task-specific logs
[2024-01-31 00:00:00] INFO: Starting AI processing for expense abc-123
[2024-01-31 00:00:05] INFO: OCR Success: 340 characters
[2024-01-31 00:00:08] INFO: LLM Success: 5 items extracted
[2024-01-31 00:00:10] INFO: Successfully processed expense abc-123
```

## Future Enhancements (Week 5+)

1. **WebSockets** - Real-time status updates (no polling)
2. **Notifications** - Email/SMS when processing completes
3. **Batch Processing** - Upload multiple bills at once
4. **Priority Queue** - VIP users get faster processing
5. **Result Caching** - Cache OCR results for duplicate images

## Testing

### Manual Test

1. Start Redis: `docker-compose up -d redis`
2. Start Worker: `celery -A app.celery_app worker --loglevel=info`
3. Start API: `python -m uvicorn main:app --reload`
4. Upload bill via Postman
5. Observe:
   - API returns immediately with `PROCESSING`
   - Worker logs show task execution
   - Poll status endpoint → `READY`

### Integration Test

```python
def test_async_bill_processing():
    # Upload bill
    response = client.post("/api/v1/expenses/bill", ...)
    assert response.status_code == 202
    expense_id = response.json()["id"]
    
    # Poll status
    for _ in range(30):  # Max 60 seconds
        status = client.get(f"/api/v1/expenses/{expense_id}/status")
        if status.json()["status"] == "READY":
            break
        time.sleep(2)
    
    # Verify result
    assert status.json()["status"] == "READY"
    assert status.json()["items_count"] > 0
```

## Summary

Week 4 transforms the AI pipeline from a **blocking operation** to a **scalable, fault-tolerant background job system**. This provides:

- ✅ Better user experience (instant response)
- ✅ Higher throughput (parallel processing)
- ✅ Fault tolerance (automatic retries)
- ✅ Production readiness (monitoring, logging)

**All while reusing Week 3's AI logic without any modifications!**
