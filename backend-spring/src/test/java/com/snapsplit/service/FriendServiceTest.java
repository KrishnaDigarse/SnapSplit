package com.snapsplit.service;

import com.snapsplit.dto.request.FriendRequestCreateRequest;
import com.snapsplit.dto.response.FriendRequestResponse;
import com.snapsplit.dto.response.FriendResponse;
import com.snapsplit.entity.*;
import com.snapsplit.enums.FriendRequestStatus;
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

import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class FriendServiceTest {

    @Mock
    private UserRepository userRepository;
    @Mock
    private FriendRequestRepository friendRequestRepository;
    @Mock
    private FriendRepository friendRepository;
    @Mock
    private GroupRepository groupRepository;
    @Mock
    private GroupMemberRepository groupMemberRepository;
    @Mock
    private ExpenseRepository expenseRepository;
    @Mock
    private ExpenseItemRepository expenseItemRepository;
    @Mock
    private SplitRepository splitRepository;
    @InjectMocks
    private FriendService friendService;

    private UserEntity sender;
    private UserEntity receiver;

    @BeforeEach
    void setUp() {
        sender = UserEntity.builder().id(UUID.randomUUID()).name("Sender").email("sender@test.com").build();
        receiver = UserEntity.builder().id(UUID.randomUUID()).name("Receiver").email("receiver@test.com").build();
    }

    @Nested
    @DisplayName("sendFriendRequest()")
    class SendRequestTests {

        @Test
        @DisplayName("should send request successfully")
        void send_success() {
            FriendRequestCreateRequest request = new FriendRequestCreateRequest();
            request.setFriendEmail("receiver@test.com");

            when(userRepository.findByEmail("receiver@test.com")).thenReturn(Optional.of(receiver));
            when(friendRequestRepository.existsBySenderIdAndReceiverIdAndStatus(any(), any(), any())).thenReturn(false);
            when(friendRepository.existsByUserIdAndFriendId(any(), any())).thenReturn(false);
            when(friendRequestRepository.save(any())).thenAnswer(inv -> {
                FriendRequestEntity e = inv.getArgument(0);
                e.setId(UUID.randomUUID());
                return e;
            });

            FriendRequestResponse resp = friendService.sendFriendRequest(sender, request);
            assertThat(resp.getStatus()).isEqualTo(FriendRequestStatus.PENDING);
            verify(friendRequestRepository).save(any(FriendRequestEntity.class));
        }

        @Test
        @DisplayName("should throw when sending to self")
        void send_toSelf() {
            FriendRequestCreateRequest request = new FriendRequestCreateRequest();
            request.setFriendEmail("sender@test.com");

            when(userRepository.findByEmail("sender@test.com")).thenReturn(Optional.of(sender));

            assertThatThrownBy(() -> friendService.sendFriendRequest(sender, request))
                    .isInstanceOf(BadRequestException.class)
                    .hasMessageContaining("yourself");
        }

        @Test
        @DisplayName("should throw when user not found")
        void send_notFound() {
            FriendRequestCreateRequest request = new FriendRequestCreateRequest();
            request.setFriendEmail("unknown@test.com");

            when(userRepository.findByEmail("unknown@test.com")).thenReturn(Optional.empty());

            assertThatThrownBy(() -> friendService.sendFriendRequest(sender, request))
                    .isInstanceOf(ResourceNotFoundException.class);
        }

        @Test
        @DisplayName("should throw when already friends")
        void send_alreadyFriends() {
            FriendRequestCreateRequest request = new FriendRequestCreateRequest();
            request.setFriendEmail("receiver@test.com");

            when(userRepository.findByEmail("receiver@test.com")).thenReturn(Optional.of(receiver));
            when(friendRequestRepository.existsBySenderIdAndReceiverIdAndStatus(any(), any(), any())).thenReturn(false);
            when(friendRepository.existsByUserIdAndFriendId(sender.getId(), receiver.getId())).thenReturn(true);

            assertThatThrownBy(() -> friendService.sendFriendRequest(sender, request))
                    .isInstanceOf(BadRequestException.class)
                    .hasMessageContaining("Already friends");
        }
    }

    @Nested
    @DisplayName("acceptFriendRequest()")
    class AcceptTests {

        @Test
        @DisplayName("should accept and create DIRECT group")
        void accept_success() {
            UUID requestId = UUID.randomUUID();
            FriendRequestEntity req = FriendRequestEntity.builder()
                    .id(requestId).sender(sender).receiver(receiver)
                    .status(FriendRequestStatus.PENDING).build();

            when(friendRequestRepository.findById(requestId)).thenReturn(Optional.of(req));
            when(friendRequestRepository.save(any())).thenReturn(req);
            when(friendRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));
            when(groupRepository.save(any())).thenAnswer(inv -> {
                GroupEntity g = inv.getArgument(0);
                g.setId(UUID.randomUUID());
                return g;
            });
            when(groupMemberRepository.save(any())).thenAnswer(inv -> inv.getArgument(0));

            var result = friendService.acceptFriendRequest(receiver, requestId);

            assertThat(result.get("message")).isEqualTo("Friend request accepted");
            assertThat(result).containsKey("direct_group_id");
            verify(friendRepository, times(2)).save(any()); // bidirectional
            verify(groupRepository).save(any());
            verify(groupMemberRepository, times(2)).save(any());
        }

        @Test
        @DisplayName("should throw when not the receiver")
        void accept_notReceiver() {
            UUID requestId = UUID.randomUUID();
            FriendRequestEntity req = FriendRequestEntity.builder()
                    .id(requestId).sender(sender).receiver(receiver)
                    .status(FriendRequestStatus.PENDING).build();

            when(friendRequestRepository.findById(requestId)).thenReturn(Optional.of(req));

            assertThatThrownBy(() -> friendService.acceptFriendRequest(sender, requestId))
                    .isInstanceOf(UnauthorizedException.class);
        }
    }

    @Nested
    @DisplayName("getFriends()")
    class GetFriendsTests {

        @Test
        @DisplayName("should return list of friends")
        void getFriends_success() {
            FriendEntity f = FriendEntity.builder()
                    .userId(sender.getId()).friendId(receiver.getId())
                    .friend(receiver).build();

            when(friendRepository.findByUserId(sender.getId())).thenReturn(List.of(f));

            List<FriendResponse> friends = friendService.getFriends(sender);

            assertThat(friends).hasSize(1);
            assertThat(friends.get(0).getFriendName()).isEqualTo("Receiver");
        }
    }
}
