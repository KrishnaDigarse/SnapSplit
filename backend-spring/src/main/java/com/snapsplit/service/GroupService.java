package com.snapsplit.service;

import com.snapsplit.dto.request.GroupCreateRequest;
import com.snapsplit.dto.request.GroupMemberAddRequest;
import com.snapsplit.dto.response.GroupResponse;
import com.snapsplit.entity.*;
import com.snapsplit.enums.GroupType;
import com.snapsplit.exception.BadRequestException;
import com.snapsplit.exception.ResourceNotFoundException;
import com.snapsplit.exception.UnauthorizedException;
import com.snapsplit.repository.*;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;

/**
 * Group service — equivalent to Python's group_service.py
 */
@Service
public class GroupService {

    private final GroupRepository groupRepository;
    private final GroupMemberRepository groupMemberRepository;
    private final UserRepository userRepository;
    private final ExpenseRepository expenseRepository;
    private final ExpenseItemRepository expenseItemRepository;
    private final SplitRepository splitRepository;

    public GroupService(GroupRepository groupRepository,
            GroupMemberRepository groupMemberRepository,
            UserRepository userRepository,
            ExpenseRepository expenseRepository,
            ExpenseItemRepository expenseItemRepository,
            SplitRepository splitRepository) {
        this.groupRepository = groupRepository;
        this.groupMemberRepository = groupMemberRepository;
        this.userRepository = userRepository;
        this.expenseRepository = expenseRepository;
        this.expenseItemRepository = expenseItemRepository;
        this.splitRepository = splitRepository;
    }

    @Transactional
    public GroupResponse createGroup(UserEntity currentUser, GroupCreateRequest request) {
        GroupEntity group = GroupEntity.builder()
                .name(request.getName())
                .creator(currentUser)
                .type(GroupType.GROUP)
                .isArchived(false)
                .build();
        GroupEntity saved = groupRepository.save(group);

        groupMemberRepository.save(GroupMemberEntity.builder()
                .groupId(saved.getId()).userId(currentUser.getId()).build());

        return toGroupResponse(saved, 1);
    }

    @Transactional
    public Map<String, String> addMember(UserEntity currentUser, UUID groupId, GroupMemberAddRequest request) {
        GroupEntity group = findGroupOrThrow(groupId);
        assertCreator(group, currentUser);

        userRepository.findById(request.getUserId())
                .orElseThrow(() -> new ResourceNotFoundException("User not found"));

        if (groupMemberRepository.existsByGroupIdAndUserId(groupId, request.getUserId())) {
            throw new BadRequestException("User is already a member");
        }

        groupMemberRepository.save(GroupMemberEntity.builder()
                .groupId(groupId).userId(request.getUserId()).build());

        return Map.of("message", "Member added successfully");
    }

    public List<GroupResponse> getGroups(UserEntity currentUser) {
        List<GroupEntity> groups = groupRepository.findActiveGroupsByUserId(currentUser.getId());

        return groups.stream()
                .filter(g -> g.getType() == GroupType.GROUP)
                .map(g -> {
                    int memberCount = groupMemberRepository.findByGroupId(g.getId()).size();
                    return toGroupResponse(g, memberCount);
                }).toList();
    }

    public GroupResponse.GroupDetailResponse getGroupDetail(UserEntity currentUser, UUID groupId) {
        GroupEntity group = findGroupOrThrow(groupId);
        assertMember(groupId, currentUser);

        List<GroupMemberEntity> members = groupMemberRepository.findByGroupId(groupId);
        List<GroupResponse.MemberDetail> memberList = members.stream().map(m -> GroupResponse.MemberDetail.builder()
                .userId(m.getUser().getId())
                .userName(m.getUser().getName())
                .userEmail(m.getUser().getEmail())
                .joinedAt(m.getJoinedAt())
                .build()).toList();

        return GroupResponse.GroupDetailResponse.builder()
                .id(group.getId())
                .name(group.getName())
                .createdBy(group.getCreator() != null ? group.getCreator().getId() : null)
                .type(group.getType())
                .isArchived(group.getIsArchived())
                .createdAt(group.getCreatedAt())
                .memberCount(memberList.size())
                .members(memberList)
                .build();
    }

    @Transactional
    public Map<String, String> deleteGroup(UserEntity currentUser, UUID groupId) {
        GroupEntity group = findGroupOrThrow(groupId);
        assertCreator(group, currentUser);

        // Delete all related data
        List<ExpenseEntity> expenses = expenseRepository.findByGroupIdOrderByCreatedAtDesc(groupId);
        for (ExpenseEntity expense : expenses) {
            List<ExpenseItemEntity> items = expenseItemRepository.findByExpenseId(expense.getId());
            for (ExpenseItemEntity item : items) {
                splitRepository.deleteAll(splitRepository.findByExpenseItemId(item.getId()));
            }
            expenseItemRepository.deleteAll(items);
        }
        expenseRepository.deleteAll(expenses);

        List<GroupMemberEntity> members = groupMemberRepository.findByGroupId(groupId);
        groupMemberRepository.deleteAll(members);

        groupRepository.delete(group);

        return Map.of("message", "Group deleted successfully");
    }

    @Transactional
    public Map<String, String> removeMember(UserEntity currentUser, UUID groupId, UUID userId) {
        GroupEntity group = findGroupOrThrow(groupId);
        assertCreator(group, currentUser);

        if (userId.equals(currentUser.getId())) {
            throw new BadRequestException("Cannot remove yourself from the group");
        }

        if (!groupMemberRepository.existsByGroupIdAndUserId(groupId, userId)) {
            throw new ResourceNotFoundException("User is not a member of this group");
        }

        groupMemberRepository.deleteByGroupIdAndUserId(groupId, userId);
        return Map.of("message", "Member removed successfully");
    }

    @Transactional
    public Map<String, String> leaveGroup(UserEntity currentUser, UUID groupId) {
        GroupEntity group = findGroupOrThrow(groupId);

        if (group.getCreator() != null && group.getCreator().getId().equals(currentUser.getId())) {
            throw new BadRequestException("Group creators cannot leave the group. You must delete the group instead.");
        }

        if (!groupMemberRepository.existsByGroupIdAndUserId(groupId, currentUser.getId())) {
            throw new BadRequestException("You are not a member of this group");
        }

        groupMemberRepository.deleteByGroupIdAndUserId(groupId, currentUser.getId());
        return Map.of("message", "Left group successfully");
    }

    // ── Helpers ──

    private GroupEntity findGroupOrThrow(UUID groupId) {
        return groupRepository.findById(groupId)
                .orElseThrow(() -> new ResourceNotFoundException("Group not found"));
    }

    private void assertCreator(GroupEntity group, UserEntity user) {
        if (group.getCreator() == null || !group.getCreator().getId().equals(user.getId())) {
            throw new UnauthorizedException("Only group creator can perform this action");
        }
    }

    public void assertMember(UUID groupId, UserEntity user) {
        if (!groupMemberRepository.existsByGroupIdAndUserId(groupId, user.getId())) {
            throw new UnauthorizedException("Not a member of this group");
        }
    }

    private GroupResponse toGroupResponse(GroupEntity group, int memberCount) {
        return GroupResponse.builder()
                .id(group.getId())
                .name(group.getName())
                .createdBy(group.getCreator() != null ? group.getCreator().getId() : null)
                .type(group.getType())
                .isArchived(group.getIsArchived())
                .createdAt(group.getCreatedAt())
                .memberCount(memberCount)
                .build();
    }
}
