package com.snapsplit.ai;

/**
 * LLM prompt templates — equivalent to Python's ai/prompts.py
 */
public final class BillPrompts {

    private BillPrompts() {
    }

    private static final String EXTRACTION_TEMPLATE = """
            You are a precise bill parser. Extract items, prices, subtotal, tax, and total from this receipt.

            STRICT RULES:
            1. Return ONLY valid JSON - no markdown, no code blocks, no explanations
            2. Use this EXACT schema:
            {
              "items": [
                {"name": "string", "quantity": number, "price": number}
              ],
              "subtotal": number,
              "tax": number,
              "total": number
            }

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
            %s

            JSON output:""";

    public static String getExtractionPrompt(String ocrText) {
        return String.format(EXTRACTION_TEMPLATE, ocrText);
    }
}
