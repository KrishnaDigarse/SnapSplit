package com.snapsplit.security;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.UUID;

import static org.assertj.core.api.Assertions.*;

class JwtServiceTest {

    private JwtService jwtService;

    @BeforeEach
    void setUp() {
        jwtService = new JwtService(
                "test-secret-key-that-is-at-least-32-chars-long-for-hs256",
                3600000L);
    }

    @Test
    @DisplayName("should generate and extract valid token")
    void generateAndExtract() {
        UUID userId = UUID.randomUUID();
        String token = jwtService.generateToken(userId);

        assertThat(token).isNotBlank();
        assertThat(jwtService.extractUserId(token)).isEqualTo(userId);
    }

    @Test
    @DisplayName("should validate valid token")
    void validateToken() {
        UUID userId = UUID.randomUUID();
        String token = jwtService.generateToken(userId);
        assertThat(jwtService.isTokenValid(token)).isTrue();
    }

    @Test
    @DisplayName("should reject expired token")
    void expiredToken() {
        JwtService shortLived = new JwtService(
                "test-secret-key-that-is-at-least-32-chars-long-for-hs256",
                -1000L);

        UUID userId = UUID.randomUUID();
        String token = shortLived.generateToken(userId);

        // extractUserId returns null for invalid/expired tokens
        assertThat(jwtService.extractUserId(token)).isNull();
        assertThat(jwtService.isTokenValid(token)).isFalse();
    }

    @Test
    @DisplayName("should reject tampered token")
    void tamperedToken() {
        UUID userId = UUID.randomUUID();
        String token = jwtService.generateToken(userId);
        // Replace the signature portion with garbage to truly tamper
        String[] parts = token.split("\\.");
        String tampered = parts[0] + "." + parts[1] + ".INVALIDSIGNATURE";

        assertThat(jwtService.extractUserId(tampered)).isNull();
    }

    @Test
    @DisplayName("should reject garbage input")
    void garbageToken() {
        assertThat(jwtService.extractUserId("not.a.jwt")).isNull();
    }
}
