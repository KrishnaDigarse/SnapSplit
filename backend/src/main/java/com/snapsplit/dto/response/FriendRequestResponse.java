package com.snapsplit.dto.response;

import com.snapsplit.enums.FriendRequestStatus;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class FriendRequestResponse {
    private UUID id;
    private UUID senderId;
    private UUID receiverId;
    private FriendRequestStatus status;
    private LocalDateTime createdAt;
    // Extra fields for pending requests
    private String senderName;
    private String senderEmail;
}
