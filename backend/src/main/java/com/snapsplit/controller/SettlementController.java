package com.snapsplit.controller;

import com.snapsplit.dto.request.SettlementCreateRequest;
import com.snapsplit.dto.response.BalanceViewResponse;
import com.snapsplit.dto.response.SettlementResponse;
import com.snapsplit.entity.UserEntity;
import com.snapsplit.service.SettlementService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

/**
 * Settlement controller — equivalent to Python's routes/settlements.py
 */
@RestController
@RequestMapping("/api/v1/settlements")
public class SettlementController {

    private final SettlementService settlementService;

    public SettlementController(SettlementService settlementService) {
        this.settlementService = settlementService;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public SettlementResponse createSettlement(
            @Valid @RequestBody SettlementCreateRequest request,
            @AuthenticationPrincipal UserEntity currentUser) {
        return settlementService.createSettlement(currentUser, request);
    }

    @GetMapping("/balances/{groupId}")
    public BalanceViewResponse getGroupFinancials(
            @PathVariable UUID groupId,
            @AuthenticationPrincipal UserEntity currentUser) {
        return settlementService.getGroupFinancials(currentUser, groupId);
    }
}
