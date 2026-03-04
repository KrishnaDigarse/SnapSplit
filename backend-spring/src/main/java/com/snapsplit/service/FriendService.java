package com.snapsplit.service;

import com.snapsplit.dto.request.FriendRequestCreateRequest;
import com.snapsplit.dto.response.FriendRequestResponse;
import com.snapsplit.dto.response.FriendResponse;
import com.snapsplit.entity.*;
import com.snapsplit.enums.FriendRequestStatus;
import com.snapsplit.enums.GroupType;
import com.snapsplit.exception.BadRequestException;
import com.snapsplit.exception.ResourceNotFoundException;
import com.snapsplit.exception.UnauthorizedException;
import com.snapsplit.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;

/**
 * Friend service — equivalent to Python's friend_service.py
 */
@Service
public class FriendService {

    private final UserRepository userRepository;
    private final FriendRequestRepository friendRequestRepository;
    private final FriendRepository friendRepository;
    private final GroupRepository groupRepository;
    private final GroupMemberRepository groupMemberRepository;
    private final ExpenseRepository expenseRepository;
    private final ExpenseItemRepository expenseItemRepository;
    private final SplitRepository splitRepository;

    public FriendService(UserRepository userRepository,
            FriendRequestRepository friendRequestRepository,
            FriendRepository friendRepository,
            GroupRepository groupRepository,
            GroupMemberRepository groupMemberRepository,
            ExpenseRepository expenseRepository,
            ExpenseItemRepository expenseItemRepository,
            SplitRepository splitRepository) {
        this.userRepository = userRepository;
        this.friendRequestRepository = friendRequestRepository;
        this.friendRepository = friendRepository;
        this.groupRepository = groupRepository;
        this.groupMemberRepository = groupMemberRepository;
        this.expenseRepository = expenseRepository;
        this.expenseItemRepository = expenseItemRepository;
        this.splitRepository = splitRepository;
    }

    /**
     * Send a friend request by email.
     */
    @Transactional
    public FriendRequestResponse sendFriendRequest(UserEntity sender, FriendRequestCreateRequest request) {
        UserEntity receiver = userRepository.findByEmail(request.getFriendEmail())
                .orElseThrow(() -> new ResourceNotFoundException(
                        "User with email " + request.getFriendEmail() + " not found"));

        if (sender.getId().equals(receiver.getId())) {
            throw new BadRequestException("Cannot send friend request to yourself");
        }

        // Check existing pending request (bidirectional)
        boolean existsPending = friendRequestRepository.existsBySenderIdAndReceiverIdAndStatus(
                sender.getId(), receiver.getId(), FriendRequestStatus.PENDING) ||
                friendRequestRepository.existsBySenderIdAndReceiverIdAndStatus(
                        receiver.getId(), sender.getId(), FriendRequestStatus.PENDING);

        if (existsPending) {
            throw new BadRequestException("Friend request already exists");
        }

        // Check existing friendship
        if (friendRepository.existsByUserIdAndFriendId(sender.getId(), receiver.getId())) {
            throw new BadRequestException("Already friends");
        }

        FriendRequestEntity entity = FriendRequestEntity.builder()
                .sender(sender)
                .receiver(receiver)
                .status(FriendRequestStatus.PENDING)
                .build();

        FriendRequestEntity saved = friendRequestRepository.save(entity);

        return FriendRequestResponse.builder()
                .id(saved.getId())
                .senderId(sender.getId())
                .receiverId(receiver.getId())
                .status(saved.getStatus())
                .createdAt(saved.getCreatedAt())
                .build();
    }

    /**
     * Accept a friend request and create a DIRECT group.
     */
    @Transactional
    public Map<String, String> acceptFriendRequest(UserEntity currentUser, UUID requestId) {
        FriendRequestEntity req = friendRequestRepository.findById(requestId)
                .orElseThrow(() -> new ResourceNotFoundException("Friend request not found"));

        if (!req.getReceiver().getId().equals(currentUser.getId())) {
            throw new UnauthorizedException("Not authorized to accept this request");
        }

        if (req.getStatus() != FriendRequestStatus.PENDING) {
            throw new BadRequestException("Friend request already processed");
        }

        req.setStatus(FriendRequestStatus.ACCEPTED);
        friendRequestRepository.save(req);

        // Create bidirectional friendship
        friendRepository.save(FriendEntity.builder()
                .userId(req.getSender().getId()).friendId(req.getReceiver().getId()).build());
        friendRepository.save(FriendEntity.builder()
                .userId(req.getReceiver().getId()).friendId(req.getSender().getId()).build());

        // Create DIRECT group
        UserEntity sender = req.getSender();
        UserEntity receiver = req.getReceiver();

        GroupEntity directGroup = GroupEntity.builder()
                .name(sender.getName() + " & " + receiver.getName())
                .creator(currentUser)
                .type(GroupType.DIRECT)
                .isArchived(false)
                .build();
        GroupEntity savedGroup = groupRepository.save(directGroup);

        groupMemberRepository.save(GroupMemberEntity.builder()
                .groupId(savedGroup.getId()).userId(sender.getId()).build());
        groupMemberRepository.save(GroupMemberEntity.builder()
                .groupId(savedGroup.getId()).userId(receiver.getId()).build());

        return Map.of("message", "Friend request accepted", "direct_group_id", savedGroup.getId().toString());
    }

