package com.snapsplit.controller;

import com.snapsplit.dto.request.ExpenseUpdateRequest;
import com.snapsplit.dto.request.ManualExpenseCreateRequest;
import com.snapsplit.dto.response.ExpenseResponse;
import com.snapsplit.entity.UserEntity;
import com.snapsplit.service.ExpenseService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

/**
 * Expense controller — equivalent to Python's routes/expenses.py
 */
@RestController
@RequestMapping("/api/v1/expenses")
public class ExpenseController {

    private final ExpenseService expenseService;

    public ExpenseController(ExpenseService expenseService) {
        this.expenseService = expenseService;
    }

    @PostMapping("/manual")
    @ResponseStatus(HttpStatus.CREATED)
    public ExpenseResponse createManualExpense(
            @Valid @RequestBody ManualExpenseCreateRequest request,
            @AuthenticationPrincipal UserEntity currentUser) {
        return expenseService.createManualExpense(currentUser, request);
    }

    @GetMapping("/{expenseId}")
    public ExpenseResponse getExpense(
            @PathVariable UUID expenseId,
            @AuthenticationPrincipal UserEntity currentUser) {
        return expenseService.getExpense(currentUser, expenseId);
    }

    @GetMapping("/group/{groupId}")
    public List<ExpenseResponse> getGroupExpenses(
            @PathVariable UUID groupId,
            @AuthenticationPrincipal UserEntity currentUser) {
        return expenseService.getGroupExpenses(currentUser, groupId);
    }

    @PutMapping("/{expenseId}")
    public ExpenseResponse updateExpense(
            @PathVariable UUID expenseId,
            @Valid @RequestBody ExpenseUpdateRequest request,
            @AuthenticationPrincipal UserEntity currentUser) {
        return expenseService.updateExpense(currentUser, expenseId, request);
    }
}
