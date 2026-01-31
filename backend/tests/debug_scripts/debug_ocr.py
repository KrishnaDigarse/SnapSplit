"""
Debug script to test OCR on a specific image.
"""
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

from app.ai.ocr import extract_text_from_image

# Test with the failed image
image_path = "uploads/bills/7be29d79-193b-450a-8563-c62b2e279be6.jpg"

print("=" * 60)
print("🔍 OCR Debug Test")
print("=" * 60)
print(f"\nTesting image: {image_path}")

try:
    ocr_text = extract_text_from_image(image_path)
    print(f"\n✅ OCR Success!")
    print(f"Extracted {len(ocr_text)} characters")
    print("\n--- OCR TEXT ---")
    print(ocr_text)
except Exception as e:
    print(f"\n❌ OCR Failed: {e}")
    import traceback
    traceback.print_exc()
