package com.snapsplit.service;

import com.snapsplit.dto.request.RegisterRequest;
import com.snapsplit.dto.response.TokenResponse;
import com.snapsplit.dto.response.UserResponse;
import com.snapsplit.entity.UserEntity;
import com.snapsplit.exception.BadRequestException;
import com.snapsplit.exception.UnauthorizedException;
import com.snapsplit.repository.UserRepository;
import com.snapsplit.security.JwtService;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

/**
 * Authentication service — equivalent to Python's services/auth_service.py
 *
 * Handles user registration, authentication, and token generation.
 */
@Service
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtService jwtService;

    public AuthService(UserRepository userRepository,
            PasswordEncoder passwordEncoder,
            JwtService jwtService) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtService = jwtService;
    }

    /**
     * Register a new user.
     * Python equivalent: auth_service.create_user(db, user_data)
     */
    @Transactional
    public UserResponse register(RegisterRequest request) {
        // Check if email already registered
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new BadRequestException("Email already registered");
        }

        // Create user with hashed password
        UserEntity user = UserEntity.builder()
                .name(request.getName())
                .email(request.getEmail())
                .passwordHash(passwordEncoder.encode(request.getPassword()))
                .build();

        UserEntity savedUser = userRepository.save(user);
        return toUserResponse(savedUser);
    }

    /**
     * Authenticate user and return JWT token.
     * Python equivalent: auth_service.authenticate_user() +
     * generate_token_for_user()
     */
    public TokenResponse login(String email, String password) {
        // Find user by email
        UserEntity user = userRepository.findByEmail(email)
                .orElseThrow(() -> new UnauthorizedException("Incorrect email or password"));

        // Verify password
        if (!passwordEncoder.matches(password, user.getPasswordHash())) {
            throw new UnauthorizedException("Incorrect email or password");
        }

        // Generate and return token
        String token = jwtService.generateToken(user.getId());
        return TokenResponse.of(token);
    }

    /**
     * Convert UserEntity to UserResponse DTO.
     */
    public UserResponse toUserResponse(UserEntity user) {
        return UserResponse.builder()
                .id(user.getId())
                .email(user.getEmail())
                .name(user.getName())
                .createdAt(user.getCreatedAt())
                .build();
    }
}
