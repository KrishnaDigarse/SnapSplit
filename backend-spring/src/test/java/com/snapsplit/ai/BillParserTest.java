package com.snapsplit.ai;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import java.math.BigDecimal;
import java.util.*;

import static org.assertj.core.api.Assertions.*;

class BillParserTest {

    private BillParser parser;

    @BeforeEach
    void setUp() {
        parser = new BillParser();
    }

    @Nested
    @DisplayName("validateBillData()")
    class ValidateTests {

        @Test
        @DisplayName("should validate correct bill data")
        void validate_success() {
            Map<String, Object> data = new LinkedHashMap<>();
            data.put("items", List.of(
                    Map.of("name", "Burger", "quantity", 1, "price", 12.00),
                    Map.of("name", "Fries", "quantity", 2, "price", 5.00)));
            data.put("subtotal", 22.00);
            data.put("tax", 2.20);
            data.put("total", 24.20);

            Map<String, Object> result = parser.validateBillData(data);

            assertThat(result.get("subtotal")).isEqualTo(new BigDecimal("22.00"));
            assertThat(result.get("tax")).isEqualTo(new BigDecimal("2.20"));
            assertThat(result.get("total")).isEqualTo(new BigDecimal("24.20"));
            assertThat((List<?>) result.get("items")).hasSize(2);
        }

        @Test
        @DisplayName("should auto-correct total within tolerance")
        void validate_autoCorrect() {
            Map<String, Object> data = new LinkedHashMap<>();
            data.put("items", List.of(Map.of("name", "Item", "quantity", 1, "price", 10.00)));
            data.put("subtotal", 10.00);
            data.put("tax", 1.00);
            data.put("total", 11.05); // slightly off

            Map<String, Object> result = parser.validateBillData(data);

            // Should auto-correct total to subtotal + tax = 11.00
            assertThat((BigDecimal) result.get("total")).isEqualByComparingTo("11.00");
        }

        @Test
        @DisplayName("should throw on missing field")
        void validate_missingField() {
            Map<String, Object> data = Map.of("items", List.of(), "subtotal", 10);

            assertThatThrownBy(() -> parser.validateBillData(data))
                    .isInstanceOf(BillParser.ValidationException.class)
                    .hasMessageContaining("Missing required field");
        }

        @Test
        @DisplayName("should throw when no valid items")
        void validate_noValidItems() {
            Map<String, Object> data = new LinkedHashMap<>();
            data.put("items", List.of(
                    Map.of("name", "", "quantity", 1, "price", 10.00) // empty name
            ));
            data.put("subtotal", 10.00);
            data.put("tax", 0);
            data.put("total", 10.00);

            assertThatThrownBy(() -> parser.validateBillData(data))
                    .isInstanceOf(BillParser.ValidationException.class)
                    .hasMessageContaining("No valid items");
        }

        @Test
        @DisplayName("should throw when math error exceeds tolerance")
        void validate_mathError() {
            Map<String, Object> data = new LinkedHashMap<>();
            data.put("items", List.of(Map.of("name", "Item", "quantity", 1, "price", 10.00)));
            data.put("subtotal", 10.00);
            data.put("tax", 1.00);
            data.put("total", 15.00); // way off

            assertThatThrownBy(() -> parser.validateBillData(data))
                    .isInstanceOf(BillParser.ValidationException.class)
                    .hasMessageContaining("Math validation failed");
        }

        @Test
        @DisplayName("should handle currency symbols in values")
        void validate_currencySymbols() {
            Map<String, Object> data = new LinkedHashMap<>();
            data.put("items", List.of(Map.of("name", "Coffee", "quantity", 1, "price", "$4.50")));
            data.put("subtotal", "$4.50");
            data.put("tax", "$0.45");
            data.put("total", "$4.95");

            Map<String, Object> result = parser.validateBillData(data);

            assertThat((BigDecimal) result.get("subtotal")).isEqualByComparingTo("4.50");
            assertThat((BigDecimal) result.get("total")).isEqualByComparingTo("4.95");
        }

        @Test
        @DisplayName("should skip items with invalid price")
        void validate_skipInvalidPriceItems() {
            Map<String, Object> data = new LinkedHashMap<>();
            data.put("items", List.of(
                    Map.of("name", "Good", "quantity", 1, "price", 10.00),
                    Map.of("name", "Bad", "quantity", 1, "price", -5.00)));
            data.put("subtotal", 10.00);
            data.put("tax", 0);
            data.put("total", 10.00);

            Map<String, Object> result = parser.validateBillData(data);
            assertThat((List<?>) result.get("items")).hasSize(1);
        }

        @Test
        @DisplayName("should default quantity to 1 if missing")
        void validate_defaultQuantity() {
            Map<String, Object> data = new LinkedHashMap<>();
            data.put("items", List.of(Map.of("name", "Item", "price", 10.00)));
            data.put("subtotal", 10.00);
            data.put("tax", 0);
            data.put("total", 10.00);

            Map<String, Object> result = parser.validateBillData(data);
            @SuppressWarnings("unchecked")
            Map<String, Object> item = ((List<Map<String, Object>>) result.get("items")).get(0);
            assertThat(item.get("quantity")).isEqualTo(1);
        }
    }
}
