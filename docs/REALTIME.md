# Real-time Updates Architecture

SnapSplit uses **WebSockets** for real-time updates, replacing the previous polling mechanism.

## Architecture
1.  **Client Connection**: Frontend connects to `/ws?token=...` via `useWebSocket` hook.
2.  **Connection Management**: `WebSocketManager` maintains active connections mapped to `user_id`.
3.  **Event Trigger**: When a background task (Celery) completes, it sends a **Webhook** (POST request) to the backend (`/ws/notify`).
4.  **Broadcast**: The backend receives the webhook and broadcasts the event to the target user via their open WebSocket connection.

## Events
### `EXPENSE_STATUS_UPDATED`
Triggered when an AI expense processing task completes (Ready/Failed).
```json
{
  "type": "EXPENSE_STATUS_UPDATED",
  "expense_id": "uuid",
  "status": "READY"
}
```

## Security
- WebSocket connection requires a valid JWT token in the query parameter.
- Internal Notification endpoint is open locally but should be restricted in production.
