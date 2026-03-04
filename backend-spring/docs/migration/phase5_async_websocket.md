# Phase 5 — Async Tasks & WebSocket

## Objective

Replace Celery (background tasks) and raw WebSocket connections with Spring's `@Async` and STOMP-over-SockJS.

---

## Python → Spring Boot Mapping

| Component | Python | Java |
|---|---|---|
| Background tasks | Celery + Redis broker | `@Async` + `ThreadPoolTaskExecutor` |
| Task retry | `celery.Task` with `autoretry_for` | Manual retry in `LlmService` |
| WebSocket server | FastAPI `WebSocket` (raw) | Spring STOMP over SockJS |
| Connection manager | `WebSocketManager` (manual dict) | `SimpMessagingTemplate` (Spring-managed) |
| Auth (WS) | JWT via query param `?token=xxx` | JWT via STOMP CONNECT header |
| User targeting | `manager.broadcast_to_user(uid)` | `convertAndSendToUser(uid, dest, msg)` |
| Event types | `WebSocketEvent` enum | `WebSocketEvent` enum |
| Internal notify | `POST /ws/notify` + API key | Direct `NotificationService.notifyUser()` |

---

## Files Created/Modified (4 files)

### `AsyncConfig.java` (Modified)
- Added `@EnableAsync` annotation
- Implemented `AsyncConfigurer` → default executor for all `@Async` methods
- Thread pool: core=2, max=5, queue=25

### `WebSocketConfig.java` (New)
- STOMP endpoint: `/ws` with SockJS fallback
- Broker destinations: `/queue`, `/topic`, user prefix `/user`
- JWT authentication on STOMP CONNECT via `ChannelInterceptor`
- Accepts token in `Authorization: Bearer xxx` or `token: xxx` headers

### `WebSocketEvent.java` (New)
```java
enum WebSocketEvent {
    EXPENSE_STATUS_UPDATED,
    SETTLEMENT_RECORDED
}
```

### `NotificationService.java` (New)
- `notifyUser(userId, event, data)` → sends to `/user/{uid}/queue/notifications`
- `notifyExpenseStatusUpdate(userId, expenseId, status)` — used by AI pipeline
- `notifySettlementRecorded(userId, settlementId, groupId)`

---

## Architecture: Python vs. Spring

### Python (Raw WebSocket)
```
Client → ws://host/ws?token=jwt → WebSocketManager.connect()
Celery task → POST /ws/notify (internal API key) → manager.broadcast_to_user()
```

### Spring (STOMP)
```
Client → ws://host/ws → STOMP CONNECT (Authorization: Bearer jwt)
       → SUBSCRIBE /user/queue/notifications
@Async method → NotificationService.notifyUser(userId, event, data)
       → SimpMessagingTemplate.convertAndSendToUser()
```

**Key improvement:** No internal HTTP endpoint needed — `NotificationService` calls `SimpMessagingTemplate` directly from any service.

---

## Build Verification

```
$ mvn compile
[INFO] Compiling 76 source files → BUILD SUCCESS (9.314 s)
```
