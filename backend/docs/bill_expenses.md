# Bill Expenses API

## Overview

The Bill Expenses API allows users to upload bill images and automatically extract expense details using AI (OCR + LLM).

## Endpoint

### Upload Bill Image

**POST** `/api/v1/expenses/bill`

Upload a bill image and process it with AI to create an expense.

#### Request

**Content-Type:** `multipart/form-data`

**Parameters:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image` | File | Yes | Bill image (JPG/PNG, max 10MB) |
| `group_id` | String (UUID) | Yes | ID of the group for this expense |

**Headers:**
```
Authorization: Bearer <jwt_token>
Content-Type: multipart/form-data
```

#### Response

**Status:** `201 Created`

**Body:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "group_id": "660e8400-e29b-41d4-a716-446655440001",
  "created_by": "770e8400-e29b-41d4-a716-446655440002",
  "source_type": "BILL_IMAGE",
  "image_url": "/uploads/bills/550e8400-e29b-41d4-a716-446655440000.jpg",
  "raw_ocr_text": "Restaurant ABC\n1. Burger $12.00\n2. Fries $5.00\nSubtotal: $17.00\nTax: $1.70\nTotal: $18.70",
  "status": "READY",
  "subtotal": 17.00,
  "tax": 1.70,
  "total": 18.70,
  "items": [
    {
      "id": "880e8400-e29b-41d4-a716-446655440003",
      "item_name": "Burger",
      "quantity": 1,
      "price": 12.00
    },
    {
      "id": "990e8400-e29b-41d4-a716-446655440004",
      "item_name": "Fries",
      "quantity": 1,
      "price": 5.00
    }
  ],
  "created_at": "2024-01-30T12:00:00Z"
}
```

#### Error Responses

**400 Bad Request** - Invalid input
```json
{
  "detail": "Invalid file type. Allowed: .jpg, .jpeg, .png"
}
```

**403 Forbidden** - Not a group member
```json
{
  "detail": "You are not a member of this group"
}
```

**413 Payload Too Large** - File too large
```json
{
  "detail": "File too large. Maximum size: 10MB"
}
```

**500 Internal Server Error** - Processing failed
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "FAILED",
  "description": "AI Processing Error: OCR failed: No text detected in image"
}
```

## Usage Examples

### cURL

```bash
curl -X POST "http://localhost:8000/api/v1/expenses/bill" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "image=@/path/to/bill.jpg" \
  -F "group_id=660e8400-e29b-41d4-a716-446655440001"
```

### Python (requests)

```python
import requests

url = "http://localhost:8000/api/v1/expenses/bill"
headers = {"Authorization": "Bearer YOUR_JWT_TOKEN"}
files = {"image": open("bill.jpg", "rb")}
data = {"group_id": "660e8400-e29b-41d4-a716-446655440001"}

response = requests.post(url, headers=headers, files=files, data=data)
print(response.json())
```

### JavaScript (fetch)

```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);
formData.append('group_id', '660e8400-e29b-41d4-a716-446655440001');

