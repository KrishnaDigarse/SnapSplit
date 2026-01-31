# Celery Setup Guide

## Overview

SnapSplit uses Celery for asynchronous task processing, specifically for AI bill scanning. This allows the API to return immediately while AI processing happens in the background.

## Prerequisites

- Python 3.10+
- Redis (running on localhost:6379)
- All project dependencies installed

## Installation

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

This installs:
- `celery==5.3.4` - Task queue
- `redis==5.0.1` - Message broker and result backend

### 2. Start Redis

**Using Docker (Recommended):**
```bash
docker-compose up -d redis
```

**Or install Redis locally:**
- Windows: https://redis.io/docs/getting-started/installation/install-redis-on-windows/
- Mac: `brew install redis && brew services start redis`
- Linux: `sudo apt-get install redis-server && sudo systemctl start redis`

### 3. Configure Environment Variables

Add to `.env`:
```bash
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Running Celery Worker

### Development

Start the Celery worker in a separate terminal:

```bash
cd backend
celery -A app.celery_app worker --loglevel=info
```

**Expected output:**
```
-------------- celery@hostname v5.3.4
---- **** -----
--- * ***  * -- Windows-10.0.19045-SP0 2024-01-31 00:00:00
-- * - **** ---
- ** ---------- [config]
- ** ---------- .> app:         snapsplit:0x...
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     redis://localhost:6379/0
- *** --- * --- .> concurrency: 4 (prefork)
-- ******* ---- .> task events: OFF

[tasks]
  . app.tasks.ai_tasks.process_bill_image_task

[2024-01-31 00:00:00,000: INFO/MainProcess] Connected to redis://localhost:6379/0
[2024-01-31 00:00:00,000: INFO/MainProcess] celery@hostname ready.
```

### Production

For production, use a process manager like Supervisor or systemd:

**Example systemd service (`/etc/systemd/system/celery-snapsplit.service`):**
```ini
[Unit]
Description=Celery Worker for SnapSplit
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/snapsplit/backend
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/celery -A app.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --pidfile=/var/run/celery/snapsplit.pid \
    --logfile=/var/log/celery/snapsplit.log

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable celery-snapsplit
sudo systemctl start celery-snapsplit
sudo systemctl status celery-snapsplit
```

## Configuration

### Worker Concurrency

Adjust based on your server's CPU cores:

```bash
# 4 concurrent workers
celery -A app.celery_app worker --concurrency=4

# Auto-detect (number of CPUs)
celery -A app.celery_app worker --concurrency=0
```

### Task Time Limits

Configured in `app/core/celery_config.py`:
- **Hard limit:** 600 seconds (10 minutes)
- **Soft limit:** 540 seconds (9 minutes)

### Retry Policy

- **Max retries:** 3
- **Backoff:** 30s, 90s, 300s (exponential)
- **Retry on:** OCR errors, LLM errors, network errors
- **No retry on:** Validation errors, invalid images

## Monitoring

### Check Worker Status

```bash
celery -A app.celery_app inspect active
celery -A app.celery_app inspect stats
```

### View Task Results

```bash
celery -A app.celery_app result <task-id>
```

### Flower (Web-based Monitoring)

Install Flower:
```bash
pip install flower
```

Run:
```bash
celery -A app.celery_app flower
```

Access at: http://localhost:5555

## Troubleshooting

### Worker not starting

**Check Redis connection:**
```bash
redis-cli ping
# Should return: PONG
```

**Check environment variables:**
```bash
echo $CELERY_BROKER_URL
echo $CELERY_RESULT_BACKEND
```

### Tasks not executing

**Check worker logs:**
```bash
celery -A app.celery_app worker --loglevel=debug
```

**Verify task registration:**
```bash
celery -A app.celery_app inspect registered
```

Should show:
```
app.tasks.ai_tasks.process_bill_image_task
```

### Redis connection errors

**Verify Redis is running:**
```bash
docker ps | grep redis
# or
sudo systemctl status redis
```

**Test connection:**
```bash
redis-cli -h localhost -p 6379 ping
```

## Testing

### Manual Task Execution

```python
from app.tasks.ai_tasks import process_bill_image_task

# Enqueue task
task = process_bill_image_task.delay(
    expense_id="uuid-here",
    image_path="/path/to/image.jpg",
    group_id="group-uuid"
)

# Check status
print(task.status)  # PENDING, STARTED, SUCCESS, FAILURE

# Get result
result = task.get(timeout=60)
print(result)
```

### Integration Test

1. Start Redis
2. Start Celery worker
3. Start FastAPI server
4. Upload bill via Postman
5. Poll status endpoint
6. Verify task completes

## Performance Tips

1. **Use connection pooling** - Redis connections are pooled automatically
2. **Monitor memory** - Workers restart after 100 tasks to prevent leaks
3. **Scale horizontally** - Run multiple workers on different machines
4. **Use SSD** - Faster disk I/O for image processing
5. **Optimize concurrency** - Match worker count to CPU cores

## Security

- **Never expose Redis** to the internet without authentication
- **Use Redis password** in production:
  ```bash
  CELERY_BROKER_URL=redis://:password@localhost:6379/0
  ```
- **Firewall rules** - Only allow backend servers to access Redis
- **TLS/SSL** - Use `rediss://` for encrypted connections

## Next Steps

- Set up monitoring with Flower
- Configure log rotation
- Implement task result cleanup
- Add WebSocket notifications (Week 5+)
