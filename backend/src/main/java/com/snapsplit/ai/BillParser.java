package com.snapsplit.ai;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.*;

/**
 * Bill data parser and validator — equivalent to Python's ai/parser.py
 *
 * Validates LLM output: schema check, number coercion, item cleanup,
 * math validation with auto-correction (subtotal + tax ≈ total).
 */
@Slf4j
@Component
public class BillParser {

    private static final BigDecimal TOLERANCE_PERCENT = new BigDecimal("2.0");

    /**
     * Validate and clean LLM-extracted bill data.
     * Python equivalent: validate_bill_data()
     */
    @SuppressWarnings("unchecked")
    public Map<String, Object> validateBillData(Map<String, Object> data) {
        log.info("Validating bill data");

        // Step 1: Validate schema
        for (String field : List.of("items", "subtotal", "tax", "total")) {
            if (!data.containsKey(field)) {
                throw new ValidationException("Missing required field: " + field);
            }
        }

        if (!(data.get("items") instanceof List)) {
            throw new ValidationException("'items' must be a list");
        }

        // Step 2: Coerce numbers
        BigDecimal subtotal = toDecimal(data.get("subtotal"), "subtotal");
        BigDecimal tax = toDecimal(data.get("tax"), "tax");
        BigDecimal total = toDecimal(data.get("total"), "total");

        // Step 3: Clean items
        List<Map<String, Object>> rawItems = (List<Map<String, Object>>) data.get("items");
        List<Map<String, Object>> cleanedItems = cleanItems(rawItems);

        if (cleanedItems.isEmpty()) {
            throw new ValidationException("No valid items found in bill");
        }

        // Step 4: Validate math (subtotal + tax ≈ total)
        BigDecimal expectedTotal = subtotal.add(tax);
        BigDecimal difference = expectedTotal.subtract(total).abs();

        if (total.compareTo(BigDecimal.ZERO) > 0) {
            BigDecimal errorPercent = difference.multiply(new BigDecimal("100"))
                    .divide(total, 2, RoundingMode.HALF_UP);

            if (errorPercent.compareTo(TOLERANCE_PERCENT) <= 0) {
                if (difference.compareTo(BigDecimal.ZERO) > 0) {
                    log.info("Auto-correcting total: {} -> {} (error: {}%)", total, expectedTotal, errorPercent);
                    total = expectedTotal;
                }
            } else {
                throw new ValidationException(String.format(
                        "Math validation failed: subtotal (%s) + tax (%s) = %s, but total is %s. Difference: %s (%.2f%%)",
                        subtotal, tax, expectedTotal, total, difference, errorPercent));
            }
        }

        log.info("Validation successful: {} items, total: {}", cleanedItems.size(), total);

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("items", cleanedItems);
        result.put("subtotal", subtotal);
        result.put("tax", tax);
        result.put("total", total);
        return result;
    }

    private BigDecimal toDecimal(Object value, String fieldName) {
        try {
            String str = String.valueOf(value)
                    .replace("$", "").replace("₹", "").replace(",", "").trim();
            return new BigDecimal(str).setScale(2, RoundingMode.HALF_UP);
        } catch (NumberFormatException e) {
            log.warn("Could not convert {}='{}' to Decimal, using 0", fieldName, value);
            return BigDecimal.ZERO.setScale(2, RoundingMode.HALF_UP);
        }
    }

    @SuppressWarnings("unchecked")
    private List<Map<String, Object>> cleanItems(List<Map<String, Object>> items) {
        List<Map<String, Object>> valid = new ArrayList<>();

        for (int i = 0; i < items.size(); i++) {
            Map<String, Object> item = items.get(i);

            if (!item.containsKey("name") || item.get("name") == null || item.get("name").toString().isBlank()) {
                log.warn("Item {} missing name, skipping", i);
                continue;
            }
            if (!item.containsKey("price")) {
                log.warn("Item {} missing price, skipping", i);
                continue;
            }

            BigDecimal price = toDecimal(item.get("price"), "price");
            int quantity = toInt(item.getOrDefault("quantity", 1));

            if (price.compareTo(BigDecimal.ZERO) <= 0) {
                log.warn("Item {} has invalid price {}, skipping", i, price);
                continue;
            }
            if (quantity <= 0) {
                log.warn("Item {} has invalid quantity {}, skipping", i, quantity);
                continue;
            }

            Map<String, Object> cleaned = new LinkedHashMap<>();
            cleaned.put("name", item.get("name").toString().trim());
            cleaned.put("quantity", quantity);
            cleaned.put("price", price);
            valid.add(cleaned);
        }

        log.info("Cleaned items: {}/{} valid", valid.size(), items.size());
        return valid;
    }

    private int toInt(Object value) {
        try {
            return (int) Double.parseDouble(String.valueOf(value));
        } catch (NumberFormatException e) {
            return 1;
        }
    }

    public static class ValidationException extends RuntimeException {
        public ValidationException(String message) {
            super(message);
        }
    }
}
