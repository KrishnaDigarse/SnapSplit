package com.snapsplit.repository;

import com.snapsplit.entity.FriendEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface FriendRepository extends JpaRepository<FriendEntity, FriendEntity.FriendId> {

    List<FriendEntity> findByUserId(UUID userId);

    boolean existsByUserIdAndFriendId(UUID userId, UUID friendId);

    void deleteByUserIdAndFriendId(UUID userId, UUID friendId);

    @Query("SELECT f.friendId FROM FriendEntity f WHERE f.userId = :userId")
    List<UUID> findFriendIdsByUserId(@Param("userId") UUID userId);
}
