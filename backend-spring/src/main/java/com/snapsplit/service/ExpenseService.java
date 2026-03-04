package com.snapsplit.service;

import com.snapsplit.dto.request.ExpenseUpdateRequest;
import com.snapsplit.dto.request.ManualExpenseCreateRequest;
import com.snapsplit.dto.response.ExpenseResponse;
import com.snapsplit.entity.*;
import com.snapsplit.enums.ExpenseStatus;
import com.snapsplit.enums.SourceType;
import com.snapsplit.enums.SplitType;
import com.snapsplit.exception.BadRequestException;
import com.snapsplit.exception.ResourceNotFoundException;
import com.snapsplit.exception.UnauthorizedException;
import com.snapsplit.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.*;

/**
 * Expense service — equivalent to Python's expense_service.py
 */
@Service
public class ExpenseService {

    private final ExpenseRepository expenseRepository;
    private final ExpenseItemRepository expenseItemRepository;
    private final SplitRepository splitRepository;
    private final GroupMemberRepository groupMemberRepository;
    private final BalanceService balanceService;

    public ExpenseService(ExpenseRepository expenseRepository,
            ExpenseItemRepository expenseItemRepository,
            SplitRepository splitRepository,
            GroupMemberRepository groupMemberRepository,
            BalanceService balanceService) {
        this.expenseRepository = expenseRepository;
        this.expenseItemRepository = expenseItemRepository;
        this.splitRepository = splitRepository;
        this.groupMemberRepository = groupMemberRepository;
        this.balanceService = balanceService;
    }

    @Transactional
    public ExpenseResponse createManualExpense(UserEntity currentUser, ManualExpenseCreateRequest request) {
        assertMember(request.getGroupId(), currentUser);

        // Validate split total matches expense total
        BigDecimal splitTotal = request.getSplits().stream()
                .map(ManualExpenseCreateRequest.SplitCreate::getAmount)
                .reduce(BigDecimal.ZERO, BigDecimal::add);

        if (splitTotal.subtract(request.getTotalAmount()).abs().compareTo(new BigDecimal("0.01")) > 0) {
            throw new BadRequestException(
                    "Split amounts (" + splitTotal + ") must equal total amount (" + request.getTotalAmount() + ")");
        }

        // Create expense
        ExpenseEntity expense = ExpenseEntity.builder()
                .group(GroupEntity.builder().id(request.getGroupId()).build())
                .creator(currentUser)
                .sourceType(SourceType.MANUAL)
                .status(ExpenseStatus.READY)
                .isEdited(false)
                .subtotal(request.getSubtotal())
                .tax(request.getTax() != null ? request.getTax() : BigDecimal.ZERO)
                .totalAmount(request.getTotalAmount())
                .build();
        ExpenseEntity savedExpense = expenseRepository.save(expense);

        // Create items
        ExpenseItemEntity firstItem = null;
        for (ManualExpenseCreateRequest.ExpenseItemCreate itemData : request.getItems()) {
            ExpenseItemEntity item = ExpenseItemEntity.builder()
                    .expense(savedExpense)
                    .itemName(itemData.getItemName())
                    .quantity(itemData.getQuantity())
                    .price(itemData.getPrice())
                    .build();
            ExpenseItemEntity savedItem = expenseItemRepository.save(item);
            if (firstItem == null)
                firstItem = savedItem;
        }

        // Create splits (attached to first item, like Python)
        if (firstItem != null) {
            for (ManualExpenseCreateRequest.SplitCreate splitData : request.getSplits()) {
                assertMember(request.getGroupId(), splitData.getUserId());

                SplitEntity split = SplitEntity.builder()
                        .expenseItem(firstItem)
                        .user(UserEntity.builder().id(splitData.getUserId()).build())
                        .amount(splitData.getAmount())
                        .splitType(splitData.getSplitType() != null ? splitData.getSplitType() : SplitType.EQUAL)
                        .build();
                splitRepository.save(split);
            }
        }

        // Update group balances
        balanceService.updateGroupBalances(request.getGroupId());

        return toExpenseResponse(savedExpense);
    }

    public ExpenseResponse getExpense(UserEntity currentUser, UUID expenseId) {
        ExpenseEntity expense = expenseRepository.findById(expenseId)
                .orElseThrow(() -> new ResourceNotFoundException("Expense not found"));

        assertMember(expense.getGroup().getId(), currentUser);
        return toExpenseResponse(expense);
    }

