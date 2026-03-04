package com.snapsplit.dto.response;

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
public class BalanceViewResponse {
    private List<GroupBalanceDetail> balances;
    private List<DebtDetail> debts;

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class GroupBalanceDetail {
        private UUID userId;
        private String userName;
        private BigDecimal totalPaid;
        private BigDecimal totalShare;
        private BigDecimal totalSettled;
        private BigDecimal netBalance;
        private LocalDateTime updatedAt;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class DebtDetail {
        private String fromUser;
        private String toUser;
        private BigDecimal amount;
    }
}
