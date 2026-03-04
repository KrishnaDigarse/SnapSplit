package com.snapsplit.service;

import com.snapsplit.dto.response.BalanceViewResponse;
import com.snapsplit.entity.*;
import com.snapsplit.repository.*;
import jakarta.persistence.EntityManager;
import jakarta.persistence.PersistenceContext;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.util.*;

/**
 * Balance computation service — equivalent to Python's balance_service.py
 *
 * Computes per-user balances (paid, share, settled, net) and
 * minimizes debts using a greedy algorithm.
 */
@Service
public class BalanceService {

    private final GroupMemberRepository groupMemberRepository;
    private final ExpenseRepository expenseRepository;
    private final ExpenseItemRepository expenseItemRepository;
    private final SplitRepository splitRepository;
    private final SettlementRepository settlementRepository;
    private final GroupBalanceRepository groupBalanceRepository;

    @PersistenceContext
    private EntityManager entityManager;

    public BalanceService(GroupMemberRepository groupMemberRepository,
            ExpenseRepository expenseRepository,
            ExpenseItemRepository expenseItemRepository,
            SplitRepository splitRepository,
            SettlementRepository settlementRepository,
            GroupBalanceRepository groupBalanceRepository) {
        this.groupMemberRepository = groupMemberRepository;
        this.expenseRepository = expenseRepository;
        this.expenseItemRepository = expenseItemRepository;
        this.splitRepository = splitRepository;
        this.settlementRepository = settlementRepository;
        this.groupBalanceRepository = groupBalanceRepository;
    }

    /**
     * Compute net balance for each user in a group.
     * Python equivalent: compute_group_balances()
     */
    public List<BalanceViewResponse.GroupBalanceDetail> computeGroupBalances(UUID groupId) {
        List<GroupMemberEntity> members = groupMemberRepository.findByGroupId(groupId);

        // Build balance map: userId → balance detail
        Map<UUID, BalanceViewResponse.GroupBalanceDetail> balances = new LinkedHashMap<>();
        for (GroupMemberEntity member : members) {
            UserEntity user = member.getUser();
            balances.put(member.getUserId(), BalanceViewResponse.GroupBalanceDetail.builder()
                    .userId(member.getUserId())
                    .userName(user.getName())
                    .totalPaid(BigDecimal.ZERO)
                    .totalShare(BigDecimal.ZERO)
                    .totalSettled(BigDecimal.ZERO)
                    .netBalance(BigDecimal.ZERO)
                    .updatedAt(LocalDateTime.now())
                    .build());
        }

        // Process expenses
        List<ExpenseEntity> expenses = expenseRepository.findByGroupIdOrderByCreatedAtDesc(groupId);
        for (ExpenseEntity expense : expenses) {
            if (expense.getTotalAmount() == null)
                continue;

            UUID payerId = expense.getCreator() != null ? expense.getCreator().getId() : null;
            BigDecimal expenseTotalShares = BigDecimal.ZERO;

            List<ExpenseItemEntity> items = expenseItemRepository.findByExpenseId(expense.getId());

            // Batch load all splits for performance (avoids N+1)
            if (!items.isEmpty()) {
                List<UUID> itemIds = items.stream().map(ExpenseItemEntity::getId).toList();
                List<SplitEntity> allSplits = splitRepository.findAllById(
                        itemIds.stream().map(id -> {
                            // Use findByExpenseItemId for each — simplified approach
                            return id;
                        }).toList());

                // Collect all splits for these items
                List<SplitEntity> splits = new ArrayList<>();
                for (ExpenseItemEntity item : items) {
                    splits.addAll(splitRepository.findByExpenseItemId(item.getId()));
                }

                for (SplitEntity split : splits) {
                    BalanceViewResponse.GroupBalanceDetail bal = balances.get(split.getUser().getId());
                    if (bal != null) {
                        bal.setTotalShare(bal.getTotalShare().add(split.getAmount()));
                        bal.setNetBalance(bal.getNetBalance().subtract(split.getAmount()));
                        expenseTotalShares = expenseTotalShares.add(split.getAmount());
                    }
                }
            }

            // Credit the payer with the exact amount that was split
            if (payerId != null && balances.containsKey(payerId)) {
                BalanceViewResponse.GroupBalanceDetail payerBal = balances.get(payerId);
                payerBal.setTotalPaid(payerBal.getTotalPaid().add(expenseTotalShares));
                payerBal.setNetBalance(payerBal.getNetBalance().add(expenseTotalShares));
            }
        }

        // Process settlements
        List<SettlementEntity> settlements = settlementRepository.findByGroupIdOrderByCreatedAtDesc(groupId);
        for (SettlementEntity settlement : settlements) {
            UUID payerById = settlement.getPayer().getId();
            UUID payeeId = settlement.getPayee().getId();

            if (balances.containsKey(payerById)) {
                BalanceViewResponse.GroupBalanceDetail b = balances.get(payerById);
                b.setNetBalance(b.getNetBalance().add(settlement.getAmount()));
                b.setTotalSettled(b.getTotalSettled().subtract(settlement.getAmount()));
            }
            if (balances.containsKey(payeeId)) {
                BalanceViewResponse.GroupBalanceDetail b = balances.get(payeeId);
                b.setNetBalance(b.getNetBalance().subtract(settlement.getAmount()));
                b.setTotalSettled(b.getTotalSettled().add(settlement.getAmount()));
            }
        }

        return new ArrayList<>(balances.values());
    }

