# Phase 7 — Testing

## Test Results

```
Tests run: 34, Failures: 0, Errors: 0, Skipped: 0
BUILD SUCCESS (4.243 s)
```

---

## Test Classes (6 files, 34 tests)

| Test Class | Tests | What's Tested |
|---|---|---|
| `AuthServiceTest` | 5 | Register (success, duplicate), Login (success, wrong email, wrong password) |
| `JwtServiceTest` | 5 | Generate/extract, validate, expired, tampered signature, garbage input |
| `FriendServiceTest` | 7 | Send request (success, self, not found, already friends), Accept (success + DIRECT group, not receiver), Get friends |
| `GroupServiceTest` | 6 | Create group, Add member (success, not creator, already member), Leave (creator forbidden), Delete (not found) |
| `SettlementServiceTest` | 3 | Create settlement (success, pay self, not member) |
| `BillParserTest` | 8 | Valid data, auto-correct total, missing field, no valid items, math error, currency symbols, invalid price items, default quantity |

---

## Test Coverage Summary

| Layer | Coverage |
|---|---|
| Auth & Security | `AuthService`, `JwtService` |
| Friends | `FriendService` — full CRUD |
| Groups | `GroupService` — create, members, leave, delete |
| Settlements | `SettlementService` — create with validations |
| AI Pipeline | `BillParser` — validation, math, edge cases |

---

## Test Technology

- **JUnit 5** — test framework
- **Mockito** — mocking repositories and services
- **AssertJ** — fluent assertions
- **@ExtendWith(MockitoExtension.class)** — no Spring context needed for unit tests
- **Nested test classes** — organized by method under test
