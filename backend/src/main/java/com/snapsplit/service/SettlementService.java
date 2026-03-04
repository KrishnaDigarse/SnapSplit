package com.snapsplit.service;

import com.snapsplit.dto.request.SettlementCreateRequest;
import com.snapsplit.dto.response.BalanceViewResponse;
import com.snapsplit.dto.response.SettlementResponse;
import com.snapsplit.entity.*;
import com.snapsplit.exception.BadRequestException;
import com.snapsplit.exception.UnauthorizedException;
import com.snapsplit.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.UUID;

/**
 * Settlement service — equivalent to Python's settlement_service.py
 */
@Service
public class SettlementService {

    private final SettlementRepository settlementRepository;
    private final GroupMemberRepository groupMemberRepository;
    private final BalanceService balanceService;

    public SettlementService(SettlementRepository settlementRepository,
            GroupMemberRepository groupMemberRepository,
            BalanceService balanceService) {
        this.settlementRepository = settlementRepository;
        this.groupMemberRepository = groupMemberRepository;
        this.balanceService = balanceService;
    }

    @Transactional
    public SettlementResponse createSettlement(UserEntity currentUser, SettlementCreateRequest request) {
        if (currentUser.getId().equals(request.getPaidTo())) {
            throw new BadRequestException("Cannot pay yourself");
        }

        boolean payerMember = groupMemberRepository.existsByGroupIdAndUserId(
                request.getGroupId(), currentUser.getId());
        boolean payeeMember = groupMemberRepository.existsByGroupIdAndUserId(
                request.getGroupId(), request.getPaidTo());

        if (!payerMember || !payeeMember) {
            throw new BadRequestException("Both users must be members of the group");
        }

        SettlementEntity settlement = SettlementEntity.builder()
                .group(GroupEntity.builder().id(request.getGroupId()).build())
                .payer(currentUser)
                .payee(UserEntity.builder().id(request.getPaidTo()).build())
                .amount(request.getAmount())
                .paymentMethod(request.getPaymentMethod())
                .note(request.getNote())
                .build();

        SettlementEntity saved = settlementRepository.save(settlement);

        balanceService.updateGroupBalances(request.getGroupId());

        return toResponse(saved);
    }

    public BalanceViewResponse getGroupFinancials(UserEntity currentUser, UUID groupId) {
        if (!groupMemberRepository.existsByGroupIdAndUserId(groupId, currentUser.getId())) {
            throw new UnauthorizedException("Not a member of this group");
        }

        return balanceService.calculateGroupDebts(groupId);
    }

    private SettlementResponse toResponse(SettlementEntity s) {
        return SettlementResponse.builder()
                .id(s.getId())
                .groupId(s.getGroup().getId())
                .paidBy(s.getPayer().getId())
                .paidTo(s.getPayee().getId())
                .amount(s.getAmount())
                .paymentMethod(s.getPaymentMethod())
                .note(s.getNote())
                .createdAt(s.getCreatedAt())
                .build();
    }
}
