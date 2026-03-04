package com.snapsplit.dto.response;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.UUID;

/**
 * User response DTO — returned by register and /me endpoints.
 * Python equivalent: schemas/user.py → UserResponse(id, email, name,
 * created_at)
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class UserResponse {

    private UUID id;
    private String email;
    private String name;
    private LocalDateTime createdAt;
}
