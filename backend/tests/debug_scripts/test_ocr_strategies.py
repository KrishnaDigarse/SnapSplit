"""
Test OCR with different strategies on sample_bill.png
"""
import sys
sys.path.insert(0, '.')

import cv2
import pytesseract
from app.utils.image import preprocess_for_ocr

image_path = "test_images/sample_bill.png"

print("=" * 60)
print("🔍 OCR Strategy Comparison for sample_bill.png")
print("=" * 60)

# Strategy 1: Direct OCR
print("\n1️⃣ Strategy 1: Direct OCR (no preprocessing)")
try:
    text1 = pytesseract.image_to_string(image_path, lang='eng', config='--psm 6')
    print(f"Length: {len(text1)} characters")
    print("Preview:", text1[:200])
except Exception as e:
    print(f"Failed: {e}")

# Strategy 2: PSM 3
print("\n2️⃣ Strategy 2: Direct OCR with PSM 3")
try:
    text2 = pytesseract.image_to_string(image_path, lang='eng', config='--psm 3')
    print(f"Length: {len(text2)} characters")
    print("Preview:", text2[:200])
except Exception as e:
    print(f"Failed: {e}")

# Strategy 3: PSM 4
print("\n3️⃣ Strategy 3: Direct OCR with PSM 4")
try:
    text3 = pytesseract.image_to_string(image_path, lang='eng', config='--psm 4')
    print(f"Length: {len(text3)} characters")
    print("Preview:", text3[:200])
except Exception as e:
    print(f"Failed: {e}")

# Strategy 4: Preprocessed
print("\n4️⃣ Strategy 4: Preprocessed (no rotation)")
try:
    processed = preprocess_for_ocr(image_path, detect_rotation_enabled=False)
    text4 = pytesseract.image_to_string(processed, lang='eng', config='--psm 6')
    print(f"Length: {len(text4)} characters")
    print("Preview:", text4[:200])
except Exception as e:
    print(f"Failed: {e}")

# Strategy 5: Preprocessed with different PSM
print("\n5️⃣ Strategy 5: Preprocessed with PSM 3")
try:
    processed = preprocess_for_ocr(image_path, detect_rotation_enabled=False)
    text5 = pytesseract.image_to_string(processed, lang='eng', config='--psm 3')
    print(f"Length: {len(text5)} characters")
    print("Full text:")
    print(text5)
except Exception as e:
    print(f"Failed: {e}")

print("\n" + "=" * 60)
print("Best strategy will be used for final OCR")
print("=" * 60)
