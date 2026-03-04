# Phase 0 — Project Scaffolding & Infrastructure

## Objective

Set up a fully compilable Spring Boot 3.4.3 project that mirrors the Python/FastAPI backend's infrastructure — same port (8000), same database (PostgreSQL 15), same cache (Redis 7), and same API base path (`/api/v1`).

---

## Python → Spring Boot Mapping

| Concept | Python (FastAPI) | Java (Spring Boot) |
|---|---|---|
| Entry point | `main.py` → `FastAPI()` | `SnapsplitApplication.java` → `@SpringBootApplication` |
| Config | `.env` + `pydantic-settings` | `application.yml` + `@Value` |
| CORS | `CORSMiddleware` | `WebMvcConfigurer.addCorsMappings()` |
| Request Logging | `RequestLoggingMiddleware` | `OncePerRequestFilter` |
| Connection Pool | SQLAlchemy `pool_size=10, max_overflow=20` | HikariCP `maximum-pool-size=10` |
| Async Tasks | Celery + Redis | `@Async` + `ThreadPoolTaskExecutor` |
| Caching | `redis.from_url()` | Spring Cache + `RedisCacheManager` |
| Error Handling | `HTTPException` | `@ControllerAdvice` + `@ExceptionHandler` |
| API Docs | Swagger UI at `/docs` | SpringDoc OpenAPI at `/docs` |
| Health Check | `@app.get("/health")` | `@GetMapping("/health")` |
| Password Hashing | `passlib` pbkdf2_sha256 | `BCryptPasswordEncoder` (fresh DB) |
| Containerization | `Dockerfile` (Python) | `Dockerfile` (multi-stage Maven→JRE) |

---

## Files Created

### 1. `pom.xml` — Maven Project Configuration

**Purpose:** Defines all dependencies and build configuration.

**Key dependencies:**

```xml
<!-- Core Web Framework -->
spring-boot-starter-web          → REST controllers, JSON serialization

<!-- Database -->
spring-boot-starter-data-jpa     → JPA/Hibernate ORM (replaces SQLAlchemy)
postgresql                       → PostgreSQL JDBC driver

<!-- Security -->
spring-boot-starter-security     → Auth framework (replaces passlib + python-jose)
jjwt-api / jjwt-impl / jjwt-jackson → JWT token creation/validation

<!-- Messaging -->
spring-boot-starter-websocket    → WebSocket support (replaces FastAPI WebSocket)
spring-boot-starter-data-redis   → Redis client (replaces redis-py)
spring-boot-starter-cache        → Cache abstraction with @Cacheable

<!-- Utilities -->
spring-boot-starter-validation   → Bean validation (replaces Pydantic)
lombok                           → Reduces boilerplate (@Data, @Builder, etc.)
springdoc-openapi                → Swagger UI (replaces FastAPI's built-in)
spring-boot-starter-actuator     → Health checks, metrics

<!-- Testing -->
spring-boot-starter-test         → JUnit 5, Mockito, MockMvc
spring-security-test             → Security test utilities
testcontainers (postgresql)      → Disposable PostgreSQL for integration tests
```

---

### 2. `application.yml` — Application Configuration

**Purpose:** Central config file replacing the Python `.env` + `pydantic-settings` pattern.

```yaml
server:
  port: 8000              # Same port as Python backend

spring.datasource:
  url: jdbc:postgresql://localhost:5432/snapsplit_db
  hikari:
    maximum-pool-size: 10  # Mirrors SQLAlchemy pool_size=10
    max-lifetime: 1800000  # 30 min = pool_recycle=1800

spring.jpa:
  hibernate.ddl-auto: validate  # Read-only schema validation, no modifications

app.jwt:
  secret: snapsplit-jwt-secret-key-change-in-production-2026
  expiration-ms: 604800000  # 7 days (matches Python: 60*24*7 minutes)
```

**Why `ddl-auto: validate`?** We're mapping JPA entities to the *existing* PostgreSQL schema. Hibernate will only check that entity mappings match the database — it won't create or modify tables.

---

### 3. `SnapsplitApplication.java` — Entry Point

```java
@SpringBootApplication  // Component scanning + auto-configuration
@EnableCaching           // Activates @Cacheable / @CacheEvict annotations
@EnableAsync             // Activates @Async for AI pipeline tasks
public class SnapsplitApplication {
    public static void main(String[] args) {
        SpringApplication.run(SnapsplitApplication.class, args);
    }
}
```

