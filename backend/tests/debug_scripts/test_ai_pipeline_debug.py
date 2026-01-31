"""
Quick test to debug AI pipeline stages.
"""
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()  # Load .env file

from app.ai.ocr import extract_text_from_image
from app.ai.llm import extract_bill_data
from app.ai.parser import validate_bill_data

# Test with the uploaded bill
image_path = "uploads/bills/ea8fe3c5-d512-49ca-9d63-8c4d1b02e303.png"

print("=" * 60)
print("🔍 AI Pipeline Debug Test")
print("=" * 60)

# Step 1: OCR
print("\n1️⃣ Testing OCR...")
try:
    ocr_text = extract_text_from_image(image_path)
    print(f"✅ OCR Success! Extracted {len(ocr_text)} characters")
    print("\n--- OCR TEXT ---")
    print(ocr_text[:500])  # First 500 chars
    print("..." if len(ocr_text) > 500 else "")
except Exception as e:
    print(f"❌ OCR Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 2: LLM
print("\n\n2️⃣ Testing LLM...")
try:
    bill_data = extract_bill_data(ocr_text)
    print(f"✅ LLM Success!")
    print("\n--- LLM OUTPUT ---")
    import json
    print(json.dumps(bill_data, indent=2))
except Exception as e:
    print(f"❌ LLM Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Validation
print("\n\n3️⃣ Testing Validation...")
try:
    validated_data = validate_bill_data(bill_data)
    print(f"✅ Validation Success!")
    print("\n--- VALIDATED DATA ---")
    print(json.dumps(validated_data, indent=2, default=str))
except Exception as e:
    print(f"❌ Validation Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n\n" + "=" * 60)
print("✅ All AI pipeline stages passed!")
print("=" * 60)
