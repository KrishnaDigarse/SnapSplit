# API Endpoints

Complete list of all SnapSplit API endpoints.

## Base URL
`http://localhost:8000/api/v1`

## Authentication

### Register
**POST** `/auth/register`
- Create new user account
- Returns: User object

### Login
**POST** `/auth/login`
- Authenticate and get JWT token
- Returns: Access token

## Friends

### Send Friend Request
**POST** `/friends/request`
- Send friend request to another user
- Protected: Yes
- Returns: Friend request object

### Accept Friend Request
**POST** `/friends/accept/{request_id}`
- Accept pending friend request
- Creates DIRECT group automatically
- Protected: Yes
- Returns: Success message with DIRECT group ID

### Reject Friend Request
**POST** `/friends/reject/{request_id}`
- Reject pending friend request
- Protected: Yes
- Returns: Updated friend request

### List Friends
**GET** `/friends`
- Get all accepted friends
- Protected: Yes
- Returns: Array of friend objects

## Groups

### Create Group
**POST** `/groups`
- Create new expense group
- Protected: Yes
- Returns: Group object

### Add Member
**POST** `/groups/{group_id}/add-member`
- Add user to group (creator only)
- Protected: Yes
- Returns: Success message

### List Groups
**GET** `/groups`
- Get all groups (excludes DIRECT groups)
- Protected: Yes
- Returns: Array of group objects with member counts

### Get Group Details
**GET** `/groups/{group_id}`
- Get group with member list
- Protected: Yes (members only)
- Returns: Group object with members array

## Expenses

### Create Manual Expense
**POST** `/expenses/manual`
- Create expense with items and splits
- Protected: Yes (group members only)
- Returns: Expense object

### Get Expense
**GET** `/expenses/{expense_id}`
- Get expense details
- Protected: Yes (group members only)
- Returns: Expense object with items

### List Group Expenses
**GET** `/expenses/group/{group_id}`
- Get all expenses for a group
- Protected: Yes (group members only)
- Returns: Array of expense objects

## Settlements

### Create Settlement
**POST** `/settlements`
- Record payment between users
- Protected: Yes (group members only)
- Returns: Settlement object

### Get Group Balances
**GET** `/settlements/balances/{group_id}`
- Get current balances for all group members
- Protected: Yes (group members only)
- Returns: Array of balance objects

## System

### Root
**GET** `/`
- API status and version
- Protected: No
- Returns: Welcome message

### Health Check
**GET** `/health`
- Service health status
- Protected: No
- Returns: Health status

## Authentication Header

All protected endpoints require JWT token:
```
Authorization: Bearer <your-jwt-token>
```

## Response Codes

- **200 OK**: Successful GET/POST/PUT
- **201 Created**: Resource created successfully
- **400 Bad Request**: Invalid input or validation error
- **401 Unauthorized**: Missing or invalid token
- **403 Forbidden**: Insufficient permissions
- **404 Not Found**: Resource doesn't exist
- **500 Internal Server Error**: Server error

## Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Interactive Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
