package com.snapsplit.entity;

import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.util.List;
import java.util.UUID;

@Entity
@Table(name = "expense_items", indexes = {
        @Index(name = "idx_expense_items_expense_id", columnList = "expense_id")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ExpenseItemEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "expense_id", nullable = false)
    private ExpenseEntity expense;

    @Column(name = "item_name", nullable = false, length = 255)
    private String itemName;

    @Column(nullable = false)
    private Integer quantity;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal price;

    // ── Relationships ──

    @OneToMany(mappedBy = "expenseItem", cascade = CascadeType.ALL, orphanRemoval = true)
    private List<SplitEntity> splits;

    @PrePersist
    public void prePersist() {
        if (quantity == null)
            quantity = 1;
    }
}
