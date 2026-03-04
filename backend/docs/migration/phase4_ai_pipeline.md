# Phase 4 — AI Pipeline (OCR + LLM)

## Objective

Migrate the AI-powered bill processing pipeline from Python (pytesseract + Groq Python SDK + Celery) to Java (Tess4J + Spring RestClient + @Async).

---

## Python → Spring Boot Mapping

| Component | Python | Java |
|---|---|---|
| OCR engine | `pytesseract` (Tesseract wrapper) | `Tess4J` 5.13.0 (Tesseract JNI wrapper) |
| Image preprocessing | OpenCV (`cv2`) | `BufferedImage` (JDK built-in) |
| LLM client | `groq.Groq` Python SDK | Spring `RestClient` → Groq REST API |
| Retry logic | `tenacity` decorator | Manual retry loop (3 attempts) |
| Background tasks | Celery + Redis broker | Spring `@Async` (thread pool) |
| Bill parser | Custom Python module | `BillParser` Java component |
| Prompts | Python f-strings | Java text blocks (`"""`) |

---

## Files Created (6 files)

### `OcrService.java` — Multi-Strategy OCR
- 3 strategies: PSM 6 direct, preprocessed grayscale, PSM 3 auto
- Quality scoring: text length + word count + digit ratio + alphanumeric ratio
- Picks the highest-scoring result

### `LlmService.java` — Groq API Client
- Calls `https://api.groq.com/openai/v1/chat/completions`
- Uses `json_object` response format for clean JSON output
- 3-attempt retry with exponential backoff

### `BillPrompts.java` — Prompt Templates
- Identical prompt to Python version
- Java text block syntax (`"""`)

### `BillParser.java` — Data Validation
- Schema validation (items, subtotal, tax, total)
- Number coercion (currency symbol removal)
- Item cleanup (remove invalid entries)
- Math validation with 2% tolerance auto-correction

### `AiExpenseService.java` — 7-Step Pipeline
```
@Async  // runs in background thread (replaces Celery)
processBillImageAsync(expenseId, imagePath, groupId)
  1. OCR → extract text
  2. LLM → extract structured JSON
  3. Parser → validate + clean
  4. Create ExpenseItems
  5. Generate equal splits for all group members
  6. Update expense status → READY
  7. Update group balances
```
Includes idempotency guard (skips if status ≠ PROCESSING).

### `AiExpenseController.java` — Upload + Status Endpoints

| Endpoint | Method | Status | Description |
|---|---|---|---|
| `POST /api/v1/expenses/bill` | Upload | 202 | Multipart upload, validates file (10MB, JPG/PNG), saves, enqueues async |
| `GET /api/v1/expenses/{id}/status` | Poll | 200 | Returns PROCESSING/READY/FAILED with details |

---

## Dependencies Added

```xml
<!-- pom.xml -->
<dependency>
    <groupId>net.sourceforge.tess4j</groupId>
    <artifactId>tess4j</artifactId>
    <version>5.13.0</version>
</dependency>
```

## Config Added (`application.yml`)
```yaml
app:
  groq:
    api-key: ${GROQ_API_KEY:}
    model: llama-3.3-70b-versatile
  ocr:
    tessdata-path: ${TESSDATA_PREFIX:}
  upload:
    dir: uploads/bills
```

---

## Build Verification

```
$ mvn compile
[INFO] Compiling 73 source files → BUILD SUCCESS (10.485 s)
```
