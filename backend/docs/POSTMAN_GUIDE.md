# 📋 How to Use the Postman Collection for AI Bill Scanning

## Prerequisites
- Postman installed
- Backend server running (`python -m uvicorn main:app --reload`)
- A bill image ready (JPG/PNG format)

## Step-by-Step Instructions

### 1. Import the Collection
1. Open Postman
2. Click **Import** button (top left)
3. Select the file: `SnapSplit_AI_Bill_Scanning.postman_collection.json`
4. Click **Import**

### 2. Run the Requests in Order

#### Request 1: Register User
- Click **Send**
- Expected: 201 Created (or 400 if user exists - that's OK!)

#### Request 2: Login
- Click **Send**
- Expected: 200 OK
- ✅ The access token will be automatically saved to `{{access_token}}`

#### Request 3: Create Group
- Click **Send**
- Expected: 201 Created
- ✅ The group ID will be automatically saved to `{{group_id}}`

#### Request 4: Upload Bill Image (AI Processing) ⚠️ **IMPORTANT**
This is where you need to manually select your bill image:

1. In the request body, you'll see a form with two fields:
   - `image` (file)
   - `group_id` (text)

2. **For the `image` field:**
   - Click on the row where it says "image"
   - On the right side, you'll see a **"Select Files"** button
   - Click **"Select Files"**
   - Browse to your bill image (e.g., `c:\Users\krish\Documents\Project\SnapSplit\backend\sample_bill.png`)
   - Select the file

3. **Verify the file is selected:**
   - You should see the filename appear next to the "Select Files" button
   - The file path should be visible

4. Click **Send**
5. Expected: 201 Created
6. Processing time: 5-15 seconds

#### What to Check in the Response:
```json
{
  "id": "...",
  "status": "READY",  // Should be READY if successful
  "subtotal": "59.00",
  "tax": "10.62",
  "total_amount": "69.62",
  "raw_ocr_text": "SRI KRISHNA\nVeg Restaurant...",  // OCR extracted text
  "items": [
    {
      "item_name": "MEDU WADA",
      "price": "65.00",
      "quantity": 1
    }
  ]
}
```

#### Request 5: Get Expense Details
- Click **Send**
- Expected: 200 OK
- This retrieves the full expense with all details

## 🔍 Debugging Tips

### If you get 422 "Field required" error:
- **Cause:** The image file wasn't selected properly
- **Fix:** 
  1. Go back to Request 4
  2. Click on the `image` field
  3. Click **"Select Files"** button on the right
  4. Choose your bill image
  5. Make sure the filename appears
  6. Try again

### If you get 401 Unauthorized:
- **Cause:** Token expired or not set
- **Fix:** Re-run Request 2 (Login) to get a fresh token

### If you get 403 Forbidden ("You are not a member of this group"):
- **Cause:** You're using a `group_id` from a previous session with a different user
- **Fix:** 
  1. **Re-run Request 3 (Create Group)** to create a fresh group
  2. The new `group_id` will be automatically saved
  3. Then run Request 4 (Upload Bill) again
  4. This ensures the current logged-in user is the creator and member of the group

### Alternative Fix for 403:
- Clear all collection variables and start from Request 1 (Register/Login)
- Run all requests in sequence: 1 → 2 → 3 → 4

### If status is "FAILED":
- **Cause:** AI processing encountered an error
- **Fix:** Check the server logs for details
- Common issues:
  - OCR couldn't extract text (image quality too poor)
  - LLM couldn't parse the bill format
  - Validation failed (totals don't match)

## 📊 Console Output

The collection includes test scripts that log useful information to the Postman Console:

1. Open **Postman Console** (View → Show Postman Console)
2. Run Request 4 (Upload Bill)
3. Check the console for:
   - AI Processing Results
   - Raw OCR Text
   - Extracted Data
   - Status

## 🎯 Testing with Different Bills

Try uploading different types of bills:
1. Restaurant receipts
2. Grocery bills
3. Utility bills
4. Invoices

The AI will attempt to extract:
- Item names and prices
- Subtotal
- Tax
- Total amount

## 📝 Notes

- **Processing Time:** AI processing takes 5-15 seconds (synchronous)
- **File Size Limit:** 10MB maximum
- **Supported Formats:** JPG, JPEG, PNG
- **OCR Quality:** Better image quality = better extraction results
- **LLM Model:** Using Groq (llama-3.3-70b-versatile) for fast, accurate parsing

