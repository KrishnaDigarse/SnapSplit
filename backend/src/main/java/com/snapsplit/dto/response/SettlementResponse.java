package com.snapsplit.dto.response;

import com.snapsplit.enums.PaymentMethod;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SettlementResponse {
    private UUID id;
    private UUID groupId;
    private UUID paidBy;
    private UUID paidTo;
    private BigDecimal amount;
    private PaymentMethod paymentMethod;
    private String note;
    private LocalDateTime createdAt;
}
