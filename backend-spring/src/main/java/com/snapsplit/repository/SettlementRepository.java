package com.snapsplit.repository;

import com.snapsplit.entity.SettlementEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.UUID;

@Repository
public interface SettlementRepository extends JpaRepository<SettlementEntity, UUID> {

    List<SettlementEntity> findByGroupIdOrderByCreatedAtDesc(UUID groupId);
}
