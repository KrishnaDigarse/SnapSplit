# Manual Expenses

## Purpose

Create and track expenses manually (without AI/OCR). Supports item-level tracking and flexible split configurations.

## Core Flow

### Creating Manual Expense
1. User specifies group, items, and splits
2. System validates:
   - User is group member
   - All split participants are group members
   - Split amounts sum to total amount
   - Total = subtotal + tax
3. Expense created with:
   - source_type = MANUAL
   - status = READY
   - is_edited = false
4. Items created and linked to expense
5. Splits created and linked to first item
6. **Group balances automatically updated**

### Viewing Expense
1. User must be group member
2. Returns expense with items
3. Can include splits if needed

### Listing Group Expenses
1. User must be group member
2. Returns all expenses for group
3. Ordered by creation date (newest first)

## Split Types

### EQUAL
- Amount divided equally among participants
- Each user pays same amount
- Common for shared meals, utilities

### CUSTOM
- Arbitrary amounts per user
- Flexible for unequal contributions
- Must sum to total amount

### ITEM (Future)
- Currently not implemented for manual expenses
- Will allow per-item split tracking

## Validation Rules

1. **Membership**: All participants must be group members
2. **Split Sum**: Total of all splits must equal expense total amount
3. **Amount Accuracy**: Total must equal subtotal + tax (within 0.01 tolerance)
4. **Non-Empty**: Must have at least one item
5. **Non-Empty Splits**: Must have at least one split

## Endpoints

### POST /api/v1/expenses/manual
Create a manual expense.

**Request Body:**
```json
{
  "group_id": "uuid",
  "items": [
    {
      "item_name": "Groceries",
      "quantity": 1,
      "price": 50.00
    }
  ],
  "splits": [
    {
      "user_id": "uuid-user-a",
      "amount": 25.00,
      "split_type": "EQUAL"
    },
    {
      "user_id": "uuid-user-b",
      "amount": 25.00,
      "split_type": "EQUAL"
    }
  ],
  "subtotal": 50.00,
  "tax": 0.00,
  "total_amount": 50.00
}
```

### GET /api/v1/expenses/{expense_id}
Get expense details.

### GET /api/v1/expenses/group/{group_id}
Get all expenses for a group.

## Balance Impact

When expense is created:
1. Creator's balance increases by total amount (they paid)
2. Each split participant's balance decreases by their split amount (they owe)
3. Group balances cache automatically updated

**Example:**
- Alice creates $60 expense
- Split equally between Alice, Bob, Carol ($20 each)
- Alice: +$60 (paid) -$20 (owes) = +$40 net
- Bob: -$20 (owes)
- Carol: -$20 (owes)

## Design Decisions

1. **Immediate READY Status**: Manual expenses don't need processing
2. **Single Item Link**: All splits link to first item for simplicity
3. **Automatic Balance Update**: Ensures balances always reflect current state
4. **Decimal Precision**: Uses Decimal type for accurate monetary calculations
5. **Creator Attribution**: Tracks who created expense (assumed to be payer)
6. **No Modification**: is_edited flag reserved for future edit functionality
