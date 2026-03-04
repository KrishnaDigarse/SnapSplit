package com.snapsplit.repository;

import com.snapsplit.entity.ExpenseItemEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface ExpenseItemRepository extends JpaRepository<ExpenseItemEntity, UUID> {

    List<ExpenseItemEntity> findByExpenseId(UUID expenseId);
}