**Python equivalent:** `main.py` with `app = FastAPI(...)` and `uvicorn.run()`.

---

### 4. `SecurityConfig.java` — Security Configuration

```java
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) {
        http
            .csrf(csrf -> csrf.disable())                    // REST API, no CSRF needed
            .sessionManagement(s -> s.sessionCreationPolicy(STATELESS))  // JWT = stateless
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/", "/health", "/api/v1/auth/**", "/docs/**").permitAll()
                .anyRequest().permitAll()  // TODO: .authenticated() in Phase 2
            );
        return http.build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();  // Fresh DB, no legacy hashes
    }
}
```

**Why all endpoints are `permitAll()` now?** The JWT authentication filter hasn't been created yet (Phase 2). This lets us verify the scaffolding compiles and runs before adding auth.

**Python equivalent:** `HTTPBearer()` + `get_current_user()` dependency in `routes/auth.py`.

---

### 5. `CorsConfig.java` — CORS Configuration

```java
registry.addMapping("/**")
    .allowedOrigins("http://localhost:3000", "http://localhost:5173")
    .allowedMethods("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")
    .allowCredentials(true);
```

**Python equivalent:**
```python
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://localhost:5173"])
```

Origins are configurable via `application.yml` under `app.cors.allowed-origins`.

---

### 6. `AsyncConfig.java` — Thread Pool for AI Tasks

```java
@Bean(name = "aiTaskExecutor")
public Executor aiTaskExecutor() {
    ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
    executor.setCorePoolSize(2);     // 2 threads kept alive
    executor.setMaxPoolSize(5);      // Max 5 concurrent AI tasks
    executor.setQueueCapacity(25);   // Queue 25 tasks if all threads busy
    return executor;
}
```

**Python equivalent:** Celery with Redis broker (`celery_app.py` + `celery_config.py`).

**Why not Celery/RabbitMQ?** For our scale, Spring's `@Async` with a thread pool is simpler and doesn't require an external task queue. If we need durability (surviving restarts), we can switch to Spring Integration later.

---

### 7. `RedisConfig.java` — Cache Configuration

```java
@Bean
public CacheManager cacheManager(RedisConnectionFactory connectionFactory) {
    RedisCacheConfiguration config = RedisCacheConfiguration.defaultCacheConfig()
        .entryTtl(Duration.ofMinutes(30))                         // 30-minute cache TTL
        .serializeValuesWith(fromSerializer(new GenericJackson2JsonRedisSerializer()));
    return RedisCacheManager.builder(connectionFactory).cacheDefaults(config).build();
}
```

**Python equivalent:** Direct `redis.from_url()` calls scattered throughout services.

**Spring advantage:** With this config, caching is as simple as adding `@Cacheable("groups")` to any service method.

---

### 8. `RequestLoggingFilter.java` — Request Logging

```java
@Component
@Order(1)
public class RequestLoggingFilter extends OncePerRequestFilter {
    protected void doFilterInternal(...) {
        long startTime = System.currentTimeMillis();
        try {
            filterChain.doFilter(request, response);
        } finally {
            long duration = System.currentTimeMillis() - startTime;
            log.info("{} {} {} - {}ms", method, uri, status, duration);
        }
    }
}
```

**Python equivalent:** `RequestLoggingMiddleware` in `core/middleware.py`.

Output: `GET /api/v1/groups 200 - 15ms`

---

### 9. `HealthController.java` — Root & Health Endpoints

Two endpoints matching the Python backend exactly:

| Endpoint | Response |
|---|---|
| `GET /` | `{"message": "SnapSplit API is running", "version": "1.0.0"}` |
| `GET /health` | `{"status": "healthy", "version": "1.0.0", "checks": {"database": "healthy"}}` |

The health check runs `SELECT 1` against PostgreSQL (same as Python's `db.execute(text("SELECT 1"))`).

---

### 10. `GlobalExceptionHandler.java` — Error Handling

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(ResourceNotFoundException.class)
    public ResponseEntity<Map<String, Object>> handleNotFound(ResourceNotFoundException ex) {
        return buildResponse(HttpStatus.NOT_FOUND, ex.getMessage());
    }
    // ... handlers for BadRequest (400), Unauthorized (401), Conflict (409), Validation (422)
}
```

**Response format matches FastAPI:**
```json
{
    "detail": "User not found",
    "status": 404,
    "timestamp": "2026-03-04T12:20:00"
}
```

The `detail` key is crucial — the React frontend parses `error.response.data.detail` for error messages.

**4 custom exception classes:**
- `ResourceNotFoundException` → 404
- `BadRequestException` → 400
- `UnauthorizedException` → 401
- `ConflictException` → 409

---

### 11. `Dockerfile` — Multi-Stage Build

```dockerfile
# Stage 1: Build with Maven
FROM maven:3.9-eclipse-temurin-21 AS build
COPY pom.xml .
RUN mvn dependency:go-offline    # Cache dependencies
COPY src ./src
RUN mvn package -DskipTests

