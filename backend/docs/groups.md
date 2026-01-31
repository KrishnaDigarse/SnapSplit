# Groups System

## Purpose

Manage expense groups for multiple users. Groups serve as containers for expenses and settlements.

## Core Flow

### Creating a Group
1. User creates group with a name
2. Group created with type = GROUP
3. Creator automatically added as first member
4. Group ID returned

### Adding Members
1. Only group creator can add members
2. System validates:
   - Group exists
   - Current user is creator
   - User to add exists
   - User not already a member
3. Member added to group

### Listing Groups
1. Returns all groups where user is a member
2. **Excludes DIRECT groups** (shown in friends list instead)
3. Includes member count for each group
4. Only shows non-archived groups

### Getting Group Details
1. User must be a member to view
2. Returns full group information
3. Includes list of all members with details

## Group Types

### GROUP
- Regular multi-user groups
- Created manually by users
- Shown in group listings
- Can have any number of members

### DIRECT
- One-on-one groups
- Created automatically when friend request accepted
- Hidden from group listings
- Always has exactly 2 members
- Used for direct expense tracking between friends

## Endpoints

### POST /api/v1/groups
Create a new group.

**Request Body:**
```json
{
  "name": "Roommates"
}
```

### POST /api/v1/groups/{group_id}/add-member
Add a member to group (creator only).

**Request Body:**
```json
{
  "user_id": "uuid-of-user"
}
```

### GET /api/v1/groups
Get all groups (excludes DIRECT groups).

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Roommates",
    "created_by": "uuid",
    "type": "GROUP",
    "is_archived": false,
    "created_at": "2024-01-30T...",
    "member_count": 3
  }
]
```

### GET /api/v1/groups/{group_id}
Get group details with member list.

## Permission Rules

1. **Member Access**: Only members can view group details
2. **Creator Privileges**: Only creator can add members
3. **Membership Validation**: Can only add existing users
4. **No Duplicates**: Cannot add user who is already a member

## Soft Delete

Groups use `is_archived` flag instead of hard deletion:
- Preserves expense history
- Maintains data integrity
- Can be restored if needed
- Archived groups hidden from listings

## Design Decisions

1. **Creator-Only Add**: Prevents unauthorized member additions
2. **Auto-Membership**: Creator automatically becomes first member
3. **DIRECT Group Exclusion**: Keeps group listings clean and focused
4. **Member Count**: Precomputed for efficient display
5. **Soft Delete**: Preserves historical data and relationships