    public List<ExpenseResponse> getGroupExpenses(UserEntity currentUser, UUID groupId) {
        assertMember(groupId, currentUser);
        List<ExpenseEntity> expenses = expenseRepository.findByGroupIdOrderByCreatedAtDesc(groupId);
        return expenses.stream().map(this::toExpenseResponse).toList();
    }

    @Transactional
    public ExpenseResponse updateExpense(UserEntity currentUser, UUID expenseId, ExpenseUpdateRequest request) {
        ExpenseEntity expense = expenseRepository.findById(expenseId)
                .orElseThrow(() -> new ResourceNotFoundException("Expense not found"));

        assertMember(expense.getGroup().getId(), currentUser);

        // Update fields
        expense.setSubtotal(request.getSubtotal());
        expense.setTax(request.getTax() != null ? request.getTax() : BigDecimal.ZERO);
        expense.setTotalAmount(request.getTotalAmount());
        expense.setIsEdited(true);
        expense.setStatus(ExpenseStatus.READY);

        // Delete existing items and splits
        List<ExpenseItemEntity> existingItems = expenseItemRepository.findByExpenseId(expenseId);
        for (ExpenseItemEntity item : existingItems) {
            splitRepository.deleteAll(splitRepository.findByExpenseItemId(item.getId()));
        }
        expenseItemRepository.deleteAll(existingItems);

        // Add new items
        ExpenseItemEntity firstItem = null;
        for (ManualExpenseCreateRequest.ExpenseItemCreate itemData : request.getItems()) {
            ExpenseItemEntity item = ExpenseItemEntity.builder()
                    .expense(expense)
                    .itemName(itemData.getItemName())
                    .quantity(itemData.getQuantity())
                    .price(itemData.getPrice())
                    .build();
            ExpenseItemEntity saved = expenseItemRepository.save(item);
            if (firstItem == null)
                firstItem = saved;
        }

        // Create default EQUAL splits for all group members
        if (firstItem != null) {
            List<GroupMemberEntity> members = groupMemberRepository.findByGroupId(expense.getGroup().getId());
            int memberCount = members.size();

            if (memberCount > 0) {
                BigDecimal splitAmount = expense.getTotalAmount()
                        .divide(BigDecimal.valueOf(memberCount), 2, RoundingMode.HALF_UP);
                BigDecimal totalSplit = splitAmount.multiply(BigDecimal.valueOf(memberCount));
                BigDecimal diff = expense.getTotalAmount().subtract(totalSplit);

                for (int i = 0; i < members.size(); i++) {
                    BigDecimal amount = (i == 0) ? splitAmount.add(diff) : splitAmount;
                    splitRepository.save(SplitEntity.builder()
                            .expenseItem(firstItem)
                            .user(UserEntity.builder().id(members.get(i).getUserId()).build())
                            .amount(amount)
                            .splitType(SplitType.EQUAL)
                            .build());
                }
            }
        }

        expenseRepository.save(expense);
        balanceService.updateGroupBalances(expense.getGroup().getId());

        return toExpenseResponse(expense);
    }

    // ── Helpers ──

    private void assertMember(UUID groupId, UserEntity user) {
        assertMember(groupId, user.getId());
    }

    private void assertMember(UUID groupId, UUID userId) {
        if (!groupMemberRepository.existsByGroupIdAndUserId(groupId, userId)) {
            throw new UnauthorizedException("Not a member of this group");
        }
    }

    private ExpenseResponse toExpenseResponse(ExpenseEntity expense) {
        List<ExpenseItemEntity> items = expenseItemRepository.findByExpenseId(expense.getId());

        return ExpenseResponse.builder()
                .id(expense.getId())
                .groupId(expense.getGroup().getId())
                .createdBy(expense.getCreator() != null ? expense.getCreator().getId() : null)
                .creatorName(expense.getCreatorName())
                .sourceType(expense.getSourceType().name())
                .status(expense.getStatus().name())
                .isEdited(expense.getIsEdited())
                .subtotal(expense.getSubtotal())
                .tax(expense.getTax())
                .totalAmount(expense.getTotalAmount())
                .createdAt(expense.getCreatedAt())
                .rawOcrText(expense.getRawOcrText())
                .items(items.stream().map(item -> ExpenseResponse.ExpenseItemResponse.builder()
                        .id(item.getId())
                        .expenseId(expense.getId())
                        .itemName(item.getItemName())
                        .quantity(item.getQuantity())
                        .price(item.getPrice())
                        .build()).toList())
                .build();
    }
}
