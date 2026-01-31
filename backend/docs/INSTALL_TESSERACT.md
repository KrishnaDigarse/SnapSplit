# ⚠️ IMPORTANT: Tesseract OCR Installation Required

## The Issue

The test failed because **Tesseract OCR** is not installed on your system. This is a **required external binary** that cannot be installed via pip.

## Quick Fix (Windows)

### Option 1: Download Installer (Recommended)

1. **Download Tesseract:**
   - Go to: https://github.com/UB-Mannheim/tesseract/wiki
   - Download: `tesseract-ocr-w64-setup-5.3.3.20231005.exe` (or latest version)

2. **Install:**
   - Run the installer
   - **IMPORTANT:** During installation, note the path (default: `C:\Program Files\Tesseract-OCR`)
   - Make sure to check "Add to PATH" if the option is available

3. **Add to PATH manually (if needed):**
   - Open System Properties → Environment Variables
   - Edit "Path" variable
   - Add: `C:\Program Files\Tesseract-OCR`
   - Click OK

4. **Verify Installation:**
   ```bash
   # Open a NEW terminal (important!)
   tesseract --version
   ```
   
   You should see:
   ```
   tesseract 5.3.3
   ```

5. **Run the test again:**
   ```bash
   cd backend
   python test_ai_setup.py
   ```

### Option 2: Use Chocolatey (if you have it)

```bash
choco install tesseract
```

## Alternative: Test Without OCR

If you want to test the API without installing Tesseract, you can:

1. **Skip the setup test** and go straight to manual testing with Postman
2. **Mock the OCR** for now (not recommended for production)

## After Installing Tesseract

Once Tesseract is installed, run:

```bash
# 1. Verify setup
python test_ai_setup.py

# 2. If all checks pass, run full test
python test_bill_scanning.py
```

## Why Tesseract is Required

- Tesseract is an **external OCR engine** (not a Python package)
- It's used to extract text from bill images
- The `pytesseract` Python package is just a wrapper that calls the Tesseract binary
- Without Tesseract installed, OCR will fail

## Current Status

✅ Python packages installed (opencv, pytesseract, etc.)
✅ Gemini API key configured
✅ Server running
❌ **Tesseract OCR binary not installed** ← You are here

## Next Steps

1. Install Tesseract (see instructions above)
2. Restart your terminal
3. Run `tesseract --version` to verify
4. Run `python test_ai_setup.py` again
5. If all checks pass, run `python test_bill_scanning.py`

---

**Need help?** Check the full setup guide: [WEEK3_SETUP.md](file:///c:/Users/krish/Documents/Project/SnapSplit/backend/docs/WEEK3_SETUP.md)
