package com.snapsplit.dto.request;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GroupCreateRequest {

    @NotBlank(message = "Group name is required")
    @Size(max = 255, message = "Group name must be at most 255 characters")
    private String name;
}
