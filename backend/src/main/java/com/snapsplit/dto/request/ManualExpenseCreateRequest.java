package com.snapsplit.dto.request;

import com.snapsplit.enums.SplitType;
import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ManualExpenseCreateRequest {

    @NotNull(message = "Group ID is required")
    private UUID groupId;

    @NotEmpty(message = "Items are required")
    @Valid
    private List<ExpenseItemCreate> items;

    @NotEmpty(message = "Splits are required")
    @Valid
    private List<SplitCreate> splits;

    @NotNull(message = "Subtotal is required")
    @DecimalMin(value = "0.01", message = "Subtotal must be positive")
    @DecimalMax(value = "1000000", message = "Subtotal exceeds maximum allowed value")
    private BigDecimal subtotal;

    @DecimalMin(value = "0", message = "Tax cannot be negative")
    @DecimalMax(value = "100000", message = "Tax exceeds maximum allowed value")
    private BigDecimal tax;

    @NotNull(message = "Total amount is required")
    @DecimalMin(value = "0.01", message = "Total amount must be positive")
    @DecimalMax(value = "1000000", message = "Total amount exceeds maximum allowed value")
    private BigDecimal totalAmount;

    private String description;

    // ── Nested DTOs ──

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ExpenseItemCreate {

        @NotBlank(message = "Item name is required")
        @Size(max = 255, message = "Item name must be at most 255 characters")
        private String itemName;

        @Min(value = 1, message = "Quantity must be positive")
        @Max(value = 10000, message = "Quantity exceeds maximum allowed value")
        private int quantity = 1;

        @NotNull(message = "Price is required")
        @DecimalMin(value = "0.01", message = "Price must be positive")
        @DecimalMax(value = "1000000", message = "Price exceeds maximum allowed value")
        private BigDecimal price;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class SplitCreate {

        @NotNull(message = "User ID is required")
        private UUID userId;

        @NotNull(message = "Amount is required")
        @DecimalMin(value = "0", message = "Split amount cannot be negative")
        @DecimalMax(value = "1000000", message = "Split amount exceeds maximum allowed value")
        private BigDecimal amount;

        private SplitType splitType = SplitType.EQUAL;
    }
}
