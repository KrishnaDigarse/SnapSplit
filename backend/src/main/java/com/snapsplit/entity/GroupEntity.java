package com.snapsplit.entity;

import com.snapsplit.enums.GroupType;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "groups", indexes = {
        @Index(name = "idx_groups_created_by", columnList = "created_by")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class GroupEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false, length = 255)
    private String name;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "created_by")
    private UserEntity creator;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, columnDefinition = "grouptype")
    private GroupType type;

    @Column(name = "is_archived", nullable = false)
    private Boolean isArchived;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    // ── Relationships ──

    @OneToMany(mappedBy = "group", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<GroupMemberEntity> members;

    @OneToMany(mappedBy = "group", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<ExpenseEntity> expenses;

    @OneToMany(mappedBy = "group", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<SettlementEntity> settlements;

    @OneToMany(mappedBy = "group", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<GroupBalanceEntity> balances;

    @PrePersist
    public void prePersist() {
        if (type == null)
            type = GroupType.GROUP;
        if (isArchived == null)
            isArchived = false;
    }
}
