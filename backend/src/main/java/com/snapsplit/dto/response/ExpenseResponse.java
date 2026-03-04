package com.snapsplit.dto.response;

import com.snapsplit.enums.SplitType;
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
public class ExpenseResponse {
    private UUID id;
    private UUID groupId;
    private UUID createdBy;
    private String creatorName;
    private String sourceType;
    private String status;
    private Boolean isEdited;
    private BigDecimal subtotal;
    private BigDecimal tax;
    private BigDecimal totalAmount;
    private LocalDateTime createdAt;
    private List<ExpenseItemResponse> items;
    private String rawOcrText;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class ExpenseItemResponse {
        private UUID id;
        private UUID expenseId;
        private String itemName;
        private Integer quantity;
        private BigDecimal price;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class SplitResponse {
        private UUID id;
        private UUID expenseItemId;
        private UUID userId;
        private BigDecimal amount;
        private SplitType splitType;
    }
}