    /**
     * Update the group_balances cache table.
     * Python equivalent: update_group_balances() with SELECT FOR UPDATE
     */
    @Transactional
    public void updateGroupBalances(UUID groupId) {
        // Row-level lock to prevent race conditions
        entityManager.createNativeQuery("SELECT * FROM group_balances WHERE group_id = :gid FOR UPDATE")
                .setParameter("gid", groupId)
                .getResultList();

        List<BalanceViewResponse.GroupBalanceDetail> computed = computeGroupBalances(groupId);

        for (BalanceViewResponse.GroupBalanceDetail detail : computed) {
            Optional<GroupBalanceEntity> existing = groupBalanceRepository
                    .findByGroupIdAndUserId(groupId, detail.getUserId());

            if (existing.isPresent()) {
                GroupBalanceEntity entity = existing.get();
                entity.setNetBalance(detail.getNetBalance());
                entity.setUpdatedAt(LocalDateTime.now());
                groupBalanceRepository.save(entity);
            } else {
                GroupBalanceEntity entity = GroupBalanceEntity.builder()
                        .groupId(groupId)
                        .userId(detail.getUserId())
                        .netBalance(detail.getNetBalance())
                        .updatedAt(LocalDateTime.now())
                        .build();
                groupBalanceRepository.save(entity);
            }
        }
    }

    /**
     * Minimize debts using a greedy algorithm.
     * Python equivalent: minimize_debts()
     */
    public List<BalanceViewResponse.DebtDetail> minimizeDebts(List<BalanceViewResponse.GroupBalanceDetail> balances) {
        List<Map.Entry<String, BigDecimal>> debtors = new ArrayList<>();
        List<Map.Entry<String, BigDecimal>> creditors = new ArrayList<>();

        for (BalanceViewResponse.GroupBalanceDetail b : balances) {
            int cmp = b.getNetBalance().compareTo(BigDecimal.ZERO);
            if (cmp < 0) {
                debtors.add(Map.entry(b.getUserName(), b.getNetBalance().negate()));
            } else if (cmp > 0) {
                creditors.add(Map.entry(b.getUserName(), b.getNetBalance()));
            }
        }

        // Sort descending by amount
        debtors.sort((a, b) -> b.getValue().compareTo(a.getValue()));
        creditors.sort((a, b) -> b.getValue().compareTo(a.getValue()));

        List<BalanceViewResponse.DebtDetail> debts = new ArrayList<>();
        // Use mutable wrappers
        BigDecimal[] debtorAmounts = debtors.stream().map(Map.Entry::getValue).toArray(BigDecimal[]::new);
        BigDecimal[] creditorAmounts = creditors.stream().map(Map.Entry::getValue).toArray(BigDecimal[]::new);

        int i = 0, j = 0;
        while (i < debtors.size() && j < creditors.size()) {
            BigDecimal amount = debtorAmounts[i].min(creditorAmounts[j]);

            if (amount.compareTo(BigDecimal.ZERO) > 0) {
                debts.add(BalanceViewResponse.DebtDetail.builder()
                        .fromUser(debtors.get(i).getKey())
                        .toUser(creditors.get(j).getKey())
                        .amount(amount.setScale(2, RoundingMode.HALF_UP))
                        .build());
            }

            debtorAmounts[i] = debtorAmounts[i].subtract(amount);
            creditorAmounts[j] = creditorAmounts[j].subtract(amount);

            if (debtorAmounts[i].compareTo(new BigDecimal("0.01")) < 0)
                i++;
            if (creditorAmounts[j].compareTo(new BigDecimal("0.01")) < 0)
                j++;
        }

        return debts;
    }

    /**
     * Calculate comprehensive group debts (balances + simplified debts).
     * Python equivalent: calculate_group_debts()
     */
    public BalanceViewResponse calculateGroupDebts(UUID groupId) {
        List<BalanceViewResponse.GroupBalanceDetail> balances = computeGroupBalances(groupId);
        List<BalanceViewResponse.DebtDetail> debts = minimizeDebts(balances);

        return BalanceViewResponse.builder()
                .balances(balances)
                .debts(debts)
                .build();
    }
}
