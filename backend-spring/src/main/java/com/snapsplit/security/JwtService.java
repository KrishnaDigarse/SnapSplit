package com.snapsplit.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.JwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;
import java.util.UUID;

/**
 * JWT utility class — equivalent to Python's core/security.py
 * Handles token creation (create_access_token) and validation
 * (decode_access_token).
 */
@Component
public class JwtService {

    private final SecretKey signingKey;
    private final long expirationMs;

    public JwtService(
            @Value("${app.jwt.secret}") String secret,
            @Value("${app.jwt.expiration-ms}") long expirationMs) {
        this.signingKey = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
        this.expirationMs = expirationMs;
    }

    /**
     * Create a JWT token for a user.
     * Python equivalent: create_access_token(data={"sub": str(user.id)})
     */
    public String generateToken(UUID userId) {
        Date now = new Date();
        Date expiry = new Date(now.getTime() + expirationMs);

        return Jwts.builder()
                .subject(userId.toString())
                .issuedAt(now)
                .expiration(expiry)
                .signWith(signingKey)
                .compact();
    }

    /**
     * Extract the user ID (subject) from a JWT token.
     * Python equivalent: decode_access_token(token) → payload.get("sub")
     *
     * @return user UUID, or null if token is invalid/expired
     */
    public UUID extractUserId(String token) {
        try {
            Claims claims = Jwts.parser()
                    .verifyWith(signingKey)
                    .build()
                    .parseSignedClaims(token)
                    .getPayload();

            String subject = claims.getSubject();
            return subject != null ? UUID.fromString(subject) : null;
        } catch (JwtException | IllegalArgumentException e) {
            return null;
        }
    }

    /**
     * Validate a JWT token (check signature and expiration).
     */
    public boolean isTokenValid(String token) {
        return extractUserId(token) != null;
    }
}