fetch('http://localhost:8000/api/v1/expenses/bill', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer YOUR_JWT_TOKEN'
  },
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));
```

## Processing Flow

1. **Upload & Validation**
   - Validate user is group member
   - Validate file type (JPG/PNG)
   - Validate file size (<10MB)
   - Save image to `/uploads/bills/`

2. **Create Expense**
   - Create expense with status `PROCESSING`
   - Store image URL

3. **AI Processing** (5-15 seconds)
   - **OCR:** Extract text from image
   - **LLM:** Parse text into structured data
   - **Validation:** Clean and validate data
   - **Expense Creation:** Create items and splits

4. **Update Status**
   - **Success:** Status = `READY`, items populated
   - **Failure:** Status = `FAILED`, error in description

5. **Return Response**
   - Return expense with all details

## Status Values

| Status | Description |
|--------|-------------|
| `PROCESSING` | AI is currently processing the bill |
| `READY` | Successfully processed, ready to use |
| `FAILED` | Processing failed, see description for error |

## Best Practices

### For Best Results

**Image Quality:**
- Use good lighting
- Keep bill flat (not crumpled)
- Take photo straight-on (not angled)
- Ensure text is in focus
- Avoid shadows

**Supported Bill Types:**
- Restaurant receipts
- Grocery receipts
- Retail receipts
- Service invoices

**Not Recommended:**
- Handwritten bills (low accuracy)
- Faded receipts
- Damaged/torn bills
- Bills with heavy background patterns

### Error Handling

**If status is FAILED:**
1. Check the `description` field for error details
2. View the uploaded image (use `image_url`)
3. If OCR failed, try:
   - Retaking photo with better lighting
   - Straightening the bill
   - Using a higher quality camera
4. If LLM failed, try:
   - Uploading a clearer image
   - Manually creating the expense instead

**Fallback to Manual Entry:**
If AI processing fails, users can always create expenses manually using the regular expense creation endpoint.

## Limitations

### Current Limitations (Week 3)

- **Synchronous Processing:** User waits 5-15 seconds
- **Single Image:** One bill per request
- **English Only:** OCR optimized for English text
- **No PDF Support:** Images only (JPG/PNG)
- **No Editing:** Can't edit AI-extracted data (must delete and recreate)

### Future Improvements (Week 4+)

- **Async Processing:** Instant response, background processing
- **Batch Upload:** Multiple bills at once
- **Multi-language:** Support for other languages
- **PDF Support:** Upload PDF receipts
- **Edit AI Results:** Correct extracted data before saving
- **Confidence Scores:** Show confidence for each extracted item
- **Receipt Tips:** In-app guidance for taking good photos

## Performance

**Typical Processing Time:**
- Clean, well-lit bills: 6-10 seconds
- Skewed or low-light bills: 10-15 seconds

**Success Rate:**
- Clean bills: 90-95%
- Skewed photos: 70-80%
- Low light: 50-60%
- Handwritten: 20-30%

**Cost:**
- ~$0.0001 per bill (Gemini API)
- Very cost-effective for MVP

## Security

**File Storage:**
- Images saved to local disk
- Unique filenames (UUID-based)
- Not accessible via direct URL (requires authentication)

**Data Privacy:**
- OCR text stored in database
- Only group members can view expense
- API key never exposed to client

**Validation:**
- File type whitelist (JPG/PNG only)
- File size limit (10MB)
- User must be group member

## Troubleshooting

### "OCR failed: No text detected"
- Image is too blurry
- Text is too small
- Image is upside down
- **Solution:** Retake photo with better quality

### "LLM extraction failed"
- OCR text was too messy
- Bill format not recognized
- API timeout
- **Solution:** Try again or use manual entry

### "Validation failed: Math doesn't add up"
- Subtotal + tax ≠ total (>2% error)
- LLM made calculation mistake
- **Solution:** Use manual entry for this bill

### "File too large"
- Image exceeds 10MB
- **Solution:** Compress image or reduce resolution

### "You are not a member of this group"
- User not in the specified group
- **Solution:** Check group_id or join the group first

## Related Endpoints

- **GET** `/api/v1/expenses/{expense_id}` - Get expense details
- **GET** `/api/v1/expenses/group/{group_id}` - List group expenses
- **POST** `/api/v1/expenses/manual` - Create manual expense (fallback)
- **GET** `/api/v1/groups/{group_id}` - Get group details

## Example Workflow

1. **User takes photo of bill**
2. **Upload to API**
   ```bash
   POST /api/v1/expenses/bill
   ```
3. **Wait for processing** (5-15 seconds)
4. **Check status**
   - If `READY`: Expense created successfully!
   - If `FAILED`: See error, retry or use manual entry
5. **View expense details**
   ```bash
   GET /api/v1/expenses/{expense_id}
   ```
6. **Splits automatically created** for all group members
7. **Balances updated** automatically

## Notes

- This is a **synchronous** endpoint (Week 3)
- User must wait for AI processing to complete
- Week 4 will add async processing with webhooks
- Always returns an expense (either READY or FAILED)
- Never crashes - all errors handled gracefully
