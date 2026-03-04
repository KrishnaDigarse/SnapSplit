package com.snapsplit.dto.request;

import com.snapsplit.enums.PaymentMethod;
import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SettlementCreateRequest {

    @NotNull(message = "Group ID is required")
    private UUID groupId;

    @NotNull(message = "Payee ID is required")
    private UUID paidTo;

    @NotNull(message = "Amount is required")
    @DecimalMin(value = "0.01", message = "Amount must be greater than 0")
    @DecimalMax(value = "1000000", message = "Settlement amount exceeds maximum allowed value")
    private BigDecimal amount;

    private PaymentMethod paymentMethod = PaymentMethod.CASH;

    @Size(max = 500, message = "Note must be at most 500 characters")
    private String note;
}
