# Phase 1 — Entities & Repositories (Data Layer)

## Objective

Map all 10 SQLAlchemy models and 6 Python enums to JPA entities and Spring Data repositories, pointing at the **existing PostgreSQL tables** — no schema modifications.

---

## Python → Spring Boot Mapping

### Enum Mapping

| Python Enum (str, Enum) | Java Enum | PostgreSQL Type | Values |
|---|---|---|---|
| `FriendRequestStatus` | `FriendRequestStatus` | `friendrequeststatus` | PENDING, ACCEPTED, REJECTED |
| `GroupType` | `GroupType` | `grouptype` | GROUP, DIRECT |
| `SourceType` | `SourceType` | `sourcetype` | BILL_IMAGE, MANUAL |
| `ExpenseStatus` | `ExpenseStatus` | `expensestatus` | PENDING, PROCESSING, READY, FAILED |
| `SplitType` | `SplitType` | `splittype` | EQUAL, ITEM, CUSTOM |
| `PaymentMethod` | `PaymentMethod` | `paymentmethod` | CASH, UPI, BANK, OTHER |

**Key detail:** PostgreSQL uses native ENUM types. In JPA, we use `@Enumerated(EnumType.STRING)` with `columnDefinition = "friendrequeststatus"` to tell Hibernate to use the existing PostgreSQL enum type instead of trying to create a VARCHAR column.

### Entity Mapping

| Python Model | JPA Entity | Table | PK Type |
|---|---|---|---|
| `User` | `UserEntity` | `users` | UUID (generated) |
| `FriendRequest` | `FriendRequestEntity` | `friend_requests` | UUID (generated) |
| `Friend` | `FriendEntity` | `friends` | Composite (user_id + friend_id) |
| `Group` | `GroupEntity` | `groups` | UUID (generated) |
| `GroupMember` | `GroupMemberEntity` | `group_members` | Composite (group_id + user_id) |
| `Expense` | `ExpenseEntity` | `expenses` | UUID (generated) |
| `ExpenseItem` | `ExpenseItemEntity` | `expense_items` | UUID (generated) |
| `Split` | `SplitEntity` | `splits` | UUID (generated) |
| `Settlement` | `SettlementEntity` | `settlements` | UUID (generated) |
| `GroupBalance` | `GroupBalanceEntity` | `group_balances` | Composite (group_id + user_id) |

---

## Files Created

### Enums (6 files)

All in `com.snapsplit.enums` package. Each is a simple Java enum matching the PostgreSQL native enum type:

```java
// Example: FriendRequestStatus.java
package com.snapsplit.enums;

public enum FriendRequestStatus {
    PENDING,
    ACCEPTED,
    REJECTED
}
```

---

### Entities (10 files)

All in `com.snapsplit.entity` package.

#### Standard Entities (UUID Primary Key)

These 7 entities have a single UUID primary key with `@GeneratedValue(strategy = GenerationType.UUID)`:

**UserEntity** — The central entity with relationships to everything:
```java
@Entity
@Table(name = "users")
public class UserEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    private String name;
    private String email;              // unique, indexed
    private String passwordHash;       // column = "password_hash"

    // 10 relationship lists:
    // sentFriendRequests, receivedFriendRequests, friends,
    // groupsCreated, groupMemberships, expensesCreated,
    // splits, settlementsPaid, settlementsReceived, groupBalances
}
```

**Python equivalent:**
```python
class User(Base):
    __tablename__ = "users"
    id = Column(GUID, primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
```

---

**ExpenseEntity** — Uses `BigDecimal` for money (not `float`):
```java
@Column(precision = 10, scale = 2)
private BigDecimal subtotal;        // NUMERIC(10,2) in PostgreSQL

@Column(precision = 10, scale = 2)
private BigDecimal tax;

@Column(name = "total_amount", precision = 10, scale = 2)
private BigDecimal totalAmount;
```

**Why `BigDecimal`?** Python's `Numeric(10, 2)` maps to PostgreSQL's `NUMERIC(10,2)`. In Java, `float`/`double` would introduce floating-point errors in financial calculations. `BigDecimal` provides exact decimal arithmetic.

---

**SettlementEntity** — Two user relationships (payer and payee):
```java
@ManyToOne(fetch = FetchType.LAZY)
@JoinColumn(name = "paid_by", nullable = false)
private UserEntity payer;

@ManyToOne(fetch = FetchType.LAZY)
@JoinColumn(name = "paid_to", nullable = false)
private UserEntity payee;
```

**Python equivalent:**
```python
paid_by = Column(GUID, ForeignKey("users.id"))
paid_to = Column(GUID, ForeignKey("users.id"))
payer = relationship("User", foreign_keys=[paid_by])
payee = relationship("User", foreign_keys=[paid_to])
```

---

#### Composite Primary Key Entities

These 3 entities use `@IdClass` with a static inner class for their composite keys:

**FriendEntity** — PK = (user_id, friend_id):
```java
@Entity
@Table(name = "friends")
@IdClass(FriendEntity.FriendId.class)
public class FriendEntity {

    @Id
    @Column(name = "user_id")
    private UUID userId;

    @Id
    @Column(name = "friend_id")
    private UUID friendId;

    // Relationships use insertable=false, updatable=false
    // to avoid conflicts with the @Id columns
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", insertable = false, updatable = false)
    private UserEntity user;

    // Static inner class for composite PK
    @NoArgsConstructor
    @AllArgsConstructor
    @EqualsAndHashCode
    public static class FriendId implements Serializable {
        private UUID userId;
        private UUID friendId;
    }
}
```