# Stage 2: Runtime with minimal JRE
FROM eclipse-temurin:21-jre-alpine
RUN adduser -S spring            # Non-root user for security
COPY --from=build /app/target/*.jar app.jar
EXPOSE 8000
ENTRYPOINT ["java", "-jar", "app.jar"]
```

**Python equivalent:** `Dockerfile` with `python:3.10-slim`, `pip install`, `uvicorn`.

**Image size comparison:** ~180MB (JRE Alpine) vs ~400MB (Python slim).

---

### 12. `docker-compose.yml` — Updated

Added a `backend` service:

```yaml
backend:
  build: ./backend-spring
  ports: ["8000:8000"]
  environment:
    SPRING_DATASOURCE_URL: jdbc:postgresql://postgres:5432/snapsplit_db
  depends_on:
    postgres: { condition: service_healthy }
    redis:    { condition: service_healthy }
```

---

## Project Structure After Phase 0

```
backend-spring/
├── pom.xml
├── mvnw.cmd
├── Dockerfile
├── .gitignore
├── .mvn/wrapper/
│   ├── maven-wrapper.jar
│   └── maven-wrapper.properties
├── docs/migration/
│   ├── README.md
│   └── phase0_scaffolding.md    ← you are here
├── src/
│   ├── main/
│   │   ├── java/com/snapsplit/
│   │   │   ├── SnapsplitApplication.java
│   │   │   ├── config/
│   │   │   │   ├── AsyncConfig.java
│   │   │   │   ├── CorsConfig.java
│   │   │   │   ├── RedisConfig.java
│   │   │   │   ├── RequestLoggingFilter.java
│   │   │   │   └── SecurityConfig.java
│   │   │   ├── controller/
│   │   │   │   └── HealthController.java
│   │   │   ├── dto/request/          (empty — Phase 3)
│   │   │   ├── dto/response/         (empty — Phase 3)
│   │   │   ├── entity/               (empty — Phase 1)
│   │   │   ├── enums/                (empty — Phase 1)
│   │   │   ├── exception/
│   │   │   │   ├── GlobalExceptionHandler.java
│   │   │   │   ├── ResourceNotFoundException.java
│   │   │   │   ├── BadRequestException.java
│   │   │   │   ├── UnauthorizedException.java
│   │   │   │   └── ConflictException.java
│   │   │   ├── repository/           (empty — Phase 1)
│   │   │   ├── security/             (empty — Phase 2)
│   │   │   ├── service/              (empty — Phase 3)
│   │   │   ├── websocket/            (empty — Phase 5)
│   │   │   └── ai/                   (empty — Phase 4)
│   │   └── resources/
│   │       └── application.yml
│   └── test/
│       ├── java/com/snapsplit/
│       │   └── SnapsplitApplicationTests.java
│       └── resources/
│           └── application-test.yml
```

---

## Build Verification

```
$ mvn compile
[INFO] Compiling 12 source files with javac [debug parameters release 21]
[INFO] BUILD SUCCESS
[INFO] Total time: 5.890 s
```

---

## How to Run

```bash
# 1. Start infrastructure
docker-compose up -d postgres redis

# 2. Build and run (development)
cd backend-spring
mvn spring-boot:run

# 3. Verify
curl http://localhost:8000/         # → {"message": "SnapSplit API is running", ...}
curl http://localhost:8000/health   # → {"status": "healthy", "checks": {"database": "healthy"}}
curl http://localhost:8000/docs     # → Swagger UI
```

---

## Key Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Password hashing | BCrypt only | DB will be flushed — no legacy `pbkdf2_sha256` hashes to support |
| JWT secret | New key | DB flush means no existing tokens to worry about |
| Schema management | `ddl-auto: validate` | Existing schema in PostgreSQL, JPA just validates mappings |
| Async framework | Spring `@Async` | Simpler than Celery; sufficient for our AI task volume |
| API docs path | `/docs` | Matches FastAPI's default Swagger UI path |
| Server port | 8000 | Matches Python backend — zero frontend changes |
