# AI Pipeline Architecture

## Overview

The SnapSplit AI pipeline transforms bill images into structured expenses through a multi-stage process involving OCR, LLM, and validation.

## Why OCR ≠ LLM

### OCR (Optical Character Recognition)
**Purpose:** Extract raw text from images

**Technology:** Tesseract OCR

**Input:** Bill image (JPG/PNG)

**Output:** Unstructured text string

**Example:**
```
1. Burger         $12.00
2. Fries          $5.00
Subtotal:         $17.00
Tax (10%):        $1.70
Total:            $18.70
```

**Limitations:**
- No understanding of structure
- No semantic meaning
- Can't distinguish item names from prices
- Doesn't understand math

### LLM (Large Language Model)
**Purpose:** Extract structured data from unstructured text

**Technology:** Google Gemini 1.5 Flash

**Input:** Raw OCR text

**Output:** Structured JSON

**Example:**
```json
{
  "items": [
    {"name": "Burger", "quantity": 1, "price": 12.00},
    {"name": "Fries", "quantity": 1, "price": 5.00}
  ],
  "subtotal": 17.00,
  "tax": 1.70,
  "total": 18.70
}
```

**Capabilities:**
- Understands context
- Extracts semantic meaning
- Identifies item names, quantities, prices
- Validates mathematical relationships

### Why Both?

