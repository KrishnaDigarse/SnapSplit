package com.snapsplit.entity;

import com.snapsplit.enums.ExpenseStatus;
import com.snapsplit.enums.SourceType;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "expenses", indexes = {
        @Index(name = "idx_expenses_group_id", columnList = "group_id"),
        @Index(name = "idx_expenses_created_by", columnList = "created_by")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ExpenseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "group_id", nullable = false)
    private GroupEntity group;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "created_by")
    private UserEntity creator;

    @Enumerated(EnumType.STRING)
    @Column(name = "source_type", nullable = false, columnDefinition = "sourcetype")
    private SourceType sourceType;

    @Column(name = "image_url", length = 500)
    private String imageUrl;

    @Column(name = "raw_ocr_text", columnDefinition = "TEXT")
    private String rawOcrText;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false, columnDefinition = "expensestatus")
    private ExpenseStatus status;

    @Column(name = "is_edited", nullable = false)
    private Boolean isEdited;

    @Column(precision = 10, scale = 2)
    private BigDecimal subtotal;

    @Column(precision = 10, scale = 2)
    private BigDecimal tax;

    @Column(name = "total_amount", precision = 10, scale = 2)
    private BigDecimal totalAmount;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    // ── Relationships ──

    @OneToMany(mappedBy = "expense", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<ExpenseItemEntity> items;

    @PrePersist
    public void prePersist() {
        if (status == null)
            status = ExpenseStatus.PENDING;
        if (isEdited == null)
            isEdited = false;
        if (tax == null)
            tax = BigDecimal.ZERO;
    }

    /**
     * Convenience method matching Python's @property creator_name
     */
    public String getCreatorName() {
        return creator != null ? creator.getName() : null;
    }
}
