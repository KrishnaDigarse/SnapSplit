# Quick Polling Guide

## ✅ Your Bill is Being Processed!

**Expense ID:** `2751a684-481f-4f55-9a70-d0a3ba5bbfb8`

---

## 📡 How to Poll for Status

### Method 1: Postman

**Request:**
```http
GET http://127.0.0.1:8000/api/v1/expenses/2751a684-481f-4f55-9a70-d0a3ba5bbfb8/status
Authorization: Bearer {your-token}
```

**Click "Send" to check the current status.**

---

### Method 2: PowerShell (Quick Check)

```powershell
# Set your token
$token = "your-access-token-here"

# Poll status
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/expenses/2751a684-481f-4f55-9a70-d0a3ba5bbfb8/status" -Headers @{Authorization="Bearer $token"}
```

---

## 🎯 What You'll See

### While Processing:
```json
{
  "expense_id": "2751a684-481f-4f55-9a70-d0a3ba5bbfb8",
  "status": "PROCESSING",
  "updated_at": "2026-01-30T19:21:05"
}
```

### When Complete (READY):
```json
{
  "expense_id": "2751a684-481f-4f55-9a70-d0a3ba5bbfb8",
  "status": "READY",
  "subtotal": "1299.00",
  "tax": "140.00",
  "total_amount": "1439.00",
  "items_count": 12,
  "updated_at": "2026-01-30T19:21:10"
}
```

---

## 🔍 Celery Worker Logs Show:

**Your bill is already processed!** ✅

```
[INFO] Task received
[INFO] Starting AI processing for expense 2751a684-481f-4f55-9a70-d0a3ba5bbfb8
[INFO] OCR extracted 644 characters
[INFO] Successfully processed: 12 items, total: ₹1439.00
```

**Poll the status endpoint now to see the READY response!**
