package com.snapsplit.repository;

import com.snapsplit.entity.SplitEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface SplitRepository extends JpaRepository<SplitEntity, UUID> {

    List<SplitEntity> findByExpenseItemId(UUID expenseItemId);

    List<SplitEntity> findByUserId(UUID userId);

    @Query("SELECT s FROM SplitEntity s WHERE s.expenseItem.expense.group.id = :groupId")
    List<SplitEntity> findByGroupId(@Param("groupId") UUID groupId);
}
