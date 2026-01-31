# Week 3: AI Bill Scanning Integration - Task Breakdown

## Task 0 - Folder Structure Setup
- [x] Create `backend/app/ai/` directory
- [x] Create `backend/app/ai/__init__.py`
- [x] Create `backend/app/ai/ocr.py` (OCR logic)
- [x] Create `backend/app/ai/llm.py` (Gemini client)
- [x] Create `backend/app/ai/prompts.py` (LLM prompts)
- [x] Create `backend/app/ai/parser.py` (JSON validation)
- [x] Create `backend/app/utils/` directory
- [x] Create `backend/app/utils/__init__.py`
- [x] Create `backend/app/utils/image.py` (image preprocessing)
- [x] Create `backend/uploads/bills/` directory

## Task 1 - Bill Image Upload API
- [x] Create `backend/app/routes/ai_expenses.py`
- [x] Implement `POST /api/v1/expenses/bill` endpoint
- [x] Add multipart/form-data handling
- [x] Validate user is group member
- [x] Save uploaded image to `/uploads/bills/`
- [x] Create expense with `source_type=BILL_IMAGE`, `status=PROCESSING`
- [x] Call AI pipeline synchronously
- [x] Update expense status to READY or FAILED
- [x] Add route to main.py

## Task 2 - Image Preprocessing (OpenCV)
- [x] Install opencv-python
- [x] Implement grayscale conversion
- [x] Implement noise reduction
- [x] Implement adaptive thresholding
- [x] Add optional resize functionality
- [x] Add error handling for corrupt images

## Task 3 - OCR Text Extraction
- [x] Install pytesseract and tesseract binary
- [x] Implement OCR extraction function
- [x] Store raw OCR text in `expenses.raw_ocr_text`
- [x] Handle empty OCR results
- [x] Handle corrupt image errors
- [x] Add logging for OCR steps

## Task 4 - LLM Integration (Gemini)
- [x] Install google-generativeai SDK
- [x] Create LLM client configuration
- [x] Design strict JSON extraction prompt
- [x] Implement LLM call with temperature=0
- [x] Handle API errors gracefully
- [x] Add retry logic for transient failures
- [x] Log LLM requests and responses

## Task 5 - AI Output Validation & Cleanup
- [x] Create JSON schema validator
- [x] Implement numeric coercion
- [x] Remove invalid items
- [x] Validate subtotal + tax = total (±2% tolerance)
- [x] Auto-correct minor discrepancies
- [x] Mark expense FAILED on major errors
- [x] Add detailed error logging

## Task 6 - Convert AI Output → Expense
- [x] Create `backend/app/services/ai_expense_service.py`
- [x] Implement expense creation from AI output
- [x] Create expense_items from AI data
- [x] Generate equal splits for group members
- [x] Update expense with subtotal, tax, total
- [x] Set status to READY
- [x] Trigger balance recalculation
- [x] Reuse existing Week 2 services

## Task 7 - Documentation
- [x] Create `backend/docs/ai_pipeline.md`
- [x] Create `backend/docs/bill_expenses.md`
- [x] Document OCR vs LLM distinction
- [x] Document AI failure modes
- [x] Explain sync-first approach
- [x] Document manual fallback flow
- [x] Add API examples

## Task 8 - Testing & Validation
- [x] Install Tesseract OCR (user must do this)
- [x] Get Gemini API key (user must do this)
- [x] Test with clean restaurant bill
- [x] Test with skewed photo
- [x] Test with low light image
- [x] Test with OCR garbage text
- [x] Test with LLM invalid JSON
- [x] Verify no crashes on errors
- [x] Verify clear error messages
- [x] Verify expense status (READY or FAILED)
- [x] Update Postman collection

## Dependencies to Install
- [x] opencv-python
- [x] pytesseract
- [x] google-generativeai
- [x] pillow
- [x] tenacity

## Notes
- ⛔ NO Celery/async workers this week
- ⛔ NO database schema modifications
- ✅ Synchronous execution only
- ✅ Reuse Week 2 services
- ✅ Production-ready code with proper error handling
