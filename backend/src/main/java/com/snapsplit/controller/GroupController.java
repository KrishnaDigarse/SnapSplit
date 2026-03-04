package com.snapsplit.controller;

import com.snapsplit.dto.request.GroupCreateRequest;
import com.snapsplit.dto.request.GroupMemberAddRequest;
import com.snapsplit.dto.response.BalanceViewResponse;
import com.snapsplit.dto.response.ExpenseResponse;
import com.snapsplit.dto.response.GroupResponse;
import com.snapsplit.entity.UserEntity;
import com.snapsplit.service.BalanceService;
import com.snapsplit.service.ExpenseService;
import com.snapsplit.service.GroupService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Group controller — equivalent to Python's routes/groups.py
 */
@RestController
@RequestMapping("/api/v1/groups")
public class GroupController {

    private final GroupService groupService;
    private final ExpenseService expenseService;
    private final BalanceService balanceService;

    public GroupController(GroupService groupService,
            ExpenseService expenseService,
            BalanceService balanceService) {
        this.groupService = groupService;
        this.expenseService = expenseService;
        this.balanceService = balanceService;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public GroupResponse createGroup(
            @Valid @RequestBody GroupCreateRequest request,
            @AuthenticationPrincipal UserEntity currentUser) {
        return groupService.createGroup(currentUser, request);
    }

    @PostMapping("/{groupId}/add-member")
    public Map<String, String> addMember(
            @PathVariable UUID groupId,
            @Valid @RequestBody GroupMemberAddRequest request,
            @AuthenticationPrincipal UserEntity currentUser) {
        return groupService.addMember(currentUser, groupId, request);
    }

    @GetMapping
    public List<GroupResponse> getGroups(
            @AuthenticationPrincipal UserEntity currentUser) {
        return groupService.getGroups(currentUser);
    }

    @GetMapping("/{groupId}")
    public GroupResponse.GroupDetailResponse getGroup(
            @PathVariable UUID groupId,
            @AuthenticationPrincipal UserEntity currentUser) {
        return groupService.getGroupDetail(currentUser, groupId);
    }

    @DeleteMapping("/{groupId}")
    public Map<String, String> deleteGroup(
            @PathVariable UUID groupId,
            @AuthenticationPrincipal UserEntity currentUser) {
        return groupService.deleteGroup(currentUser, groupId);
    }

    @DeleteMapping("/{groupId}/members/{userId}")
    public Map<String, String> removeMember(
            @PathVariable UUID groupId,
            @PathVariable UUID userId,
            @AuthenticationPrincipal UserEntity currentUser) {
        return groupService.removeMember(currentUser, groupId, userId);
    }

    @PostMapping("/{groupId}/leave")
    public Map<String, String> leaveGroup(
            @PathVariable UUID groupId,
            @AuthenticationPrincipal UserEntity currentUser) {
        return groupService.leaveGroup(currentUser, groupId);
    }

    @GetMapping("/{groupId}/expenses")
    public List<ExpenseResponse> getGroupExpenses(
            @PathVariable UUID groupId,
            @AuthenticationPrincipal UserEntity currentUser) {
        return expenseService.getGroupExpenses(currentUser, groupId);
    }

    @GetMapping("/{groupId}/balances")
    public BalanceViewResponse getGroupBalances(
            @PathVariable UUID groupId,
            @AuthenticationPrincipal UserEntity currentUser) {
        groupService.assertMember(groupId, currentUser);
        return balanceService.calculateGroupDebts(groupId);
    }
}
