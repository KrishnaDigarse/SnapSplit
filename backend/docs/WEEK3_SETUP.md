# Week 3 AI Integration - Setup Guide

## Prerequisites

### 1. Tesseract OCR Installation

Tesseract is required for OCR text extraction. Install it based on your OS:

#### Windows
1. Download Tesseract installer from: https://github.com/UB-Mannheim/tesseract/wiki
2. Run the installer (recommended: `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)
3. During installation, note the installation path (default: `C:\Program Files\Tesseract-OCR`)
4. Add Tesseract to PATH:
   - Open System Properties → Environment Variables
   - Edit PATH variable
   - Add: `C:\Program Files\Tesseract-OCR`
5. Verify installation:
   ```bash
   tesseract --version
   ```

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

#### macOS
```bash
brew install tesseract
```

### 2. Google Gemini API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the API key
4. Add to `.env` file:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

## Installation Steps

### 1. Install Python Dependencies

```bash
cd backend
.\venv\Scripts\Activate.ps1  # Windows
# or
source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

This will install:
- `opencv-python` - Image preprocessing
- `pytesseract` - OCR wrapper
- `google-generativeai` - Gemini API client
- `pillow` - Image handling
- `tenacity` - Retry logic

### 2. Configure Environment Variables

Add to `backend/.env`:

```env
# Existing variables
DATABASE_URL=sqlite:///./snapsplit.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# New: Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here

# Optional: Upload configuration
UPLOAD_DIR=./uploads/bills
MAX_IMAGE_SIZE_MB=10
```

### 3. Create Upload Directory

```bash
mkdir -p uploads/bills
```

### 4. Verify Installation

Run this test script:

```python
# test_ai_setup.py
import cv2
import pytesseract
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing AI setup...")

# Test 1: OpenCV
print("\n1. OpenCV:", cv2.__version__)

# Test 2: Tesseract
try:
    version = pytesseract.get_tesseract_version()
    print(f"2. Tesseract: {version}")
except Exception as e:
    print(f"2. Tesseract: ERROR - {e}")
    print("   Make sure Tesseract is installed and in PATH")

# Test 3: Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    print("3. Gemini API Key: Found")
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say 'API working'")
        print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ERROR: {e}")
else:
    print("3. Gemini API Key: NOT FOUND")
    print("   Add GEMINI_API_KEY to .env file")

print("\nSetup verification complete!")
```

Run it:
```bash
python test_ai_setup.py
```

Expected output:
```
Testing AI setup...

1. OpenCV: 4.9.0
2. Tesseract: 5.3.3
3. Gemini API Key: Found
   Response: API working

Setup verification complete!
```

## Testing the API

### 1. Start the Server

```bash
cd backend
python -m uvicorn main:app --reload
```

Server should start on: http://localhost:8000

### 2. Test with Postman

#### Step 1: Register and Login
1. Register a user (User 1)
2. Login to get JWT token
3. Save token as `{{token}}`

#### Step 2: Create a Group
```
POST http://localhost:8000/api/v1/groups
Authorization: Bearer {{token}}

{
  "name": "Test Group"
}
```

Save `group_id` from response.

#### Step 3: Upload Bill Image

```
POST http://localhost:8000/api/v1/expenses/bill
Authorization: Bearer {{token}}
Content-Type: multipart/form-data

image: [Select a bill image file]
group_id: {{group_id}}
```

**Note:** This will take 5-15 seconds to process.

#### Step 4: Check Response

**Success (status: READY):**
```json
{
  "id": "...",
  "status": "READY",
  "items": [
    {"item_name": "Burger", "quantity": 1, "price": 12.00}
  ],
  "subtotal": 12.00,
  "tax": 1.20,
  "total": 13.20
}
```

**Failure (status: FAILED):**
```json
{
  "id": "...",
  "status": "FAILED",
  "description": "AI Processing Error: OCR failed: No text detected"
}
```

### 3. Test with cURL

```bash
# Get token first
TOKEN="your_jwt_token_here"
GROUP_ID="your_group_id_here"

# Upload bill
curl -X POST "http://localhost:8000/api/v1/expenses/bill" \
  -H "Authorization: Bearer $TOKEN" \
  -F "image=@path/to/bill.jpg" \
  -F "group_id=$GROUP_ID"
```

## Sample Test Bills

Create test bills for different scenarios:

### Test 1: Clean Bill (High Success Rate)
Create a simple text file and screenshot it:
```
Restaurant ABC
123 Main St

1. Burger         $12.00
2. Fries          $5.00
3. Soda           $3.00

Subtotal:         $20.00
Tax (10%):        $2.00
Total:            $22.00

Thank you!
```

### Test 2: Real Receipt Photo
- Take a photo of a real receipt
- Ensure good lighting
- Keep bill flat
- Photo straight-on

### Test 3: Challenging Photo
- Skewed angle
- Low light
- Crumpled bill

## Troubleshooting

### "Tesseract not found"
**Error:** `TesseractNotFoundError`

**Solution:**
1. Install Tesseract (see Prerequisites)
2. Add to PATH
3. Restart terminal/IDE
4. Verify: `tesseract --version`

### "GEMINI_API_KEY not set"
**Error:** `ValueError: GEMINI_API_KEY environment variable not set`

**Solution:**
1. Get API key from https://makersuite.google.com/app/apikey
2. Add to `.env`: `GEMINI_API_KEY=your_key`
3. Restart server

### "OCR failed: No text detected"
**Cause:** Image is too blurry or no text visible

**Solution:**
- Use better quality image
- Ensure good lighting
- Keep bill flat
- Take photo straight-on

### "LLM extraction failed"
**Cause:** API error or invalid response

**Solution:**
- Check internet connection
- Verify API key is valid
- Check Gemini API quota
- Try again (has retry logic)

### "File too large"
**Error:** `413 Payload Too Large`

**Solution:**
- Compress image
- Reduce resolution
- Maximum size: 10MB

### Server won't start
**Error:** Import errors

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check for circular imports
python -c "from app.routes import ai_expenses; print('OK')"
```

## Performance Tips

### For Faster Processing
1. **Use smaller images** (resize to 1500px width max)
2. **Preprocess images** before upload (already done automatically)
3. **Use good quality photos** (reduces retry attempts)

### For Better Accuracy
1. **Good lighting** - Natural light or bright indoor lighting
2. **Flat bill** - No wrinkles or folds
3. **Straight angle** - Photo taken from directly above
4. **Clean background** - Plain surface, no patterns
5. **Focus** - Ensure text is sharp and readable

## Next Steps

After setup is complete:

1. ✅ Test with sample bills
2. ✅ Verify all statuses (PROCESSING → READY/FAILED)
3. ✅ Check expense items created correctly
4. ✅ Verify splits generated for group members
5. ✅ Test error handling (bad images, no text, etc.)
6. ✅ Review logs for any issues
7. ✅ Update Postman collection with new endpoint

## Week 4 Preview

Future improvements:
- Async processing with Celery
- Webhook notifications
- Batch bill upload
- PDF support
- Multi-language OCR
- Manual correction UI
- Confidence scores

## Support

If you encounter issues:
1. Check logs: Server console output
2. Check expense description for error details
3. View uploaded image to verify quality
4. Try with a different bill image
5. Fall back to manual expense creation

## Resources

- Tesseract: https://github.com/tesseract-ocr/tesseract
- Gemini API: https://ai.google.dev/
- OpenCV: https://opencv.org/
- API Docs: http://localhost:8000/docs
