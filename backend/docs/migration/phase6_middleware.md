# Phase 6 — Middleware & Cross-Cutting

## Objective

Ensure all cross-cutting concerns (logging, error handling, caching, health checks) are in place.

---

## Status

Most Phase 6 components were already created in Phase 0 scaffolding. The only new component is `CacheConfig` for Redis caching.

| Component | Status | File |
|---|---|---|
| Request logging filter | ✅ Phase 0 | `config/RequestLoggingFilter.java` |
| Global exception handler | ✅ Phase 0 | `exception/GlobalExceptionHandler.java` |
| Health check (Actuator) | ✅ Phase 0 | `controller/HealthController.java` + Actuator |
| Redis caching | ✅ **New** | `config/CacheConfig.java` |

---

## New: `CacheConfig.java`

Enables Spring Cache abstraction with Redis backend and per-cache TTL overrides:

| Cache Name | TTL | Usage |
|---|---|---|
| `groupBalances` | 2 min | Cached balance computations |
| `userProfile` | 10 min | Cached user info |
| `groupDetail` | 3 min | Cached group details |
| Default | 5 min | All other caches |

Usage in services:
```java
@Cacheable("groupBalances")
public BalanceViewResponse calculateGroupDebts(UUID groupId) { ... }

@CacheEvict(value = "groupBalances", key = "#groupId")
public void updateGroupBalances(UUID groupId) { ... }
```

## Existing Components (from Phase 0)

### `RequestLoggingFilter` — logs every request
```
GET /api/v1/groups 200 - 45ms
POST /api/v1/expenses/manual 201 - 123ms
```

### `GlobalExceptionHandler` — consistent error responses
Handles: `ResourceNotFoundException` (404), `BadRequestException` (400), `UnauthorizedException` (401), `ConflictException` (409), validation errors (422), and generic 500.

### Spring Actuator — `/actuator/health`, `/actuator/info`

---

## Build Verification
```
$ mvn compile
[INFO] Compiling 77 source files → BUILD SUCCESS (4.784 s)
```
