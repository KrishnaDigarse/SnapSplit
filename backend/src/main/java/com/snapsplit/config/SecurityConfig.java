package com.snapsplit.config;

import com.snapsplit.security.JwtAuthenticationFilter;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

/**
 * Spring Security configuration — equivalent to Python's HTTPBearer +
 * get_current_user dependency.
 *
 * Key behaviors:
 * - Stateless sessions (JWT-based auth, no cookies)
 * - CSRF disabled (REST API)
 * - Public endpoints: /auth/register, /auth/login, /health, /docs
 * - All other endpoints require a valid JWT Bearer token
 * - JWT filter runs before Spring's default auth filter
 */
@Configuration
@EnableWebSecurity
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;

    public SecurityConfig(JwtAuthenticationFilter jwtAuthenticationFilter) {
        this.jwtAuthenticationFilter = jwtAuthenticationFilter;
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
                .csrf(csrf -> csrf.disable())
                .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(auth -> auth
                        // Public endpoints (no JWT required)
                        .requestMatchers(
                                "/",
                                "/health",
                                "/api/v1/auth/register",
                                "/api/v1/auth/login",
                                "/docs/**",
                                "/swagger-ui/**",
                                "/api-docs/**",
                                "/actuator/**")
                        .permitAll()
                        // Everything else requires authentication
                        .anyRequest().authenticated())
                // Add JWT filter before the default UsernamePasswordAuthenticationFilter
                .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
