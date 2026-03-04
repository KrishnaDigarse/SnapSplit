# Phase 2 — Security & Authentication

## Objective

Implement JWT-based authentication matching the Python backend's auth flow exactly: register → login → get token → use token on protected endpoints. Uses BCrypt for password hashing (fresh DB) and HS256 JWT tokens.

---

## Python → Spring Boot Mapping

| Concept | Python (FastAPI) | Java (Spring Boot) |
|---|---|---|
| JWT creation | `jose.jwt.encode({"sub": user_id}, SECRET)` | `Jwts.builder().subject(userId).signWith(key).compact()` |
| JWT validation | `jose.jwt.decode(token, SECRET)` | `Jwts.parser().verifyWith(key).parseSignedClaims(token)` |
| Password hashing | `passlib.hash(password)` | `BCryptPasswordEncoder.encode(password)` |
| Password verify | `passlib.verify(plain, hashed)` | `BCryptPasswordEncoder.matches(plain, hashed)` |
| Get current user | `Depends(get_current_user)` function | `@AuthenticationPrincipal UserEntity` annotation |
| Auth middleware | `HTTPBearer()` + dependency | `JwtAuthenticationFilter` (servlet filter) |
| Route protection | `Depends(get_current_user)` per route | `SecurityFilterChain` → `.anyRequest().authenticated()` |
| Error format | `HTTPException(status_code=401, detail="...")` | `UnauthorizedException("...")` → `GlobalExceptionHandler` |

---

## Files Created

### 1. `JwtService.java` — Token Generation & Validation

**Location:** `com.snapsplit.security.JwtService`

This replaces Python's `core/security.py` (`create_access_token` + `decode_access_token`).

```java
// Generate: puts user UUID as the "sub" claim, signs with HS256
public String generateToken(UUID userId) {
    return Jwts.builder()
            .subject(userId.toString())    // "sub" claim = user ID
            .issuedAt(now)
            .expiration(now + 7 days)      // from app.jwt.expiration-ms
            .signWith(signingKey)          // HMAC-SHA256
            .compact();
}

// Validate: parses token, extracts user UUID from "sub" claim
public UUID extractUserId(String token) {
    Claims claims = Jwts.parser()
            .verifyWith(signingKey)        // verify signature
            .build()
            .parseSignedClaims(token)      // parse + check expiration
            .getPayload();
    return UUID.fromString(claims.getSubject());
}
```

**Config (from `application.yml`):**
```yaml
app:
  jwt:
    secret: snapsplit-jwt-secret-key-change-in-production-2026
    expiration-ms: 604800000  # 7 days
```

---

### 2. `JwtAuthenticationFilter.java` — Request Authentication

**Location:** `com.snapsplit.security.JwtAuthenticationFilter`

This replaces Python's `dependencies/auth.py` → `get_current_user()`.

**Request flow:**
```
Client sends: Authorization: Bearer <jwt-token>
                      │
                      ▼
         ┌─ JwtAuthenticationFilter ──┐
         │  1. Extract "Bearer " token │
         │  2. jwtService.extractUserId│
         │  3. userRepository.findById │
         │  4. Set SecurityContext     │
         └────────────┬───────────────┘
                      │
                      ▼
            Controller method runs
            @AuthenticationPrincipal UserEntity currentUser
```

**Skipped for public endpoints:**
```java
protected boolean shouldNotFilter(HttpServletRequest request) {
    return path.startsWith("/api/v1/auth/register")
        || path.startsWith("/api/v1/auth/login")
        || path.equals("/") || path.equals("/health")
        || path.startsWith("/docs") || path.startsWith("/swagger-ui");
}
```

---

### 3. `SecurityConfig.java` — Updated Security Chain

**Location:** `com.snapsplit.config.SecurityConfig`

The Phase 0 version had `.anyRequest().permitAll()`. Now updated to:

```java
http
    .csrf(csrf -> csrf.disable())
    .sessionManagement(s -> s.sessionCreationPolicy(STATELESS))
    .authorizeHttpRequests(auth -> auth
        .requestMatchers("/", "/health", "/api/v1/auth/register",
                         "/api/v1/auth/login", "/docs/**").permitAll()
        .anyRequest().authenticated()      // ← enforced now!
    )
    .addFilterBefore(jwtFilter, UsernamePasswordAuthenticationFilter.class);
```

**Key change:** `.anyRequest().authenticated()` means any request without a valid JWT gets a 403 Forbidden automatically — no need to add `Depends(get_current_user)` to every route.

---

### 4. Auth DTOs (Request/Response Objects)

| DTO | Replaces (Python) | Fields |
|---|---|---|
| `RegisterRequest` | `UserCreate` | `email` (validated), `name`, `password` (6-72 chars) |
| `LoginRequest` | `UserLogin` | `email`, `password` |
| `UserResponse` | `UserResponse` | `id`, `email`, `name`, `createdAt` |
| `TokenResponse` | `Token` | `accessToken`, `tokenType` ("bearer") |

