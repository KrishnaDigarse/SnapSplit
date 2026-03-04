package com.snapsplit.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import javax.sql.DataSource;
import java.sql.Connection;
import java.util.HashMap;
import java.util.Map;

@RestController
public class HealthController {

    @Value("${spring.application.name:snapsplit}")
    private String appName;

    private final DataSource dataSource;

    public HealthController(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @GetMapping("/")
    public Map<String, Object> root() {
        return Map.of(
                "message", "SnapSplit API is running",
                "version", "1.0.0");
    }

    @GetMapping("/health")
    public Map<String, Object> healthCheck() {
        Map<String, Object> health = new HashMap<>();
        health.put("status", "healthy");
        health.put("version", "1.0.0");

        Map<String, String> checks = new HashMap<>();

        // Check database connectivity
        try (Connection conn = dataSource.getConnection()) {
            conn.createStatement().execute("SELECT 1");
            checks.put("database", "healthy");
        } catch (Exception e) {
            health.put("status", "unhealthy");
            checks.put("database", "unhealthy: " + e.getMessage());
        }

        health.put("checks", checks);
        return health;
    }
}
