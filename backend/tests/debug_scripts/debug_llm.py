"""
Debug script to test LLM parsing on the extracted OCR text.
"""
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv()

from app.ai.llm import extract_bill_data

# OCR text from the failed bill
ocr_text = """RESTAURANT

osEt. AMER PALACE ,RATANPUR

Mevhangabad Roa, RatanPUr
"nope mnopaia2046
'State: ADKYA. PRADESH

pati No:oRTI735 1

Gime Stoward Table Cover
15:16 MAKON

snc: 996332

Description

veo wancua so 1129.00
Veo sweet CORN 1 219,00
DAL TADKA. 2 215.00
HERA RICE 1 145,00
PLAIN PAPAD 2 80.00
EARED VEG WITH 1270.00

i 265.00

'MUSHROOM NATTA
BUDTER TANDOOR 1-27.00
MISSI ROTI 1 30.00
GARLIC NAAN 1 45.00

'otal amount 1315.00
cost 2.56 2.58 32.08
saat 2.58 2.58 32.81

'Bill Amount 1381.00"""

print("=" * 60)
print("🔍 LLM Debug Test")
print("=" * 60)
print(f"\nOCR Text Length: {len(ocr_text)} characters")

try:
    bill_data = extract_bill_data(ocr_text)
    print(f"\n✅ LLM Success!")
    print("\n--- EXTRACTED DATA ---")
    import json
    print(json.dumps(bill_data, indent=2))
except Exception as e:
    print(f"\n❌ LLM Failed: {e}")
    import traceback
    traceback.print_exc()
