package com.snapsplit.service;

import com.snapsplit.ai.BillParser;
import com.snapsplit.ai.LlmService;
import com.snapsplit.ai.OcrService;
import com.snapsplit.entity.*;
import com.snapsplit.enums.ExpenseStatus;
import com.snapsplit.enums.SplitType;
import com.snapsplit.repository.*;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.*;

/**
 * AI expense service — equivalent to Python's ai_expense_service.py +
 * ai_tasks.py
 *
 * Orchestrates the 7-step pipeline:
 * 1. OCR text extraction
 * 2. LLM structured data extraction
 * 3. Data validation
 * 4. Create expense items
 * 5. Generate equal splits
 * 6. Update expense totals → READY
 * 7. Update group balances
 *
 * Uses @Async instead of Celery for background processing.
 */
@Slf4j
@Service
public class AiExpenseService {

    private final OcrService ocrService;
    private final LlmService llmService;
    private final BillParser billParser;
    private final ExpenseRepository expenseRepository;
    private final ExpenseItemRepository expenseItemRepository;
    private final SplitRepository splitRepository;
    private final GroupMemberRepository groupMemberRepository;
    private final BalanceService balanceService;

    public AiExpenseService(OcrService ocrService,
            LlmService llmService,
            BillParser billParser,
            ExpenseRepository expenseRepository,
            ExpenseItemRepository expenseItemRepository,
            SplitRepository splitRepository,
            GroupMemberRepository groupMemberRepository,
            BalanceService balanceService) {
        this.ocrService = ocrService;
        this.llmService = llmService;
        this.billParser = billParser;
        this.expenseRepository = expenseRepository;
        this.expenseItemRepository = expenseItemRepository;
        this.splitRepository = splitRepository;
        this.groupMemberRepository = groupMemberRepository;
        this.balanceService = balanceService;
    }

    /**
     * Process a bill image asynchronously (background thread).
     * Python equivalent: process_bill_image_task (Celery task)
     *
     * Never throws — always sets expense to READY or FAILED.
     */
    @Async
    public void processBillImageAsync(UUID expenseId, String imagePath, UUID groupId) {
        log.info("Starting async AI processing for expense {}", expenseId);
        processBillImage(expenseId, imagePath, groupId);
    }

    @Transactional
    public void processBillImage(UUID expenseId, String imagePath, UUID groupId) {
        ExpenseEntity expense = expenseRepository.findById(expenseId).orElse(null);
        if (expense == null) {
            log.error("Expense {} not found", expenseId);
            return;
        }

        // Idempotency guard
        if (expense.getStatus() != ExpenseStatus.PROCESSING) {
            log.warn("Expense {} already processed (status: {}). Skipping.", expenseId, expense.getStatus());
            return;
        }

        try {
            // Step 1: OCR
            log.info("Step 1: OCR extraction");
            String ocrText = ocrService.extractText(imagePath);
            expense.setRawOcrText(ocrText);
            expenseRepository.save(expense);
            log.info("OCR extracted {} characters", ocrText.length());

            // Step 2: LLM
            log.info("Step 2: LLM structured extraction");
            Map<String, Object> billData = llmService.extractBillData(ocrText);

            // Step 3: Validate
            log.info("Step 3: Data validation");
            Map<String, Object> validated = billParser.validateBillData(billData);

            // Step 4: Create expense items
            log.info("Step 4: Creating expense items");
            @SuppressWarnings("unchecked")
            List<Map<String, Object>> items = (List<Map<String, Object>>) validated.get("items");
            List<ExpenseItemEntity> expenseItems = createExpenseItems(expense, items);
            log.info("Created {} expense items", expenseItems.size());

            // Step 5: Generate equal splits
            log.info("Step 5: Generating equal splits");
            createEqualSplits(expenseItems, groupId);

            // Step 6: Update expense totals → READY
            log.info("Step 6: Updating expense totals");
            expense.setSubtotal((BigDecimal) validated.get("subtotal"));
            expense.setTax((BigDecimal) validated.get("tax"));
            expense.setTotalAmount((BigDecimal) validated.get("total"));
            expense.setStatus(ExpenseStatus.READY);
            expenseRepository.save(expense);

            // Step 7: Update group balances
            log.info("Step 7: Updating group balances");
            balanceService.updateGroupBalances(groupId);

            log.info("AI processing completed for expense {}: {} items, total {}",
                    expenseId, expenseItems.size(), expense.getTotalAmount());

        } catch (Exception e) {
            log.error("AI processing failed for expense {}: {}", expenseId, e.getMessage(), e);
            expense.setStatus(ExpenseStatus.FAILED);
            expenseRepository.save(expense);
        }
    }

    private List<ExpenseItemEntity> createExpenseItems(ExpenseEntity expense,
            List<Map<String, Object>> itemsData) {
        List<ExpenseItemEntity> result = new ArrayList<>();
        for (Map<String, Object> itemData : itemsData) {
            ExpenseItemEntity item = ExpenseItemEntity.builder()
                    .expense(expense)
                    .itemName((String) itemData.get("name"))
                    .quantity((Integer) itemData.get("quantity"))
                    .price((BigDecimal) itemData.get("price"))
                    .build();
            result.add(expenseItemRepository.save(item));
        }
        return result;
    }

    private void createEqualSplits(List<ExpenseItemEntity> expenseItems, UUID groupId) {
        List<GroupMemberEntity> members = groupMemberRepository.findByGroupId(groupId);
        if (members.isEmpty()) {
            throw new IllegalStateException("No members in group " + groupId);
        }
        int memberCount = members.size();

        for (ExpenseItemEntity item : expenseItems) {
            BigDecimal totalItemCost = item.getPrice().multiply(BigDecimal.valueOf(item.getQuantity()));
            BigDecimal splitAmount = totalItemCost.divide(
                    BigDecimal.valueOf(memberCount), 2, RoundingMode.HALF_UP);

            for (GroupMemberEntity member : members) {
                splitRepository.save(SplitEntity.builder()
                        .expenseItem(item)
                        .user(UserEntity.builder().id(member.getUserId()).build())
                        .amount(splitAmount)
                        .splitType(SplitType.EQUAL)
                        .build());
            }
        }
    }
}
