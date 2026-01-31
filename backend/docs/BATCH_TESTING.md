# Batch Testing for AI Bill Scanning

This script processes all bill images in the `test_images/` folder and generates detailed result files.

## Setup

1. **Create test_images folder:**
   ```bash
   mkdir test_images
   ```

2. **Add your bill images:**
   - Copy bill images (JPG, PNG) to `test_images/`
   - Any number of images

3. **Run the batch test:**
   ```bash
   python batch_test_bills.py
   ```

## What It Does

For each image in `test_images/`, the script:

1. **Runs OCR** - Extracts text using Tesseract
2. **Runs LLM** - Parses bill data using Groq
3. **Validates** - Cleans and validates the data
4. **Saves Results** - Creates `{image_name}_results.txt`

## Output Files

Each result file contains:

### 📄 Raw OCR Text
- Complete text extracted from the image
- Character count

### 🤖 LLM Extracted Data
- JSON output from Groq
- Items, prices, quantities
- Subtotal, tax, total

### ✅ Validated & Cleaned Data
- Final validated data
- Invalid items removed
- Math corrections applied

### ❌ Errors (if any)
- Detailed error messages
- Stage where failure occurred

## Example Output

```
test_images/
├── bill1.jpg
├── bill1_results.txt          ← Generated
├── bill2.png
├── bill2_results.txt          ← Generated
└── receipt3.jpg
    └── receipt3_results.txt   ← Generated
```

## Console Output

The script shows real-time progress:

```
🧪 BATCH AI BILL SCANNING TEST
============================================================
Found 3 images to process

============================================================
Processing: bill1.jpg
============================================================
1️⃣ Running OCR...
✅ OCR Success: 425 characters
2️⃣ Running LLM...
✅ LLM Success: 8 items extracted
3️⃣ Running Validation...
✅ Validation Success: 8 valid items
💾 Results saved to: bill1_results.txt

... (continues for each image)

============================================================
📊 BATCH TEST SUMMARY
============================================================
Total Images: 3
✅ Successful: 2
❌ Failed: 1

✅ bill1.jpg
   Items: 8, Total: 245.50
✅ bill2.png
   Items: 5, Total: 125.00
❌ receipt3.jpg
   Error: OCR failed: No text detected
```

## Troubleshooting

### No images found
- Make sure images are in `test_images/` folder
- Check file extensions (JPG, JPEG, PNG)

### OCR fails
- Image quality too poor
- Text not readable
- Try with better quality image

### LLM fails
- Check GROQ_API_KEY in `.env`
- OCR text might be too messy
- Check rate limits

### Validation fails
- Math doesn't add up (subtotal + tax ≠ total)
- No valid items found
- Check the LLM output in results file

## Tips for Best Results

1. **Good Image Quality**
   - Clear, well-lit photos
   - Text is horizontal
   - High resolution

2. **Supported Bill Types**
   - Restaurant receipts
   - Grocery bills
   - Retail invoices
   - Any printed bill with items and prices

3. **Batch Size**
   - Process 10-20 images at a time
   - Groq free tier: 30 requests/minute
   - Each image = 1 request

## Next Steps

After reviewing results:
1. Check which images failed
2. Improve image quality if needed
3. Review LLM output for accuracy
4. Use validated data for your application
