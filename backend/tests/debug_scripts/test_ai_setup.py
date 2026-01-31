"""
Simple setup verification script.

Run this first to verify all prerequisites are installed correctly.
"""
import os
import sys


def test_opencv():
    """Test OpenCV installation."""
    try:
        import cv2
        print(f"✅ OpenCV: {cv2.__version__}")
        return True
    except ImportError:
        print("❌ OpenCV not installed")
        print("   Install: pip install opencv-python")
        return False


def test_pytesseract():
    """Test Tesseract OCR installation."""
    try:
        import pytesseract
        
        # Try to auto-configure Tesseract on Windows
        try:
            import sys
            if sys.platform == "win32":
                from app.ai import tesseract_config
        except:
            pass
        
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR: {version}")
        return True
    except ImportError:
        print("❌ pytesseract not installed")
        print("   Install: pip install pytesseract")
        return False
    except Exception as e:
        print(f"❌ Tesseract OCR not found: {e}")
        print("   Install Tesseract binary:")
        print("   Windows: https://github.com/UB-Mannheim/tesseract/wiki")
        print("   Linux: sudo apt-get install tesseract-ocr")
        print("   Mac: brew install tesseract")
        return False


def test_gemini():
    """Test Gemini API setup."""
    try:
        import google.generativeai as genai
        print("✅ google-generativeai package installed")
        
        # Check for API key
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            print("✅ GEMINI_API_KEY found in .env")
            
            # Test API connection
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                response = model.generate_content("Say 'API working'")
                print(f"✅ Gemini API connection successful")
                print(f"   Response: {response.text}")
                return True
            except Exception as e:
                print(f"❌ Gemini API error: {e}")
                print("   Check your API key is valid")
                return False
        else:
            print("❌ GEMINI_API_KEY not found in .env")
            print("   Get API key from: https://makersuite.google.com/app/apikey")
            print("   Add to .env: GEMINI_API_KEY=your_key_here")
            return False
            
    except ImportError:
        print("❌ google-generativeai not installed")
        print("   Install: pip install google-generativeai")
        return False


def test_pillow():
    """Test Pillow installation."""
    try:
        from PIL import Image
        print("✅ Pillow (PIL) installed")
        return True
    except ImportError:
        print("❌ Pillow not installed")
        print("   Install: pip install pillow")
        return False


def test_tenacity():
    """Test tenacity installation."""
    try:
        import tenacity
        print("✅ tenacity installed")
        return True
    except ImportError:
        print("❌ tenacity not installed")
        print("   Install: pip install tenacity")
        return False


def test_server():
    """Test if server is running."""
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running on http://localhost:8000")
            return True
        else:
            print(f"⚠️  Server returned status {response.status_code}")
            return False
    except ImportError:
        print("❌ requests not installed")
        print("   Install: pip install requests")
        return False
    except Exception:
        print("❌ Server is not running")
        print("   Start with: python -m uvicorn main:app --reload")
        return False


def main():
    """Run all setup tests."""
    print("=" * 60)
    print("🔍 SnapSplit AI Setup Verification")
    print("=" * 60)
    print()
    
    results = []
    
    print("Testing Python packages...")
    print("-" * 60)
    results.append(test_opencv())
    results.append(test_pytesseract())
    results.append(test_gemini())
    results.append(test_pillow())
    results.append(test_tenacity())
    
    print()
    print("Testing server...")
    print("-" * 60)
    results.append(test_server())
    
    print()
    print("=" * 60)
    
    if all(results):
        print("✅ All setup checks passed!")
        print()
        print("You're ready to test bill scanning:")
        print("  python test_bill_scanning.py")
        return 0
    else:
        print("❌ Some setup checks failed")
        print()
        print("Please fix the issues above and try again.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
