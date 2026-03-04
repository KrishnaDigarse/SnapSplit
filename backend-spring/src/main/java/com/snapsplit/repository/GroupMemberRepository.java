package com.snapsplit.repository;

import com.snapsplit.entity.GroupMemberEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface GroupMemberRepository extends JpaRepository<GroupMemberEntity, GroupMemberEntity.GroupMemberId> {

    List<GroupMemberEntity> findByGroupId(UUID groupId);

    List<GroupMemberEntity> findByUserId(UUID userId);

    boolean existsByGroupIdAndUserId(UUID groupId, UUID userId);

    void deleteByGroupIdAndUserId(UUID groupId, UUID userId);
}
