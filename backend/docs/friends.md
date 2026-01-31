# Friends System

## Purpose

Manage friend connections between users and automatically create DIRECT groups for one-on-one expense tracking.

## Core Flow

### Sending Friend Request
1. User A sends request to User B
2. System validates:
   - Not sending to self
   - User B exists
   - No pending request exists (either direction)
   - Not already friends
3. Friend request created with PENDING status

### Accepting Friend Request
1. User B accepts request from User A
2. System validates:
   - Request exists
   - User B is the receiver
   - Request is still PENDING
3. Request status updated to ACCEPTED
4. **Two friendship records created** (bidirectional):
   - `friends(user_id=A, friend_id=B)`
   - `friends(user_id=B, friend_id=A)`
5. **DIRECT group automatically created**:
   - Type: DIRECT
   - Name: "User A & User B"
   - Both users added as members
6. DIRECT group ID returned in response

### Rejecting Friend Request
1. User B rejects request from User A
2. Request status updated to REJECTED
3. No friendship or group created

### Listing Friends
1. Returns all accepted friendships for current user
2. Includes friend's name and email

## DIRECT Group Behavior

**Key Characteristics:**
- Type = DIRECT (not GROUP)
- Created automatically on friend acceptance
- Hidden from regular group listings
- Used for one-on-one expense tracking
- Name format: "User A & User B"

**Why DIRECT Groups?**
- Consistent expense tracking mechanism
- Simplifies balance calculations
- Enables direct settlements between friends
- Reuses existing group infrastructure

## Endpoints

### POST /api/v1/friends/request
Send a friend request.

**Request Body:**
```json
{
  "receiver_id": "uuid-of-user-b"
}
```

### POST /api/v1/friends/accept/{request_id}
Accept a friend request and create DIRECT group.

**Response:**
```json
{
  "message": "Friend request accepted",
  "direct_group_id": "uuid-of-created-group"
}
```

### POST /api/v1/friends/reject/{request_id}
Reject a friend request.

### GET /api/v1/friends
Get list of all friends.

## Validation Rules

1. **No Self-Requests**: Cannot send friend request to yourself
2. **No Duplicates**: Cannot have multiple pending requests between same users
3. **No Duplicate Friendships**: Cannot accept if already friends
4. **Authorization**: Only receiver can accept/reject requests
5. **Status Check**: Can only accept/reject PENDING requests

## Design Decisions

1. **Bidirectional Friendship**: Two rows in `friends` table ensures efficient queries from either user's perspective
2. **Automatic DIRECT Group**: Eliminates manual group creation for common use case
3. **Request Status Tracking**: PENDING/ACCEPTED/REJECTED allows for request history
4. **Receiver Authorization**: Only the person receiving request can accept/reject
