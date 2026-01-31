"""
Debug a specific failing image to see what went wrong.
"""
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

from app.ai.ocr import extract_text_from_image
from app.ai.llm import extract_bill_data
from app.ai.parser import validate_bill_data
import json

# Test the failing image
image_path = "test_images/sample_bill.png"

print("=" * 60)
print("🔍 Debugging sample_bill.png")
print("=" * 60)

# Step 1: OCR
print("\n1️⃣ OCR...")
try:
    ocr_text = extract_text_from_image(image_path)
    print(f"✅ OCR Success: {len(ocr_text)} characters")
    print("\n--- OCR TEXT ---")
    print(ocr_text)
    print("\n" + "-" * 60)
except Exception as e:
    print(f"❌ OCR Failed: {e}")
    sys.exit(1)

# Step 2: LLM
print("\n2️⃣ LLM...")
try:
    llm_output = extract_bill_data(ocr_text)
    print(f"✅ LLM Success")
    print("\n--- LLM OUTPUT ---")
    # Convert to serializable format
    llm_json = {
        'items': [
            {
                'name': item.get('name', ''),
                'quantity': int(item.get('quantity', 1)),
                'price': float(item.get('price', 0))
            }
            for item in llm_output.get('items', [])
        ],
        'subtotal': float(llm_output.get('subtotal', 0)),
        'tax': float(llm_output.get('tax', 0)),
        'total': float(llm_output.get('total', 0))
    }
    print(json.dumps(llm_json, indent=2))
    print(f"\nItems extracted: {len(llm_output.get('items', []))}")
    print("\n" + "-" * 60)
except Exception as e:
    print(f"❌ LLM Failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 3: Validation
print("\n3️⃣ Validation...")

# Show what we're validating
print("\n--- PRE-VALIDATION CHECK ---")
print(f"Items from LLM: {len(llm_output.get('items', []))}")
if llm_output.get('items'):
    for i, item in enumerate(llm_output['items']):
        print(f"  Item {i+1}: {item.get('name')} - ${item.get('price')} x {item.get('quantity')}")
else:
    print("  ⚠️ No items returned by LLM!")

print(f"Subtotal: {llm_output.get('subtotal')}")
print(f"Tax: {llm_output.get('tax')}")
print(f"Total: {llm_output.get('total')}")
print("-" * 60)

try:
    validated_data = validate_bill_data(llm_output)
    print(f"✅ Validation Success!")
    print(f"Valid items: {len(validated_data['items'])}")
except Exception as e:
    print(f"❌ Validation Failed: {e}")
    import traceback
    traceback.print_exc()
