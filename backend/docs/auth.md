# Authentication

## Purpose

JWT-based authentication system for SnapSplit API. Provides user registration, login, and token-based access control for all protected endpoints.

## Core Flow

### Registration
1. User submits email, name, and password
2. System validates email uniqueness
3. Password is hashed using bcrypt
4. User record created in database
5. User details returned (without password)

### Login
1. User submits email and password
2. System validates credentials
3. Password verified against stored hash
4. JWT token generated with user ID in payload
5. Token returned to client

### Protected Routes
1. Client includes JWT token in Authorization header (`Bearer <token>`)
2. `get_current_user` dependency extracts and validates token
3. User object retrieved from database
4. User object passed to route handler

## Token Configuration

- **Algorithm**: HS256
- **Expiry**: 7 days (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES`)
- **Secret Key**: Loaded from environment variable `SECRET_KEY`

## Security Considerations

- Passwords never stored in plain text
- Bcrypt used for password hashing (automatic salt generation)
- JWT tokens include expiration timestamp
- All non-auth routes protected by default
- Invalid tokens return 401 Unauthorized

## Endpoints

### POST /api/v1/auth/register
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "name": "John Doe",
  "password": "securepassword123"
}
```

**Response:** User object (201 Created)

### POST /api/v1/auth/login
Login and receive JWT token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## Design Decisions

1. **Single Token Type**: Only access tokens implemented (no refresh tokens) for simplicity
2. **Long Expiry**: 7-day token expiry reduces need for frequent re-authentication
3. **Stateless Auth**: JWT tokens are self-contained, no server-side session storage
4. **User ID in Token**: Token payload contains user ID (`sub` claim) for quick user lookup
