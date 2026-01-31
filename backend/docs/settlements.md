# Settlements & Partial Payments

## Purpose

Track payments between users to settle debts. Supports partial payments and maintains accurate balance calculations.

## Core Flow

### Creating Settlement
1. User (payer) creates settlement to another user (payee)
2. System validates:
   - Not paying yourself
   - Both users are group members
   - Amount is positive
3. Settlement record created
4. **Group balances automatically updated**

### Viewing Balances
1. User requests group balances
2. System computes current balances:
   - Expenses (who paid, who owes)
   - Settlements (who paid whom)
3. Returns net balance for each member
4. Cached in group_balances table

## Balance Calculation

### Formula
For each user in a group:
```
net_balance = (expenses_paid) - (expenses_owed) + (settlements_received) - (settlements_paid)
```

### Interpretation
- **Positive balance**: User is owed money
- **Negative balance**: User owes money
- **Zero balance**: User is settled up

### Example
Alice, Bob, and Carol in a group:

**Expenses:**
- Alice paid $60, split equally ($20 each)
  - Alice: +$60 -$20 = +$40
  - Bob: -$20
  - Carol: -$20

**Settlements:**
- Bob pays Alice $20
  - Alice: +$40 +$20 = +$60
  - Bob: -$20 -$20 = -$40
  - Carol: -$20

**Final Balances:**
- Alice: +$60 (owed)
- Bob: -$40 (owes)
- Carol: -$20 (owes)

## Partial Payments

Settlements can be for any amount:
- Don't need to settle full debt at once
- Multiple partial payments allowed
- Balances update incrementally
- No minimum payment required

## Endpoints

### POST /api/v1/settlements
Create a settlement.

**Request Body:**
```json
{
  "group_id": "uuid",
  "paid_to": "uuid-of-payee",
  "amount": 25.00,
  "payment_method": "UPI",
  "note": "Partial payment for groceries"
}
```

**Payment Methods:**
- CASH
- UPI
- BANK
- OTHER

### GET /api/v1/settlements/balances/{group_id}
Get current balances for all group members.

**Response:**
```json
[
  {
    "user_id": "uuid",
    "user_name": "Alice",
    "net_balance": 60.00,
    "updated_at": "2024-01-30T..."
  },
  {
    "user_id": "uuid",
    "user_name": "Bob",
    "net_balance": -40.00,
    "updated_at": "2024-01-30T..."
  }
]
```

## Cache Table

`group_balances` table stores computed balances:
- Updated automatically on expense/settlement creation
- Improves query performance
- Can be recomputed if cache is stale
- Includes timestamp for freshness tracking

## Validation Rules

1. **No Self-Payment**: Cannot pay yourself
2. **Group Membership**: Both users must be in the group
3. **Positive Amount**: Amount must be greater than 0
4. **Valid Payment Method**: Must be one of allowed methods

## Design Decisions

1. **Never Modify Expenses**: Settlements are separate records, expenses remain unchanged
2. **Flexible Amounts**: No restriction on partial vs full payments
3. **Automatic Balance Update**: Ensures consistency without manual recalculation
4. **Payment Method Tracking**: Useful for reconciliation and reporting
5. **Optional Notes**: Allows context for payments
6. **Payer Implicit**: Current user is always the payer
7. **Cache Strategy**: Balance computation is expensive, cache improves performance