    /**
     * Reject a friend request.
     */
    @Transactional
    public FriendRequestResponse rejectFriendRequest(UserEntity currentUser, UUID requestId) {
        FriendRequestEntity req = friendRequestRepository.findById(requestId)
                .orElseThrow(() -> new ResourceNotFoundException("Friend request not found"));

        if (!req.getReceiver().getId().equals(currentUser.getId())) {
            throw new UnauthorizedException("Not authorized to reject this request");
        }

        if (req.getStatus() != FriendRequestStatus.PENDING) {
            throw new BadRequestException("Friend request already processed");
        }

        req.setStatus(FriendRequestStatus.REJECTED);
        friendRequestRepository.save(req);

        return FriendRequestResponse.builder()
                .id(req.getId())
                .senderId(req.getSender().getId())
                .receiverId(req.getReceiver().getId())
                .status(req.getStatus())
                .createdAt(req.getCreatedAt())
                .build();
    }

    /**
     * Get pending friend requests for the current user.
     */
    public List<FriendRequestResponse> getPendingRequests(UserEntity currentUser) {
        List<FriendRequestEntity> requests = friendRequestRepository
                .findByReceiverIdAndStatus(currentUser.getId(), FriendRequestStatus.PENDING);

        return requests.stream().map(req -> FriendRequestResponse.builder()
                .id(req.getId())
                .senderId(req.getSender().getId())
                .receiverId(req.getReceiver().getId())
                .status(req.getStatus())
                .createdAt(req.getCreatedAt())
                .senderName(req.getSender().getName())
                .senderEmail(req.getSender().getEmail())
                .build()).toList();
    }

    /**
     * Get list of friends for the current user.
     */
    public List<FriendResponse> getFriends(UserEntity currentUser) {
        List<FriendEntity> friends = friendRepository.findByUserId(currentUser.getId());

        return friends.stream().map(f -> FriendResponse.builder()
                .userId(f.getUserId())
                .friendId(f.getFriendId())
                .friendName(f.getFriend().getName())
                .friendEmail(f.getFriend().getEmail())
                .createdAt(f.getCreatedAt())
                .build()).toList();
    }

    /**
     * Get the DIRECT group for a specific friend.
     */
    public Map<String, Object> getDirectGroup(UserEntity currentUser, UUID friendId) {
        if (!friendRepository.existsByUserIdAndFriendId(currentUser.getId(), friendId)) {
            throw new ResourceNotFoundException("Friendship not found");
        }

        List<GroupEntity> allGroups = groupRepository.findAllGroupsByUserId(currentUser.getId());
        GroupEntity directGroup = null;

        for (GroupEntity group : allGroups) {
            if (group.getType() == GroupType.DIRECT &&
                    groupMemberRepository.existsByGroupIdAndUserId(group.getId(), friendId)) {
                directGroup = group;
                break;
            }
        }

        if (directGroup == null) {
            throw new ResourceNotFoundException("DIRECT group not found for this friendship");
        }

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("group_id", directGroup.getId());
        result.put("group_name", directGroup.getName());
        result.put("created_at", directGroup.getCreatedAt());
        return result;
    }

    /**
     * Remove a friend and delete the DIRECT group.
     */
    @Transactional
    public Map<String, String> removeFriend(UserEntity currentUser, UUID friendId) {
        boolean exists = friendRepository.existsByUserIdAndFriendId(currentUser.getId(), friendId) ||
                friendRepository.existsByUserIdAndFriendId(friendId, currentUser.getId());

        if (!exists) {
            throw new ResourceNotFoundException("Friendship not found");
        }

        // Find and delete DIRECT group
        List<GroupEntity> allGroups = groupRepository.findAllGroupsByUserId(currentUser.getId());
        for (GroupEntity group : allGroups) {
            if (group.getType() == GroupType.DIRECT &&
                    groupMemberRepository.existsByGroupIdAndUserId(group.getId(), friendId)) {
                // Delete all related data (cascade handles most, but be explicit for splits)
                List<ExpenseEntity> expenses = expenseRepository.findByGroupIdOrderByCreatedAtDesc(group.getId());
                for (ExpenseEntity expense : expenses) {
                    List<ExpenseItemEntity> items = expenseItemRepository.findByExpenseId(expense.getId());
                    for (ExpenseItemEntity item : items) {
                        List<SplitEntity> splits = splitRepository.findByExpenseItemId(item.getId());
                        splitRepository.deleteAll(splits);
                    }
                    expenseItemRepository.deleteAll(items);
                }
                expenseRepository.deleteAll(expenses);
                groupMemberRepository.deleteByGroupIdAndUserId(group.getId(), currentUser.getId());
                groupMemberRepository.deleteByGroupIdAndUserId(group.getId(), friendId);
                groupRepository.delete(group);
                break;
            }
        }

        // Delete bidirectional friendships
        friendRepository.deleteByUserIdAndFriendId(currentUser.getId(), friendId);
        friendRepository.deleteByUserIdAndFriendId(friendId, currentUser.getId());

        return Map.of("message", "Friend removed successfully");
    }
}
