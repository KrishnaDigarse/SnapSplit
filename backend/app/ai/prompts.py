"""
LLM prompt templates for bill data extraction.

This module contains carefully crafted prompts for extracting structured data
from OCR text. The prompts are designed to be:
- Clear and unambiguous
- Enforce strict JSON output
- Handle edge cases
- Minimize hallucinations
"""

BILL_EXTRACTION_PROMPT = """You are a precise bill parser. Extract items, prices, subtotal, tax, and total from this receipt.

STRICT RULES:
1. Return ONLY valid JSON - no markdown, no code blocks, no explanations
2. Use this EXACT schema:
{{
  "items": [
    {{"name": "string", "quantity": number, "price": number}}
  ],
  "subtotal": number,
  "tax": number,
  "total": number
}}

3. If quantity is not specified, use 1
4. Prices must be numeric (remove currency symbols like $, ₹, etc.)
5. **IMPORTANT - Discount Handling:**
   - If there's a discount, use the NET TOTAL (after discount) as the subtotal
   - Example: Sub Total 100, Discount 10, Net Total 90 → use subtotal: 90
   - The formula should be: subtotal + tax = total
6. If you cannot extract a field, use 0 for numbers
7. Item names should be clean (no extra symbols or line numbers)
8. All numbers should be decimal format (e.g., 12.50 not 12,50)
9. Round to 2 decimal places

Receipt text:
{ocr_text}

JSON output:"""


BILL_EXTRACTION_PROMPT_WITH_EXAMPLES = """You are a precise bill parser. Extract items, prices, subtotal, tax, and total from this receipt.

STRICT RULES:
1. Return ONLY valid JSON - no markdown, no code blocks, no explanations
2. Prices must be numeric (remove currency symbols)
3. If quantity not specified, use 1
4. Ensure subtotal + tax ≈ total
5. Clean item names (remove line numbers, extra symbols)

EXAMPLE INPUT:
1. Burger         $12.00
2. Fries          $5.00
Subtotal:         $17.00
Tax (10%):        $1.70
Total:            $18.70

EXAMPLE OUTPUT:
{{"items":[{{"name":"Burger","quantity":1,"price":12.00}},{{"name":"Fries","quantity":1,"price":5.00}}],"subtotal":17.00,"tax":1.70,"total":18.70}}

Now extract from this receipt:
{ocr_text}

JSON output:"""


def get_extraction_prompt(ocr_text: str, include_examples: bool = False) -> str:
    """
    Get the bill extraction prompt with OCR text inserted.
    
    Args:
        ocr_text: Raw text extracted from bill image
        include_examples: Whether to include example input/output
        
    Returns:
        Complete prompt ready for LLM
    """
    if include_examples:
        return BILL_EXTRACTION_PROMPT_WITH_EXAMPLES.format(ocr_text=ocr_text)
    return BILL_EXTRACTION_PROMPT.format(ocr_text=ocr_text)


def get_retry_prompt(ocr_text: str, previous_error: str) -> str:
    """
    Get a retry prompt when LLM output was invalid.
    
    Args:
        ocr_text: Raw OCR text
        previous_error: Description of what was wrong with previous output
        
    Returns:
        Prompt with additional guidance
    """
    return f"""The previous attempt failed: {previous_error}

Please try again with extra care.

{BILL_EXTRACTION_PROMPT.format(ocr_text=ocr_text)}"""