**Validation example:**
```java
public class RegisterRequest {
    @NotBlank @Email
    private String email;

    @NotBlank @Size(max = 255)
    private String name;

    @NotBlank @Size(min = 6, max = 72)  // 72-byte limit matches Python's bcrypt limit
    private String password;
}
```

---

### 5. `AuthService.java` — Business Logic

**Location:** `com.snapsplit.service.AuthService`

Directly mirrors Python's `services/auth_service.py`:

| Python Function | Java Method | Behavior |
|---|---|---|
| `create_user(db, user_data)` | `register(request)` | Check email exists → hash password → save → return DTO |
| `authenticate_user(db, email, password)` | `login(email, password)` | Find by email → verify password → generate token |
| `generate_token_for_user(user)` | (inside `login()`) | `jwtService.generateToken(user.getId())` |

**Error messages match exactly** for frontend compatibility:
- `"Email already registered"` → 400
- `"Incorrect email or password"` → 401

---

### 6. `AuthController.java` — REST Endpoints

**Location:** `com.snapsplit.controller.AuthController`

| Endpoint | Method | Auth | Python Equivalent |
|---|---|---|---|
| `POST /api/v1/auth/register` | `register()` | Public | `@router.post("/register")` |
| `POST /api/v1/auth/login` | `login()` | Public | `@router.post("/login")` |
| `GET /api/v1/auth/me` | `getMe()` | JWT Required | `@router.get("/me")` |

**Getting the current user in controllers:**
```java
// Spring Boot — @AuthenticationPrincipal injects the UserEntity from SecurityContext
@GetMapping("/me")
public UserResponse getMe(@AuthenticationPrincipal UserEntity currentUser) {
    return authService.toUserResponse(currentUser);
}
```

**Python equivalent:**
```python
@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
```

---

## Auth Flow Diagram

```
┌──────────┐     POST /register      ┌──────────────┐     Save to DB     ┌──────────┐
│  Client  │ ──────────────────────→ │ AuthController │ ─────────────────→ │ Postgres │
│          │ ←────────────────────── │               │ ←───────────────── │          │
│          │     UserResponse (201)  └──────────────┘                    └──────────┘
│          │
│          │     POST /login         ┌──────────────┐     Verify BCrypt   ┌──────────┐
│          │ ──────────────────────→ │ AuthController │ ─────────────────→ │ Postgres │
│          │ ←────────────────────── │               │ ←───────────────── │          │
│          │     TokenResponse       │  → JwtService │                    └──────────┘
│          │     {accessToken}       └──────────────┘
│          │
│          │     GET /me             ┌───────────────────┐   Extract UUID   ┌────────────┐
│          │  Authorization: Bearer  │ JwtAuthFilter      │ ───────────────→ │ JwtService │
│          │ ──────────────────────→ │  → SecurityContext │ ←─────────────── │            │
│          │ ←────────────────────── │  → AuthController  │                  └────────────┘
│          │     UserResponse        └───────────────────┘
└──────────┘
```

---

## Build Verification

```
$ mvn compile
[INFO] Compiling 46 source files with javac [debug parameters release 21]
[INFO] BUILD SUCCESS
[INFO] Total time: 11.239 s
```

**46 files = 38 (Phase 0+1) + 8 (Phase 2: JwtService, JwtAuthFilter, SecurityConfig, AuthService, AuthController, RegisterRequest, LoginRequest, UserResponse, TokenResponse)**

---

## How to Test (Manual)

```bash
# 1. Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User","password":"password123"}'
# → 201 {"id":"uuid","email":"test@example.com","name":"Test User","createdAt":"..."}

# 2. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
# → 200 {"accessToken":"eyJhbG...","tokenType":"bearer"}

# 3. Get profile (with token)
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbG..."
# → 200 {"id":"uuid","email":"test@example.com","name":"Test User","createdAt":"..."}

# 4. Access without token → 403 Forbidden
curl http://localhost:8000/api/v1/groups
# → 403
```

---

## Key Decisions

| Decision | Choice | Rationale |
|---|---|---|
| JWT library | jjwt 0.12.6 | Most popular Java JWT library, supports HS256, clean API |
| Password encoder | BCrypt (only) | DB will be flushed — no need for legacy `pbkdf2_sha256` support |
| Auth principal | `UserEntity` stored as principal | Avoids extra DB query per request (user loaded once in filter) |
| Token format | `accessToken` + `tokenType` | Matches Python's `Token(access_token, token_type)` response |
| Public endpoint list | Explicit paths, not patterns | More secure — only listed paths are public |
| Password limit | 6-72 chars | 72-byte BCrypt limit; matches Python's limit |
