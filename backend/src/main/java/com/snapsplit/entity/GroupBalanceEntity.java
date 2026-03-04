package com.snapsplit.entity;

import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.UpdateTimestamp;

import java.io.Serializable;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "group_balances")
@IdClass(GroupBalanceEntity.GroupBalanceId.class)
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class GroupBalanceEntity {

    @Id
    @Column(name = "group_id", nullable = false)
    private UUID groupId;

    @Id
    @Column(name = "user_id", nullable = false)
    private UUID userId;

    @Column(name = "net_balance", nullable = false, precision = 10, scale = 2)
    private BigDecimal netBalance;

    @UpdateTimestamp
    @Column(name = "updated_at", nullable = false)
    private LocalDateTime updatedAt;

    // ── Relationships ──

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "group_id", insertable = false, updatable = false)
    private GroupEntity group;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", insertable = false, updatable = false)
    private UserEntity user;

    @PrePersist
    public void prePersist() {
        if (netBalance == null)
            netBalance = BigDecimal.ZERO;
    }

    // ── Composite Primary Key class ──

    @NoArgsConstructor
    @AllArgsConstructor
    @EqualsAndHashCode
    public static class GroupBalanceId implements Serializable {
        private UUID groupId;
        private UUID userId;
    }
}
