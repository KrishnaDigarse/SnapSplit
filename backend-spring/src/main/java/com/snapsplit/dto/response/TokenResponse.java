package com.snapsplit.dto.response;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Token response DTO — returned by login endpoint.
 * Python equivalent: schemas/user.py → Token(access_token, token_type)
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class TokenResponse {

    private String accessToken;
    private String tokenType;

    public static TokenResponse of(String accessToken) {
        return new TokenResponse(accessToken, "bearer");
    }
}
