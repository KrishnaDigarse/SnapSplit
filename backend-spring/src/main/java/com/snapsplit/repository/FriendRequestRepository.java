package com.snapsplit.repository;

import com.snapsplit.entity.FriendRequestEntity;
import com.snapsplit.enums.FriendRequestStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface FriendRequestRepository extends JpaRepository<FriendRequestEntity, UUID> {

    List<FriendRequestEntity> findByReceiverIdAndStatus(UUID receiverId, FriendRequestStatus status);

    List<FriendRequestEntity> findBySenderIdAndStatus(UUID senderId, FriendRequestStatus status);

    Optional<FriendRequestEntity> findBySenderIdAndReceiverId(UUID senderId, UUID receiverId);

    boolean existsBySenderIdAndReceiverIdAndStatus(UUID senderId, UUID receiverId, FriendRequestStatus status);
}
