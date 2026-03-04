package com.snapsplit.repository;

import com.snapsplit.entity.GroupEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface GroupRepository extends JpaRepository<GroupEntity, UUID> {

    @Query("SELECT g FROM GroupEntity g JOIN g.members m WHERE m.userId = :userId AND g.isArchived = false")
    List<GroupEntity> findActiveGroupsByUserId(@Param("userId") UUID userId);

    @Query("SELECT g FROM GroupEntity g JOIN g.members m WHERE m.userId = :userId")
    List<GroupEntity> findAllGroupsByUserId(@Param("userId") UUID userId);
}
