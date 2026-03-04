# Phase 3 — Core API Controllers & Services

## Objective

Migrate all REST API endpoints from Python/FastAPI to Spring Boot, maintaining identical paths, HTTP methods, request/response formats, and error messages for frontend compatibility.

---

## Python → Spring Boot Endpoint Map

### Friends API (`/api/v1/friends`)

| Method | Path | Python | Java |
|---|---|---|---|
| POST | `/request` | `friends.send_friend_request()` | `FriendController.sendFriendRequest()` |
| POST | `/request/{id}/accept` | `friends.accept_friend_request()` | `FriendController.acceptFriendRequest()` |
| POST | `/request/{id}/reject` | `friends.reject_friend_request()` | `FriendController.rejectFriendRequest()` |
| GET | `/requests` | `friends.get_pending_requests()` | `FriendController.getPendingRequests()` |
| GET | (root) | `friends.get_friends()` | `FriendController.getFriends()` |
| GET | `/{id}/direct-group` | `friends.get_direct_group()` | `FriendController.getDirectGroup()` |
| DELETE | `/{id}` | `friends.remove_friend()` | `FriendController.removeFriend()` |

### Groups API (`/api/v1/groups`)

| Method | Path | Python | Java |
|---|---|---|---|
| POST | (root) | `groups.create_group()` | `GroupController.createGroup()` |
| POST | `/{id}/add-member` | `groups.add_member()` | `GroupController.addMember()` |
| GET | (root) | `groups.get_groups()` | `GroupController.getGroups()` |
| GET | `/{id}` | `groups.get_group()` | `GroupController.getGroup()` |
| DELETE | `/{id}` | `groups.delete_group()` | `GroupController.deleteGroup()` |
| DELETE | `/{id}/members/{uid}` | `groups.remove_member()` | `GroupController.removeMember()` |
| POST | `/{id}/leave` | `groups.leave_group()` | `GroupController.leaveGroup()` |
| GET | `/{id}/expenses` | `groups.get_group_expenses()` | `GroupController.getGroupExpenses()` |
| GET | `/{id}/balances` | `groups.get_group_balances()` | `GroupController.getGroupBalances()` |

### Expenses API (`/api/v1/expenses`)

| Method | Path | Python | Java |
|---|---|---|---|
| POST | `/manual` | `expenses.create_manual_expense()` | `ExpenseController.createManualExpense()` |
| GET | `/{id}` | `expenses.get_expense()` | `ExpenseController.getExpense()` |
| GET | `/group/{id}` | `expenses.get_group_expenses()` | `ExpenseController.getGroupExpenses()` |
| PUT | `/{id}` | `expenses.update_expense()` | `ExpenseController.updateExpense()` |

### Settlements API (`/api/v1/settlements`)

| Method | Path | Python | Java |
|---|---|---|---|
| POST | (root) | `settlements.create_settlement()` | `SettlementController.createSettlement()` |
| GET | `/balances/{id}` | `settlements.get_group_balances()` | `SettlementController.getGroupFinancials()` |

**Total: 22 endpoints migrated**

---

## Files Created (21 files)

### Request DTOs (6 files in `dto/request/`)

| DTO | Python Equivalent | Key Validations |
|---|---|---|
| `FriendRequestCreateRequest` | `FriendRequestCreate` | `@Email` |
| `GroupCreateRequest` | `GroupCreate` | `@NotBlank`, max 255 |
| `GroupMemberAddRequest` | `GroupMemberAdd` | `@NotNull` UUID |
| `ManualExpenseCreateRequest` | `ManualExpenseCreate` | Nested items + splits, amount limits |
| `ExpenseUpdateRequest` | `ExpenseUpdate` | Reuses `ExpenseItemCreate` |
| `SettlementCreateRequest` | `SettlementCreate` | Amount > 0, max $1M |

### Response DTOs (6 files in `dto/response/`)

| DTO | Python Equivalent |
|---|---|
| `FriendRequestResponse` | `FriendRequestResponse` |
| `FriendResponse` | `FriendResponse` |
| `GroupResponse` + `GroupDetailResponse` | `GroupResponse` + `GroupDetailResponse` |
| `ExpenseResponse` + nested items | `ExpenseResponse` + `ExpenseItemResponse` |
| `SettlementResponse` | `SettlementResponse` |
| `BalanceViewResponse` + nested debts | `BalanceViewResponse` + `GroupBalanceResponse` + `DebtResponse` |

### Services (5 files in `service/`)

| Service | Python File | Core Logic |
|---|---|---|
| `FriendService` | `friend_service.py` | Friend requests, acceptance with DIRECT group creation, removal with cascade delete |
| `GroupService` | `group_service.py` | CRUD, membership management, creator-only operations |
| `ExpenseService` | `expense_service.py` | Manual expense with items/splits, update with equal redistribution |
| `BalanceService` | `balance_service.py` | Net balance computation, `SELECT FOR UPDATE` locking, greedy debt minimization |
| `SettlementService` | `settlement_service.py` | Partial payments, group financials view |

### Controllers (4 files in `controller/`)

| Controller | Python File | Endpoints |
|---|---|---|
| `FriendController` | `routes/friends.py` | 7 |
| `GroupController` | `routes/groups.py` | 9 |
| `ExpenseController` | `routes/expenses.py` | 4 |
| `SettlementController` | `routes/settlements.py` | 2 |

---

## Key Business Logic Preserved

### 1. Friend Request Acceptance → DIRECT Group
When a friend request is accepted, a `DIRECT` group is automatically created (same as Python):
```java
// FriendService.acceptFriendRequest()
GroupEntity directGroup = GroupEntity.builder()
    .name(sender.getName() + " & " + receiver.getName())
    .type(GroupType.DIRECT)
    .build();
```

### 2. Split Validation
Split amounts must equal the total expense amount (tolerance: $0.01):
```java
if (splitTotal.subtract(request.getTotalAmount()).abs()
        .compareTo(new BigDecimal("0.01")) > 0) {
    throw new BadRequestException("Split amounts must equal total amount");
}
```

### 3. Balance Computation with Row-Level Locking
```java
// BalanceService.updateGroupBalances() — prevents race conditions
entityManager.createNativeQuery(
    "SELECT * FROM group_balances WHERE group_id = :gid FOR UPDATE"
).setParameter("gid", groupId).getResultList();
```

### 4. Greedy Debt Minimization
The `minimizeDebts()` algorithm sorts debtors and creditors, then greedily matches them to minimize the number of transactions.

---

## Build Verification

```
$ mvn compile
[INFO] Compiling 67 source files with javac [debug parameters release 21]
[INFO] BUILD SUCCESS
[INFO] Total time: 10.612 s
```

**67 files = 46 (Phase 0-2) + 21 (Phase 3)**
