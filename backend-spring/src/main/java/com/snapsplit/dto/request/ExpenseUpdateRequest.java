package com.snapsplit.dto.request;

import jakarta.validation.Valid;
import jakarta.validation.constraints.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ExpenseUpdateRequest {

    private String description;

    @NotEmpty(message = "Items are required")
    @Valid
    private List<ManualExpenseCreateRequest.ExpenseItemCreate> items;

    @NotNull(message = "Subtotal is required")
    @DecimalMin(value = "0.01", message = "Subtotal must be positive")
    private BigDecimal subtotal;

    @DecimalMin(value = "0", message = "Tax cannot be negative")
    private BigDecimal tax;

    @NotNull(message = "Total amount is required")
    @DecimalMin(value = "0.01", message = "Total amount must be positive")
    private BigDecimal totalAmount;
}
