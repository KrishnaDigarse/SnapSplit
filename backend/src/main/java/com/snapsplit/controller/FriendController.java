package com.snapsplit.controller;

import com.snapsplit.dto.request.FriendRequestCreateRequest;
import com.snapsplit.dto.response.FriendRequestResponse;
import com.snapsplit.dto.response.FriendResponse;
import com.snapsplit.entity.UserEntity;
import com.snapsplit.service.FriendService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * Friend controller — equivalent to Python's routes/friends.py
 */
@RestController
@RequestMapping("/api/v1/friends")
public class FriendController {

    private final FriendService friendService;

    public FriendController(FriendService friendService) {
        this.friendService = friendService;
    }

    @PostMapping("/request")
    @ResponseStatus(HttpStatus.CREATED)
    public FriendRequestResponse sendFriendRequest(
            @Valid @RequestBody FriendRequestCreateRequest request,
            @AuthenticationPrincipal UserEntity currentUser) {
        return friendService.sendFriendRequest(currentUser, request);
    }

    @PostMapping("/request/{requestId}/accept")
    public Map<String, String> acceptFriendRequest(
            @PathVariable UUID requestId,
            @AuthenticationPrincipal UserEntity currentUser) {
        return friendService.acceptFriendRequest(currentUser, requestId);
    }

    @PostMapping("/request/{requestId}/reject")
    public FriendRequestResponse rejectFriendRequest(
            @PathVariable UUID requestId,
            @AuthenticationPrincipal UserEntity currentUser) {
        return friendService.rejectFriendRequest(currentUser, requestId);
    }

    @GetMapping("/requests")
    public List<FriendRequestResponse> getPendingRequests(
            @AuthenticationPrincipal UserEntity currentUser) {
        return friendService.getPendingRequests(currentUser);
    }

    @GetMapping
    public List<FriendResponse> getFriends(
            @AuthenticationPrincipal UserEntity currentUser) {
        return friendService.getFriends(currentUser);
    }

    @GetMapping("/{friendId}/direct-group")
    public Map<String, Object> getDirectGroup(
            @PathVariable UUID friendId,
            @AuthenticationPrincipal UserEntity currentUser) {
        return friendService.getDirectGroup(currentUser, friendId);
    }

    @DeleteMapping("/{friendId}")
    public Map<String, String> removeFriend(
            @PathVariable UUID friendId,
            @AuthenticationPrincipal UserEntity currentUser) {
        return friendService.removeFriend(currentUser, friendId);
    }
}
