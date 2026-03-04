package com.snapsplit.repository;

import com.snapsplit.entity.GroupBalanceEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Repository
public interface GroupBalanceRepository extends JpaRepository<GroupBalanceEntity, GroupBalanceEntity.GroupBalanceId> {

    List<GroupBalanceEntity> findByGroupId(UUID groupId);

    Optional<GroupBalanceEntity> findByGroupIdAndUserId(UUID groupId, UUID userId);
}