**OCR First:**
- LLMs cannot process images directly (or it's expensive)
- OCR is fast and cheap
- Provides text that LLM can understand

**LLM Second:**
- OCR output is messy and unstructured
- LLM can parse and structure the data
- LLM can handle variations in bill formats

## Pipeline Stages

### Stage 1: Image Preprocessing
**Module:** `app/utils/image.py`

**Steps:**
1. Load image
2. Resize if too large (>2000px width)
3. Convert to grayscale
4. Apply Gaussian blur (noise reduction)
5. Apply adaptive thresholding (enhance contrast)

**Why:**
- Grayscale reduces complexity, speeds up OCR
- Blur removes camera noise
- Thresholding makes text stand out
- Preprocessing improves OCR accuracy by 20-30%

### Stage 2: OCR Text Extraction
**Module:** `app/ai/ocr.py`

**Process:**
1. Run Tesseract on preprocessed image
2. Extract text with line breaks preserved
3. Validate output (minimum length, alphanumeric content)
4. Store raw text in `expenses.raw_ocr_text`

**Error Handling:**
- Empty text → Raise `OCRError`
- Corrupt image → Raise `OCRError`
- Tesseract not installed → Clear error message

### Stage 3: LLM Data Extraction
**Module:** `app/ai/llm.py`

**Process:**
1. Build prompt with OCR text
2. Call Gemini API with temperature=0 (deterministic)
3. Parse JSON response
4. Validate required fields

**Configuration:**
- Model: `gemini-1.5-flash` (fast, cost-effective)
- Temperature: 0 (no randomness)
- Max tokens: 2048
- Retry: 3 attempts with exponential backoff

**Error Handling:**
- API error → Retry 3x, then raise `LLMError`
- Invalid JSON → Raise `LLMError`
- Missing fields → Raise `LLMError`

### Stage 4: Data Validation & Cleanup
**Module:** `app/ai/parser.py`

**Process:**
1. Validate schema (required fields present)
2. Coerce numbers (handle strings, currency symbols)
3. Remove invalid items (missing name/price)
4. Validate math: `subtotal + tax ≈ total`
5. Auto-correct if error < 2%
6. Fail if error > 2%

**Validation Rules:**
- Items must have name and price
- Prices must be positive
- Quantities default to 1
- Math must be correct within 2% tolerance

**Auto-Correction:**
- If `subtotal + tax` differs from `total` by <2%, use calculated total
- Logs warning for manual review

### Stage 5: Expense Creation
**Module:** `app/services/ai_expense_service.py`

**Process:**
1. Create expense items from validated data
2. Generate equal splits for all group members
3. Update expense totals
4. Set status to READY
5. Trigger balance recalculation

**Reuses Week 2 Services:**
- Uses existing expense item creation logic
- Uses existing split generation logic
- Uses existing balance calculation service

## AI Failure Modes

### 1. OCR Failures

**Causes:**
- Blurry image
- Low light
- Skewed/rotated photo
- No text in image
- Corrupt file

**Handling:**
- Mark expense as FAILED
- Store error message
- Preserve image for manual review
- Suggest: "Please upload a clearer photo"

### 2. LLM Failures

**Causes:**
- API timeout
- API rate limit
- Invalid JSON output
- Hallucinated data

**Handling:**
- Retry 3x with exponential backoff
- Mark expense as FAILED if all retries fail
- Preserve raw OCR text for debugging
- Log full error details

### 3. Validation Failures

**Causes:**
- Math doesn't add up (>2% error)
- No valid items extracted
- Missing required fields

**Handling:**
- Mark expense as FAILED
- Store validation error details
- Preserve OCR text and LLM output
- Allow manual expense creation as fallback

### 4. Unexpected Errors

**Causes:**
- File system errors
- Database errors
- Memory errors

**Handling:**
- Catch all exceptions
- Mark expense as FAILED
- Log full stack trace
- Never crash the API

## Sync vs Async

### Week 3: Synchronous Processing

**How it works:**
1. User uploads image
2. API waits for AI processing (5-15 seconds)
3. Returns completed expense

**Pros:**
- Simple to implement
- Easy to debug
- No queue infrastructure needed
- User gets immediate feedback

**Cons:**
- User waits 5-15 seconds
- API request tied up during processing
- Can't handle high load

### Week 4: Asynchronous Processing (Future)

**How it will work:**
1. User uploads image
2. API returns immediately with status PROCESSING
3. Celery worker processes in background
4. User polls or receives webhook when done

**Pros:**
- Instant API response
- Can retry failed jobs
- Better scalability
- Can process multiple bills in parallel

**Cons:**
- More complex infrastructure
- Requires Celery + Redis/RabbitMQ
- Need polling or webhooks for status

**Decision:** Start sync, add async later when needed.

## Manual Fallback Flow

If AI processing fails, users can manually create the expense:

1. **View Failed Expense**
   - See status: FAILED
   - See error message
   - See uploaded bill image

2. **Manual Entry**
   - Use regular manual expense creation
   - Copy data from bill image
   - Create expense items manually

3. **Delete Failed Expense**
   - Optional: delete the failed AI expense
   - Or keep it for reference

## Performance Metrics

**Typical Processing Time:**
- Image preprocessing: 0.5-1s
- OCR extraction: 2-4s
- LLM extraction: 3-8s
- Validation & expense creation: 0.5-1s
- **Total: 6-14 seconds**

**Accuracy:**
- Clean bills: 90-95% success rate
- Skewed photos: 70-80% success rate
- Low light: 50-60% success rate
- Handwritten bills: 20-30% success rate

**Cost (Gemini API):**
- ~$0.0001 per bill (1.5 Flash pricing)
- Very cost-effective for MVP

## Monitoring & Debugging

**Logs:**
- All stages logged with INFO level
- Errors logged with ERROR level
- OCR text preview logged (first 200 chars)
- LLM response logged
- Validation results logged

**Stored Data:**
- `expenses.raw_ocr_text` - Full OCR output
- `expenses.image_url` - Original bill image
- `expenses.description` - Error messages if failed
- `expenses.status` - PROCESSING, READY, or FAILED

**Debugging Failed Expenses:**
1. Check `raw_ocr_text` - Was OCR successful?
2. Check logs - Where did it fail?
3. Check image - Is it readable?
4. Retry with better image if needed

## Security Considerations

**File Upload:**
- Max size: 10MB
- Allowed types: JPG, PNG only
- Files saved to local disk (not database)
- Unique filenames (UUID-based)

**API Key:**
- Gemini API key in environment variable
- Never exposed to client
- Rotated periodically

**Data Privacy:**
- Bill images stored locally
- OCR text stored in database
- No data sent to third parties (except Gemini API)
- Consider encryption for sensitive bills

## Future Improvements

**Week 4+:**
- [ ] Async processing with Celery
- [ ] Webhook notifications
- [ ] Image cleanup job (delete old bills)
- [ ] Support for PDF bills
- [ ] Multi-language OCR
- [ ] Receipt photo tips in UI
- [ ] Confidence scores for items
- [ ] Manual correction UI
- [ ] Batch bill processing
- [ ] Receipt templates for common merchants
