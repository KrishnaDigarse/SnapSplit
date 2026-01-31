# Tesseract Not Recognized - Quick Fix Guide

## Problem
You installed Tesseract but Python can't find it.

## Solution 1: Manual Path Configuration (Quickest)

If Tesseract is installed but not in PATH, tell me where you installed it and I'll configure it.

**Common locations:**
- `C:\Program Files\Tesseract-OCR\tesseract.exe`
- `C:\Program Files (x86)\Tesseract-OCR\tesseract.exe`
- `C:\Tesseract-OCR\tesseract.exe`

**To find it:**
1. Open File Explorer
2. Search for `tesseract.exe`
3. Note the full path

Then I can add it to the configuration.

## Solution 2: Add to PATH (Permanent)

1. **Find Tesseract installation folder** (e.g., `C:\Program Files\Tesseract-OCR`)

2. **Add to PATH:**
   - Press `Win + X` → System
   - Click "Advanced system settings"
   - Click "Environment Variables"
   - Under "System variables", find "Path"
   - Click "Edit"
   - Click "New"
   - Add: `C:\Program Files\Tesseract-OCR`
   - Click OK on all windows

3. **Restart terminal** (IMPORTANT!)
   - Close all PowerShell/CMD windows
   - Open a new terminal
   - Test: `tesseract --version`

## Solution 3: Reinstall with PATH Option

1. Uninstall Tesseract
2. Download again from: https://github.com/UB-Mannheim/tesseract/wiki
3. During installation, **check "Add to PATH"** option
4. Restart terminal

## Quick Test

After any solution, test with:
```bash
# In a NEW terminal
tesseract --version
```

Should show:
```
tesseract 5.3.3
```

Then run:
```bash
cd backend
python test_ai_setup.py
```

## Still Not Working?

If none of these work, you can manually set the path in code. Tell me:
1. Where did you install Tesseract? (full path to tesseract.exe)
2. Did you restart your terminal after installation?

I'll configure it for you!
