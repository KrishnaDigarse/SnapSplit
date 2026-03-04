package com.snapsplit.websocket;

import lombok.extern.slf4j.Slf4j;
import org.springframework.messaging.simp.SimpMessagingTemplate;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.UUID;

/**
 * Notification service — equivalent to Python's websockets/manager.py
 *
 * Uses SimpMessagingTemplate to send messages to specific users via STOMP.
 * Replaces the raw WebSocketManager that maintained connection lists manually.
 *
 * Spring handles connection tracking internally — no manual connect/disconnect
 * needed.
 */
@Slf4j
@Service
public class NotificationService {

    private final SimpMessagingTemplate messagingTemplate;

    public NotificationService(SimpMessagingTemplate messagingTemplate) {
        this.messagingTemplate = messagingTemplate;
    }

    /**
     * Send a notification to a specific user.
     * Python equivalent: manager.broadcast_to_user(user_id, message)
     *
     * The user subscribes to /user/queue/notifications on the client side.
     */
    public void notifyUser(UUID userId, WebSocketEvent event, Map<String, Object> data) {
        Map<String, Object> message = Map.of(
                "type", event.name(),
                "data", data);

        messagingTemplate.convertAndSendToUser(
                userId.toString(),
                "/queue/notifications",
                message);

        log.info("Notification sent to user {}: {}", userId, event.name());
    }

    /**
     * Notify about expense status change.
     * Python equivalent: _send_notification(user_id, expense_id, status)
     */
    public void notifyExpenseStatusUpdate(UUID userId, UUID expenseId, String status) {
        notifyUser(userId, WebSocketEvent.EXPENSE_STATUS_UPDATED, Map.of(
                "expense_id", expenseId.toString(),
                "status", status));
    }

    /**
     * Notify about a new settlement.
     */
    public void notifySettlementRecorded(UUID userId, UUID settlementId, UUID groupId) {
        notifyUser(userId, WebSocketEvent.SETTLEMENT_RECORDED, Map.of(
                "settlement_id", settlementId.toString(),
                "group_id", groupId.toString()));
    }
}
