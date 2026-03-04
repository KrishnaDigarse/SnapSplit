package com.snapsplit.config;

import com.snapsplit.security.JwtService;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.annotation.Configuration;
import org.springframework.messaging.Message;
import org.springframework.messaging.MessageChannel;
import org.springframework.messaging.simp.config.ChannelRegistration;
import org.springframework.messaging.simp.config.MessageBrokerRegistry;
import org.springframework.messaging.simp.stomp.StompCommand;
import org.springframework.messaging.simp.stomp.StompHeaderAccessor;
import org.springframework.messaging.support.ChannelInterceptor;
import org.springframework.messaging.support.MessageHeaderAccessor;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.web.socket.config.annotation.EnableWebSocketMessageBroker;
import org.springframework.web.socket.config.annotation.StompEndpointRegistry;
import org.springframework.web.socket.config.annotation.WebSocketMessageBrokerConfigurer;

import java.util.List;
import java.util.UUID;

/**
 * WebSocket configuration using STOMP over SockJS.
 *
 * Python equivalent: routes/ws.py + websockets/manager.py
 *
 * Architecture:
 * Client connects to /ws with JWT token in query param
 * Server authenticates via JwtService
 * Client subscribes to /user/queue/notifications for personal updates
 * Server sends via SimpMessagingTemplate (per-user targeting)
 */
@Slf4j
@Configuration
@EnableWebSocketMessageBroker
public class WebSocketConfig implements WebSocketMessageBrokerConfigurer {

    private final JwtService jwtService;

    public WebSocketConfig(JwtService jwtService) {
        this.jwtService = jwtService;
    }

    @Override
    public void configureMessageBroker(MessageBrokerRegistry registry) {
        // Enable simple in-memory broker for /queue and /topic destinations
        registry.enableSimpleBroker("/queue", "/topic");
        // Prefix for @MessageMapping endpoints
        registry.setApplicationDestinationPrefixes("/app");
        // Prefix for user-specific destinations
        registry.setUserDestinationPrefix("/user");
    }

    @Override
    public void registerStompEndpoints(StompEndpointRegistry registry) {
        // Clients connect to ws://host/ws
        registry.addEndpoint("/ws")
                .setAllowedOriginPatterns("*")
                .withSockJS();
    }

    @Override
    public void configureClientInboundChannel(ChannelRegistration registration) {
        registration.interceptors(new ChannelInterceptor() {
            @Override
            public Message<?> preSend(Message<?> message, MessageChannel channel) {
                StompHeaderAccessor accessor = MessageHeaderAccessor.getAccessor(message, StompHeaderAccessor.class);

                if (accessor != null && StompCommand.CONNECT.equals(accessor.getCommand())) {
                    // Extract JWT from query params or native headers
                    String token = null;

                    // Try native header first
                    List<String> authHeader = accessor.getNativeHeader("Authorization");
                    if (authHeader != null && !authHeader.isEmpty()) {
                        String bearerToken = authHeader.get(0);
                        if (bearerToken.startsWith("Bearer ")) {
                            token = bearerToken.substring(7);
                        }
                    }

                    // Fallback: try "token" header (like Python query param)
                    if (token == null) {
                        List<String> tokenHeader = accessor.getNativeHeader("token");
                        if (tokenHeader != null && !tokenHeader.isEmpty()) {
                            token = tokenHeader.get(0);
                        }
                    }

                    if (token != null) {
                        try {
                            UUID userId = jwtService.extractUserId(token);
                            // Set user as the principal — enables /user/ destinations
                            UsernamePasswordAuthenticationToken auth = new UsernamePasswordAuthenticationToken(
                                    userId.toString(), null, List.of());
                            accessor.setUser(auth);
                            log.info("WebSocket authenticated: user {}", userId);
                        } catch (Exception e) {
                            log.warn("WebSocket auth failed: {}", e.getMessage());
                        }
                    }
                }
                return message;
            }
        });
    }
}
