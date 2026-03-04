package com.snapsplit.service;

import com.snapsplit.dto.request.GroupCreateRequest;
import com.snapsplit.dto.response.GroupResponse;
import com.snapsplit.entity.*;
import com.snapsplit.enums.GroupType;
import com.snapsplit.exception.BadRequestException;
import com.snapsplit.exception.ResourceNotFoundException;
import com.snapsplit.exception.UnauthorizedException;
import com.snapsplit.repository.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.time.LocalDateTime;
import java.util.*;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class GroupServiceTest {

    @Mock
    private GroupRepository groupRepository;
    @Mock
    private GroupMemberRepository groupMemberRepository;
    @Mock
    private UserRepository userRepository;
    @Mock
    private ExpenseRepository expenseRepository;
    @Mock
    private ExpenseItemRepository expenseItemRepository;
    @Mock
    private SplitRepository splitRepository;
    @InjectMocks
    private GroupService groupService;

    private UserEntity creator;
    private UserEntity member;
    private GroupEntity group;

    @BeforeEach
    void setUp() {
        creator = UserEntity.builder().id(UUID.randomUUID()).name("Creator").email("creator@test.com").build();
        member = UserEntity.builder().id(UUID.randomUUID()).name("Member").email("member@test.com").build();
        group = GroupEntity.builder()
                .id(UUID.randomUUID()).name("Test Group").creator(creator)
                .type(GroupType.GROUP).isArchived(false).createdAt(LocalDateTime.now()).build();
    }

    @Nested
    @DisplayName("createGroup()")
    class CreateTests {
        @Test
        @DisplayName("should create group and add creator as member")
        void create_success() {
            GroupCreateRequest req = new GroupCreateRequest();
            req.setName("My Group");

            when(groupRepository.save(any())).thenAnswer(inv -> {
                GroupEntity g = inv.getArgument(0);
                g.setId(UUID.randomUUID());
                g.setCreatedAt(LocalDateTime.now());
                return g;
            });
            when(groupMemberRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

            GroupResponse resp = groupService.createGroup(creator, req);

            assertThat(resp.getName()).isEqualTo("My Group");
            assertThat(resp.getType()).isEqualTo(GroupType.GROUP);
            assertThat(resp.getMemberCount()).isEqualTo(1);
            verify(groupMemberRepository).save(any());
        }
    }

    @Nested
    @DisplayName("addMember()")
    class AddMemberTests {
        @Test
        @DisplayName("should add new member")
        void addMember_success() {
            when(groupRepository.findById(group.getId())).thenReturn(Optional.of(group));
            when(userRepository.findById(member.getId())).thenReturn(Optional.of(member));
            when(groupMemberRepository.existsByGroupIdAndUserId(group.getId(), member.getId())).thenReturn(false);
            when(groupMemberRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

            var req = new com.snapsplit.dto.request.GroupMemberAddRequest();
            req.setUserId(member.getId());

            var result = groupService.addMember(creator, group.getId(), req);
            assertThat(result.get("message")).isEqualTo("Member added successfully");
        }

        @Test
        @DisplayName("should throw when non-creator tries to add")
        void addMember_notCreator() {
            when(groupRepository.findById(group.getId())).thenReturn(Optional.of(group));

            var req = new com.snapsplit.dto.request.GroupMemberAddRequest();
            req.setUserId(member.getId());

            assertThatThrownBy(() -> groupService.addMember(member, group.getId(), req))
                    .isInstanceOf(UnauthorizedException.class);
        }

        @Test
        @DisplayName("should throw when user already a member")
        void addMember_alreadyMember() {
            when(groupRepository.findById(group.getId())).thenReturn(Optional.of(group));
            when(userRepository.findById(member.getId())).thenReturn(Optional.of(member));
            when(groupMemberRepository.existsByGroupIdAndUserId(group.getId(), member.getId())).thenReturn(true);

            var req = new com.snapsplit.dto.request.GroupMemberAddRequest();
            req.setUserId(member.getId());

            assertThatThrownBy(() -> groupService.addMember(creator, group.getId(), req))
                    .isInstanceOf(BadRequestException.class)
                    .hasMessageContaining("already a member");
        }
    }

    @Nested
    @DisplayName("leaveGroup()")
    class LeaveTests {
        @Test
        @DisplayName("should throw when creator tries to leave")
        void leave_creatorForbidden() {
            when(groupRepository.findById(group.getId())).thenReturn(Optional.of(group));

            assertThatThrownBy(() -> groupService.leaveGroup(creator, group.getId()))
                    .isInstanceOf(BadRequestException.class)
                    .hasMessageContaining("creators cannot leave");
        }
    }

    @Nested
    @DisplayName("deleteGroup()")
    class DeleteTests {
        @Test
        @DisplayName("should throw when group not found")
        void delete_notFound() {
            UUID fakeId = UUID.randomUUID();
            when(groupRepository.findById(fakeId)).thenReturn(Optional.empty());

            assertThatThrownBy(() -> groupService.deleteGroup(creator, fakeId))
                    .isInstanceOf(ResourceNotFoundException.class);
        }
    }
}
