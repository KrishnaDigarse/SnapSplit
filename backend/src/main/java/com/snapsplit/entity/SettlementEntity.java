package com.snapsplit.entity;

import com.snapsplit.enums.PaymentMethod;
import jakarta.persistence.*;
import lombok.*;
import org.hibernate.annotations.CreationTimestamp;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

@Entity
@Table(name = "settlements", indexes = {
        @Index(name = "idx_settlements_group_id", columnList = "group_id"),
        @Index(name = "idx_settlements_paid_by", columnList = "paid_by"),
        @Index(name = "idx_settlements_paid_to", columnList = "paid_to")
})
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class SettlementEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "group_id", nullable = false)
    private GroupEntity group;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "paid_by", nullable = false)
    private UserEntity payer;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "paid_to", nullable = false)
    private UserEntity payee;

    @Column(nullable = false, precision = 10, scale = 2)
    private BigDecimal amount;

    @Enumerated(EnumType.STRING)
    @Column(name = "payment_method", nullable = false, columnDefinition = "paymentmethod")
    private PaymentMethod paymentMethod;

    @Column(length = 500)
    private String note;

    @CreationTimestamp
    @Column(name = "created_at", nullable = false, updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    public void prePersist() {
        if (paymentMethod == null)
            paymentMethod = PaymentMethod.CASH;
    }
}
