# Testing AI Bill Scanning

This directory contains test scripts for the AI bill scanning feature.

## Test Scripts

### 1. Setup Verification (`test_ai_setup.py`)

**Purpose:** Verify all prerequisites are installed correctly.

**Run this first:**
```bash
python test_ai_setup.py
```

**What it checks:**
- ✅ OpenCV installed
- ✅ Tesseract OCR installed and in PATH
- ✅ Gemini API key configured
- ✅ Pillow (PIL) installed
- ✅ tenacity installed
- ✅ Server running on http://localhost:8000

**Expected output:**
```
✅ All setup checks passed!
You're ready to test bill scanning
```

### 2. Bill Scanning Test (`test_bill_scanning.py`)

**Purpose:** Test the complete bill upload and AI processing pipeline.

**Prerequisites:**
- Server must be running: `python -m uvicorn main:app --reload`
- Tesseract OCR installed
- GEMINI_API_KEY in `.env` file

**Run the test:**
```bash
python test_bill_scanning.py
```

**What it does:**
1. ✅ Verifies setup (Tesseract, Gemini API)
2. ✅ Creates a sample bill image
3. ✅ Registers a test user
4. ✅ Logs in and gets JWT token
5. ✅ Creates a test group
6. ✅ Uploads the bill image
7. ✅ Waits for AI processing (5-15 seconds)
8. ✅ Verifies expense created with items and splits

**Expected output:**
```
🧪 SnapSplit AI Bill Scanning - Test Suite
============================================================

0️⃣ Verifying Setup
============================================================
✅ Server is running
✅ Tesseract OCR installed: 5.3.3
✅ Gemini API key found

1️⃣ Registering Test User
============================================================
✅ User registered: bill_test_user@example.com

2️⃣ Logging In
============================================================
✅ Login successful

3️⃣ Creating Test Group
============================================================
✅ Group created: Bill Test Group

4️⃣ Uploading Bill Image
============================================================
ℹ️  Uploading and processing (this may take 5-15 seconds)...
ℹ️  Processing took 8.45 seconds
✅ Bill uploaded successfully!
✅ AI processing succeeded!
ℹ️  Subtotal: $20.00
ℹ️  Tax: $2.00
ℹ️  Total: $22.00
ℹ️  Items extracted: 3

Extracted Items:
  - Burger: $12.00 x 1
  - Fries: $5.00 x 1
  - Soda: $3.00 x 1

5️⃣ Verifying Expense Details
============================================================
✅ Expense retrieved successfully
ℹ️  Splits created: 1
✅ OCR text stored

============================================================
✅ All tests completed!
============================================================
🎉 AI bill scanning is working perfectly!
```

## Before Running Tests

### 1. Install Tesseract OCR

**Windows:**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install to: `C:\Program Files\Tesseract-OCR`
3. Add to PATH
4. Verify: `tesseract --version`

**Linux:**
```bash
sudo apt-get install tesseract-ocr
```

**macOS:**
```bash
brew install tesseract
```

### 2. Get Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Add to `.env`:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

### 3. Start the Server

```bash
python -m uvicorn main:app --reload
```

Server should be running on http://localhost:8000

## Troubleshooting

### "Tesseract not found"
- Make sure Tesseract is installed
- Add Tesseract to your PATH
- Restart your terminal/IDE

### "GEMINI_API_KEY not found"
- Check `.env` file exists in `backend/` directory
- Verify the key is correct
- Restart the server after adding the key

### "Server is not running"
- Start server: `python -m uvicorn main:app --reload`
- Check it's running on port 8000
- Visit http://localhost:8000/docs to verify

### "AI processing failed"
- This is normal for some test cases
- Check the error message in the response
- The test script handles failures gracefully

## Manual Testing

You can also test manually with Postman:

1. **Register & Login** to get a JWT token
2. **Create a Group**
3. **Upload Bill:**
   ```
   POST http://localhost:8000/api/v1/expenses/bill
   Authorization: Bearer YOUR_TOKEN
   
   Form Data:
   - image: [Select a bill image]
   - group_id: YOUR_GROUP_ID
   ```

## Sample Bills

The test script creates a sample bill automatically. You can also:

1. **Create a text bill** and screenshot it
2. **Use a real receipt photo**
3. **Test with different qualities** (blurry, skewed, low light)

## Next Steps

After tests pass:
1. Try uploading real bill photos
2. Test error handling (bad images, no text)
3. Check the Swagger UI: http://localhost:8000/docs
4. Review logs for any issues

## Files

- `test_ai_setup.py` - Setup verification
- `test_bill_scanning.py` - Full API test
- `test_bill.png` - Sample bill (auto-generated, auto-deleted)
