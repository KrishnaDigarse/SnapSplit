package com.snapsplit.controller;

import com.snapsplit.entity.*;
import com.snapsplit.enums.ExpenseStatus;
import com.snapsplit.enums.SourceType;
import com.snapsplit.exception.BadRequestException;
import com.snapsplit.exception.ResourceNotFoundException;
import com.snapsplit.exception.UnauthorizedException;
import com.snapsplit.repository.ExpenseRepository;
import com.snapsplit.repository.GroupMemberRepository;
import com.snapsplit.service.AiExpenseService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.util.*;

/**
 * AI expense controller — equivalent to Python's routes/ai_expenses.py
 *
 * Endpoints:
 * POST /api/v1/expenses/bill → upload bill image for async AI processing
 * GET /api/v1/expenses/{id}/status → poll processing status
 */
@Slf4j
@RestController
@RequestMapping("/api/v1/expenses")
public class AiExpenseController {

    private static final long MAX_FILE_SIZE = 10 * 1024 * 1024; // 10 MB
    private static final Set<String> ALLOWED_EXTENSIONS = Set.of(".jpg", ".jpeg", ".png");

    @Value("${app.upload.dir:uploads/bills}")
    private String uploadDir;

    private final AiExpenseService aiExpenseService;
    private final ExpenseRepository expenseRepository;
    private final GroupMemberRepository groupMemberRepository;

    public AiExpenseController(AiExpenseService aiExpenseService,
            ExpenseRepository expenseRepository,
            GroupMemberRepository groupMemberRepository) {
        this.aiExpenseService = aiExpenseService;
        this.expenseRepository = expenseRepository;
        this.groupMemberRepository = groupMemberRepository;
    }

    /**
     * Upload a bill image for async AI processing.
     * Python equivalent: POST /expenses/bill (202 Accepted)
     */
    @PostMapping("/bill")
    @ResponseStatus(HttpStatus.ACCEPTED)
    public Map<String, Object> uploadBill(
            @RequestParam("image") MultipartFile image,
            @RequestParam("group_id") UUID groupId,
            @RequestParam(value = "payer_id", required = false) UUID payerId,
            @AuthenticationPrincipal UserEntity currentUser) throws IOException {

        log.info("Bill upload from user {} for group {}", currentUser.getId(), groupId);

        UUID actualPayerId = (payerId != null) ? payerId : currentUser.getId();

        // Validate payer membership
        if (!groupMemberRepository.existsByGroupIdAndUserId(groupId, actualPayerId)) {
            throw new UnauthorizedException("Payer is not a member of this group");
        }
        // Validate uploader membership if different from payer
        if (!actualPayerId.equals(currentUser.getId())
                && !groupMemberRepository.existsByGroupIdAndUserId(groupId, currentUser.getId())) {
            throw new UnauthorizedException("You are not a member of this group");
        }

        // Validate file
        if (image.isEmpty() || image.getOriginalFilename() == null) {
            throw new BadRequestException("No file provided");
        }

        String fileName = image.getOriginalFilename();
        String ext = fileName.substring(fileName.lastIndexOf('.')).toLowerCase();
        if (!ALLOWED_EXTENSIONS.contains(ext)) {
            throw new BadRequestException("Invalid file type. Allowed: " + ALLOWED_EXTENSIONS);
        }

        if (image.getSize() > MAX_FILE_SIZE) {
            throw new BadRequestException("File too large. Maximum size: 10MB");
        }

        // Create expense with PROCESSING status
        ExpenseEntity expense = ExpenseEntity.builder()
                .group(GroupEntity.builder().id(groupId).build())
                .creator(UserEntity.builder().id(actualPayerId).build())
                .sourceType(SourceType.BILL_IMAGE)
                .status(ExpenseStatus.PROCESSING)
                .build();
        ExpenseEntity saved = expenseRepository.save(expense);

        // Save file with safe filename
        Path uploadPath = Paths.get(uploadDir);
        Files.createDirectories(uploadPath);
        String safeFilename = saved.getId() + ext;
        Path filePath = uploadPath.resolve(safeFilename);

        // Security: verify path stays within upload directory
        if (!filePath.toAbsolutePath().startsWith(uploadPath.toAbsolutePath())) {
            throw new BadRequestException("Invalid file path");
        }

        image.transferTo(filePath.toFile());
        log.info("Saved image to {} ({} bytes)", filePath, image.getSize());

        // Enqueue async processing
        try {
            aiExpenseService.processBillImageAsync(saved.getId(), filePath.toString(), groupId);
        } catch (Exception e) {
            log.error("Failed to enqueue AI task: {}", e.getMessage());
            saved.setStatus(ExpenseStatus.FAILED);
            expenseRepository.save(saved);
            Files.deleteIfExists(filePath);
            throw new BadRequestException("Failed to enqueue processing task. Please try again.");
        }

        Map<String, Object> response = new LinkedHashMap<>();
        response.put("id", saved.getId().toString());
        response.put("status", "PROCESSING");
        response.put("message",
                "Bill is being processed. Poll /api/v1/expenses/" + saved.getId() + "/status for updates.");
        response.put("created_at", saved.getCreatedAt() != null ? saved.getCreatedAt().toString() : null);
        return response;
    }

    /**
     * Get expense processing status.
     * Python equivalent: GET /expenses/{expense_id}/status
     */
    @GetMapping("/{expenseId}/status")
    public Map<String, Object> getExpenseStatus(
            @PathVariable UUID expenseId,
            @AuthenticationPrincipal UserEntity currentUser) {

        ExpenseEntity expense = expenseRepository.findById(expenseId)
                .orElseThrow(() -> new ResourceNotFoundException("Expense not found"));

        if (!groupMemberRepository.existsByGroupIdAndUserId(
                expense.getGroup().getId(), currentUser.getId())) {
            throw new UnauthorizedException("You are not authorized to view this expense");
        }

        Map<String, Object> response = new LinkedHashMap<>();
        response.put("expense_id", expense.getId().toString());
        response.put("status", expense.getStatus().name());
        response.put("created_at", expense.getCreatedAt() != null ? expense.getCreatedAt().toString() : null);

        if (expense.getStatus() == ExpenseStatus.READY) {
            response.put("subtotal", expense.getSubtotal() != null ? expense.getSubtotal().toString() : null);
            response.put("tax", expense.getTax() != null ? expense.getTax().toString() : null);
            response.put("total_amount", expense.getTotalAmount() != null ? expense.getTotalAmount().toString() : null);
            response.put("items_count", expense.getItems() != null ? expense.getItems().size() : 0);
        } else if (expense.getStatus() == ExpenseStatus.FAILED) {
            response.put("error_message", "AI processing failed. Please try uploading the image again.");
        }

        return response;
    }
}
