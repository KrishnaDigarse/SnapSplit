package com.snapsplit.security;

import com.snapsplit.entity.UserEntity;
import com.snapsplit.repository.UserRepository;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.lang.NonNull;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Collections;
import java.util.UUID;

/**
 * JWT authentication filter — equivalent to Python's get_current_user()
 * dependency.
 *
 * Intercepts every request, extracts the Bearer token from the Authorization
 * header,
 * validates it, looks up the user, and sets the Spring Security context.
 */
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtService jwtService;
    private final UserRepository userRepository;

    public JwtAuthenticationFilter(JwtService jwtService, UserRepository userRepository) {
        this.jwtService = jwtService;
        this.userRepository = userRepository;
    }

    @Override
    protected void doFilterInternal(
            @NonNull HttpServletRequest request,
            @NonNull HttpServletResponse response,
            @NonNull FilterChain filterChain) throws ServletException, IOException {

        // 1. Extract Authorization header
        String authHeader = request.getHeader("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            filterChain.doFilter(request, response);
            return;
        }

        // 2. Extract and validate the JWT token
        String token = authHeader.substring(7); // Remove "Bearer " prefix
        UUID userId = jwtService.extractUserId(token);

        if (userId == null) {
            filterChain.doFilter(request, response);
            return;
        }

        // 3. Look up the user (only if not already authenticated in this request)
        if (SecurityContextHolder.getContext().getAuthentication() == null) {
            UserEntity user = userRepository.findById(userId).orElse(null);

            if (user != null) {
                // 4. Set Spring Security context with the authenticated user
                UsernamePasswordAuthenticationToken authToken = new UsernamePasswordAuthenticationToken(
                        user, // principal = UserEntity
                        null, // credentials (not needed for JWT)
                        Collections.emptyList() // authorities (no roles for now)
                );
                authToken.setDetails(
                        new WebAuthenticationDetailsSource().buildDetails(request));
                SecurityContextHolder.getContext().setAuthentication(authToken);
            }
        }

        filterChain.doFilter(request, response);
    }

    @Override
    protected boolean shouldNotFilter(HttpServletRequest request) {
        String path = request.getServletPath();
        // Skip JWT filter for public endpoints
        return path.startsWith("/api/v1/auth/register")
                || path.startsWith("/api/v1/auth/login")
                || path.equals("/")
                || path.equals("/health")
                || path.startsWith("/docs")
                || path.startsWith("/swagger-ui")
                || path.startsWith("/api-docs")
                || path.startsWith("/actuator");
    }
}
