package com.snapsplit.service;

import com.snapsplit.dto.request.RegisterRequest;
import com.snapsplit.dto.response.TokenResponse;
import com.snapsplit.dto.response.UserResponse;
import com.snapsplit.entity.UserEntity;
import com.snapsplit.exception.BadRequestException;
import com.snapsplit.exception.UnauthorizedException;
import com.snapsplit.repository.UserRepository;
import com.snapsplit.security.JwtService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.security.crypto.password.PasswordEncoder;

import java.util.Optional;
import java.util.UUID;

import static org.assertj.core.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class AuthServiceTest {

    @Mock
    private UserRepository userRepository;
    @Mock
    private PasswordEncoder passwordEncoder;
    @Mock
    private JwtService jwtService;
    @InjectMocks
    private AuthService authService;

    private UserEntity testUser;
    private final UUID userId = UUID.randomUUID();

    @BeforeEach
    void setUp() {
        testUser = UserEntity.builder()
                .id(userId)
                .name("Test User")
                .email("test@example.com")
                .passwordHash("$2a$10$hashedpassword")
                .build();
    }

    @Nested
    @DisplayName("register()")
    class RegisterTests {

        @Test
        @DisplayName("should register new user successfully")
        void register_success() {
            RegisterRequest request = new RegisterRequest();
            request.setName("New User");
            request.setEmail("new@example.com");
            request.setPassword("password123");

            when(userRepository.existsByEmail("new@example.com")).thenReturn(false);
            when(passwordEncoder.encode("password123")).thenReturn("$2a$10$encoded");
            when(userRepository.save(any(UserEntity.class))).thenAnswer(inv -> {
                UserEntity u = inv.getArgument(0);
                u.setId(UUID.randomUUID());
                return u;
            });

            UserResponse response = authService.register(request);

            assertThat(response).isNotNull();
            assertThat(response.getName()).isEqualTo("New User");
            assertThat(response.getEmail()).isEqualTo("new@example.com");
            verify(userRepository).save(any(UserEntity.class));
        }

        @Test
        @DisplayName("should throw when email already exists")
        void register_duplicateEmail() {
            RegisterRequest request = new RegisterRequest();
            request.setEmail("test@example.com");
            request.setPassword("password123");

            when(userRepository.existsByEmail("test@example.com")).thenReturn(true);

            assertThatThrownBy(() -> authService.register(request))
                    .isInstanceOf(BadRequestException.class)
                    .hasMessageContaining("already registered");
        }
    }

    @Nested
    @DisplayName("login()")
    class LoginTests {

        @Test
        @DisplayName("should login successfully and return token")
        void login_success() {
            when(userRepository.findByEmail("test@example.com")).thenReturn(Optional.of(testUser));
            when(passwordEncoder.matches("password123", "$2a$10$hashedpassword")).thenReturn(true);
            when(jwtService.generateToken(userId)).thenReturn("jwt-token-123");

            TokenResponse response = authService.login("test@example.com", "password123");

            assertThat(response).isNotNull();
            assertThat(response.getAccessToken()).isEqualTo("jwt-token-123");
            assertThat(response.getTokenType()).isEqualTo("bearer");
        }

        @Test
        @DisplayName("should throw on wrong email")
        void login_wrongEmail() {
            when(userRepository.findByEmail("wrong@example.com")).thenReturn(Optional.empty());

            assertThatThrownBy(() -> authService.login("wrong@example.com", "password123"))
                    .isInstanceOf(UnauthorizedException.class);
        }

        @Test
        @DisplayName("should throw on wrong password")
        void login_wrongPassword() {
            when(userRepository.findByEmail("test@example.com")).thenReturn(Optional.of(testUser));
            when(passwordEncoder.matches("wrongpass", "$2a$10$hashedpassword")).thenReturn(false);

            assertThatThrownBy(() -> authService.login("test@example.com", "wrongpass"))
                    .isInstanceOf(UnauthorizedException.class);
        }
    }
}