**Why `insertable = false, updatable = false`?** When a column is both part of the primary key (`@Id`) and a foreign key (`@JoinColumn`), JPA needs to know which mapping "owns" the column. The `@Id` owns it; the `@ManyToOne` is read-only.

**Python equivalent:**
```python
class Friend(Base):
    __table_args__ = (
        PrimaryKeyConstraint("user_id", "friend_id"),
    )
    user_id = Column(GUID, ForeignKey("users.id"))
    friend_id = Column(GUID, ForeignKey("users.id"))
```

The same pattern is used for `GroupMemberEntity` (group_id + user_id) and `GroupBalanceEntity` (group_id + user_id).

---

### JPA Annotations Reference

| Annotation | Purpose | Python Equivalent |
|---|---|---|
| `@Entity` | Marks class as JPA entity | `class X(Base):` |
| `@Table(name = "...")` | Maps to specific table | `__tablename__ = "..."` |
| `@Id` | Primary key | `primary_key=True` |
| `@GeneratedValue(UUID)` | Auto-generate UUID | `default=uuid.uuid4` |
| `@Column(name, nullable, unique, length)` | Column config | `Column(String(255), nullable=False)` |
| `@ManyToOne(fetch = LAZY)` | FK relationship | `relationship("X")` with FK |
| `@OneToMany(mappedBy, cascade, orphanRemoval)` | Inverse relationship | `relationship("X", back_populates="y", cascade="all, delete-orphan")` |
| `@Enumerated(EnumType.STRING)` | Store enum as string | `Enum as SQLEnum` |
| `@CreationTimestamp` | Auto-set on insert | `default=datetime.utcnow` |
| `@UpdateTimestamp` | Auto-set on update | `onupdate=datetime.utcnow` |
| `@IdClass` | Composite PK | `PrimaryKeyConstraint(...)` |
| `@Index` | Database index | `Index("idx_...", "column")` |

---

### Repositories (10 files)

All in `com.snapsplit.repository` package. Each extends `JpaRepository<Entity, PrimaryKeyType>`.

**What you get for free with JpaRepository:**
- `save(entity)` — insert or update
- `findById(id)` — find by primary key
- `findAll()` — list all
- `deleteById(id)` — delete
- `count()` — count rows
- `existsById(id)` — existence check

**Custom query methods added:**

| Repository | Custom Methods |
|---|---|
| `UserRepository` | `findByEmail()`, `existsByEmail()` |
| `FriendRequestRepository` | `findByReceiverIdAndStatus()`, `findBySenderIdAndReceiverId()`, `existsBySenderIdAndReceiverIdAndStatus()` |
| `FriendRepository` | `findByUserId()`, `existsByUserIdAndFriendId()`, `deleteByUserIdAndFriendId()`, `findFriendIdsByUserId()` |
| `GroupRepository` | `findActiveGroupsByUserId()` (JPQL), `findAllGroupsByUserId()` (JPQL) |
| `GroupMemberRepository` | `findByGroupId()`, `existsByGroupIdAndUserId()`, `deleteByGroupIdAndUserId()` |
| `ExpenseRepository` | `findByGroupIdOrderByCreatedAtDesc()` |
| `ExpenseItemRepository` | `findByExpenseId()` |
| `SplitRepository` | `findByExpenseItemId()`, `findByUserId()`, `findByGroupId()` (JPQL) |
| `SettlementRepository` | `findByGroupIdOrderByCreatedAtDesc()` |
| `GroupBalanceRepository` | `findByGroupId()`, `findByGroupIdAndUserId()` |

**Spring Data magic:** Method names like `findByGroupIdOrderByCreatedAtDesc` are parsed automatically by Spring — no SQL needed. For complex joins, we use `@Query` with JPQL.

---

### Lombok Annotations Used

Every entity uses these Lombok annotations to eliminate boilerplate:

| Annotation | What It Generates |
|---|---|
| `@Getter` | All getter methods |
| `@Setter` | All setter methods |
| `@NoArgsConstructor` | Empty constructor (required by JPA) |
| `@AllArgsConstructor` | Constructor with all fields |
| `@Builder` | Builder pattern for clean object creation |
| `@EqualsAndHashCode` | On composite PK inner classes |

**Without Lombok**, the `UserEntity` class would be ~300 lines of boilerplate. **With Lombok**, it's ~75 lines of pure domain logic.

---

## Build Verification

```
$ mvn compile
[INFO] Compiling 38 source files with javac [debug parameters release 21]
[INFO] BUILD SUCCESS
[INFO] Total time: 9.088 s
```

**38 files = 12 (Phase 0) + 6 (enums) + 10 (entities) + 10 (repositories)**

---

## Key Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Entity suffix | `*Entity` (e.g., `UserEntity`) | Avoids collision with DTOs (`UserResponse`) and keeps naming clear |
| Money type | `BigDecimal` | Exact arithmetic for financial data; avoids floating-point rounding errors |
| Fetch strategy | `FetchType.LAZY` on all `@ManyToOne` | Prevents N+1 query issues; load related data only when accessed |
| Composite PK pattern | `@IdClass` with static inner class | Cleaner than `@EmbeddedId` for simple 2-column keys |
| Enum storage | `@Enumerated(STRING)` + `columnDefinition` | Matches existing PostgreSQL native ENUM types |
| Cascade rules | Match Python's `cascade="all, delete-orphan"` | `CascadeType.ALL` + `orphanRemoval = true` |
