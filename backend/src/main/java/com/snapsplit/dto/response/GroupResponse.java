package com.snapsplit.dto.response;

import com.snapsplit.enums.GroupType;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class GroupResponse {
    private UUID id;
    private String name;
    private UUID createdBy;
    private GroupType type;
    private Boolean isArchived;
    private LocalDateTime createdAt;
    private Integer memberCount;

    // ── For detail view ──

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class MemberDetail {
        private UUID userId;
        private String userName;
        private String userEmail;
        private LocalDateTime joinedAt;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class GroupDetailResponse {
        private UUID id;
        private String name;
        private UUID createdBy;
        private GroupType type;
        private Boolean isArchived;
        private LocalDateTime createdAt;
        private Integer memberCount;
        private List<MemberDetail> members;
    }
}
