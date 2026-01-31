"""
Test the complete AI pipeline with the actual bill image.
"""
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

from app.ai.ocr import extract_text_from_image
from app.ai.llm import extract_bill_data
from app.ai.parser import validate_bill_data

# Test with the food bill
image_path = "uploads/bills/e387d52c-0bc1-442d-9934-6a25155b0cf2.jpg"

print("=" * 60)
print("🔍 Complete AI Pipeline Test")
print("=" * 60)

# Step 1: OCR
print("\n1️⃣ Testing OCR...")
try:
    ocr_text = extract_text_from_image(image_path)
    print(f"✅ OCR Success! Extracted {len(ocr_text)} characters")
except Exception as e:
    print(f"❌ OCR Failed: {e}")
    sys.exit(1)

# Step 2: LLM
print("\n2️⃣ Testing LLM...")
try:
    bill_data = extract_bill_data(ocr_text)
    print(f"✅ LLM Success!")
    print(f"\n--- LLM OUTPUT ---")
    import json
    print(json.dumps(bill_data, indent=2))
except Exception as e:
    print(f"❌ LLM Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Validation
print("\n3️⃣ Testing Validation...")
try:
    validated_data = validate_bill_data(bill_data)
    print(f"✅ Validation Success!")
    print(f"\n--- VALIDATED DATA ---")
    print(json.dumps(validated_data, indent=2))
except Exception as e:
    print(f"❌ Validation Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ All AI pipeline stages passed!")
print("=" * 60)
