package com.snapsplit.controller;

import com.snapsplit.dto.request.LoginRequest;
import com.snapsplit.dto.request.RegisterRequest;
import com.snapsplit.dto.response.TokenResponse;
import com.snapsplit.dto.response.UserResponse;
import com.snapsplit.entity.UserEntity;
import com.snapsplit.service.AuthService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

/**
 * Authentication controller — equivalent to Python's routes/auth.py
 *
 * Endpoints:
 * POST /api/v1/auth/register → register a new user
 * POST /api/v1/auth/login → login and get JWT token
 * GET /api/v1/auth/me → get current user profile
 */
@RestController
@RequestMapping("/api/v1/auth")
public class AuthController {

    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    /**
     * Register a new user.
     * Python equivalent: @router.post("/register", response_model=UserResponse,
     * status_code=201)
     */
    @PostMapping("/register")
    @ResponseStatus(HttpStatus.CREATED)
    public UserResponse register(@Valid @RequestBody RegisterRequest request) {
        return authService.register(request);
    }

    /**
     * Login and receive JWT token.
     * Python equivalent: @router.post("/login", response_model=Token)
     */
    @PostMapping("/login")
    public TokenResponse login(@Valid @RequestBody LoginRequest request) {
        return authService.login(request.getEmail(), request.getPassword());
    }

    /**
     * Get current user profile from JWT token.
     * Python equivalent: @router.get("/me", response_model=UserResponse)
     *
     * The @AuthenticationPrincipal injects the UserEntity that was set
     * by JwtAuthenticationFilter — equivalent to Depends(get_current_user).
     */
    @GetMapping("/me")
    public UserResponse getMe(@AuthenticationPrincipal UserEntity currentUser) {
        return authService.toUserResponse(currentUser);
    }
}
