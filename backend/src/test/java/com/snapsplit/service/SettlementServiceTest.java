package com.snapsplit.service;

import com.snapsplit.dto.request.SettlementCreateRequest;
import com.snapsplit.dto.response.SettlementResponse;
import com.snapsplit.entity.*;
import com.snapsplit.enums.PaymentMethod;
import com.snapsplit.exception.BadRequestException;
import com.snapsplit.repository.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.math.BigDecimal;
import java.util.UUID;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class SettlementServiceTest {

    @Mock
    private SettlementRepository settlementRepository;
    @Mock
    private GroupMemberRepository groupMemberRepository;
    @Mock
    private BalanceService balanceService;
    @InjectMocks
    private SettlementService settlementService;

    private UserEntity payer;
    private UserEntity payee;
    private UUID groupId;

    @BeforeEach
    void setUp() {
        payer = UserEntity.builder().id(UUID.randomUUID()).name("Payer").build();
        payee = UserEntity.builder().id(UUID.randomUUID()).name("Payee").build();
        groupId = UUID.randomUUID();
    }

    @Nested
    @DisplayName("createSettlement()")
    class CreateTests {
        @Test
        @DisplayName("should create settlement successfully")
        void create_success() {
            SettlementCreateRequest req = new SettlementCreateRequest();
            req.setGroupId(groupId);
            req.setPaidTo(payee.getId());
            req.setAmount(new BigDecimal("50.00"));
            req.setPaymentMethod(PaymentMethod.CASH);

            when(groupMemberRepository.existsByGroupIdAndUserId(groupId, payer.getId())).thenReturn(true);
            when(groupMemberRepository.existsByGroupIdAndUserId(groupId, payee.getId())).thenReturn(true);
            when(settlementRepository.save(any())).thenAnswer(inv -> {
                SettlementEntity s = inv.getArgument(0);
                s.setId(UUID.randomUUID());
                return s;
            });
            doNothing().when(balanceService).updateGroupBalances(groupId);

            SettlementResponse resp = settlementService.createSettlement(payer, req);

            assertThat(resp.getAmount()).isEqualByComparingTo("50.00");
            verify(balanceService).updateGroupBalances(groupId);
        }

        @Test
        @DisplayName("should throw when paying self")
        void create_paySelf() {
            SettlementCreateRequest req = new SettlementCreateRequest();
            req.setGroupId(groupId);
            req.setPaidTo(payer.getId());
            req.setAmount(new BigDecimal("50.00"));

            assertThatThrownBy(() -> settlementService.createSettlement(payer, req))
                    .isInstanceOf(BadRequestException.class)
                    .hasMessageContaining("Cannot pay yourself");
        }

        @Test
        @DisplayName("should throw when users not in group")
        void create_notMember() {
            SettlementCreateRequest req = new SettlementCreateRequest();
            req.setGroupId(groupId);
            req.setPaidTo(payee.getId());
            req.setAmount(new BigDecimal("50.00"));

            when(groupMemberRepository.existsByGroupIdAndUserId(groupId, payer.getId())).thenReturn(false);
            when(groupMemberRepository.existsByGroupIdAndUserId(groupId, payee.getId())).thenReturn(true);

            assertThatThrownBy(() -> settlementService.createSettlement(payer, req))
                    .isInstanceOf(BadRequestException.class)
                    .hasMessageContaining("must be members");
        }
    }
}
