"""
Tesseract configuration for pytesseract.

This file explicitly sets the Tesseract path to avoid PATH issues on Windows.
"""
import pytesseract
import os
import sys

# Common Tesseract installation paths on Windows
TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Tesseract-OCR\tesseract.exe",
]

def configure_tesseract():
    """
    Configure pytesseract to find Tesseract executable.
    
    This function checks common installation paths and sets pytesseract.tesseract_cmd
    if Tesseract is found.
    """
    # Check if tesseract is already in PATH
    try:
        pytesseract.get_tesseract_version()
        print("✅ Tesseract found in PATH")
        return True
    except:
        pass
    
    # Try common installation paths
    for path in TESSERACT_PATHS:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            print(f"✅ Tesseract configured at: {path}")
            
            # Verify it works
            try:
                version = pytesseract.get_tesseract_version()
                print(f"✅ Tesseract version: {version}")
                return True
            except Exception as e:
                print(f"❌ Found Tesseract at {path} but failed to run: {e}")
                continue
    
    # Not found
    print("❌ Tesseract not found in common locations")
    print("   Searched:")
    for path in TESSERACT_PATHS:
        print(f"   - {path}")
    print("\n   Please install Tesseract or set pytesseract.tesseract_cmd manually")
    return False


# Auto-configure on import
if sys.platform == "win32":
    configure_tesseract()
