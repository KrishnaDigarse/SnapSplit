# SnapSplit — Expense Splitting Application

A full-stack expense splitting app with AI-powered bill scanning, built with **Java Spring Boot** and **PostgreSQL**.

## Features

- 👥 **Friends & Groups** — Manage friendships and create expense groups
- 💰 **Manual + Bill-based Expenses** — Add expenses manually or scan bills
- 📝 **Item-level Splits** — Split expenses by individual items
- 💳 **Partial Settlements** — Track and settle debts incrementally
- 🤖 **AI Pipeline** — OCR + LLM bill processing (Tesseract + Groq)
- ⚡ **Real-time** — WebSocket notifications via STOMP

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Java 21, Spring Boot 3.4 |
| **Database** | PostgreSQL 15 |
| **Cache** | Redis 7 |
| **ORM** | Hibernate / Spring Data JPA |
| **Auth** | JWT (jjwt) |
| **AI / OCR** | Tess4J (Tesseract), Groq LLM API |
| **WebSocket** | STOMP over SockJS |
| **API Docs** | SpringDoc OpenAPI (Swagger) |
| **Testing** | JUnit 5, Mockito, AssertJ |
| **Containerization** | Docker & Docker Compose |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Java 21+ (for local dev)
- Maven 3.9+ (or use `./mvnw`)

### Run with Docker (recommended)

```bash
git clone <repository-url>
cd SnapSplit

# Set Groq API key for AI bill scanning (optional)
export GROQ_API_KEY=your-groq-api-key

docker-compose up -d
```

The API is available at `http://localhost:8000`

### Run locally (development)

```bash
# 1. Start infrastructure
docker-compose up -d postgres redis

# 2. Build & run
cd backend-spring
./mvnw spring-boot:run
```

### Run tests

```bash
cd backend-spring
./mvnw test
```

## API Documentation

Once the server is running:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **OpenAPI JSON**: [http://localhost:8000/api-docs](http://localhost:8000/api-docs)

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Register a new user |
| POST | `/api/v1/auth/login` | Login and get JWT |
| POST | `/api/v1/friends/request` | Send friend request |
| PUT | `/api/v1/friends/request/{id}/accept` | Accept friend request |
| GET | `/api/v1/friends` | List friends |
| POST | `/api/v1/groups` | Create a group |
| POST | `/api/v1/groups/{id}/members` | Add member |
| GET | `/api/v1/groups` | List groups |
| POST | `/api/v1/expenses/manual` | Create manual expense |
| POST | `/api/v1/expenses/bill` | Upload bill image (AI) |
| GET | `/api/v1/expenses/{id}/status` | Poll AI processing status |
| POST | `/api/v1/settlements` | Record a settlement |
| GET | `/api/v1/settlements/{groupId}/summary` | Get group balances |

## Project Structure

```
SnapSplit/
├── docker-compose.yml              # Dev: postgres + redis + backend
├── docker-compose.prod.yml         # Prod: + frontend (nginx)
├── backend-spring/
│   ├── Dockerfile
│   ├── pom.xml
│   ├── docs/migration/             # Phase-by-phase migration docs
│   └── src/main/java/com/snapsplit/
│       ├── ai/                     # OCR, LLM, parser
│       ├── config/                 # Async, Cache, WebSocket, Security
│       ├── controller/             # REST endpoints
│       ├── dto/                    # Request/Response objects
│       ├── entity/                 # JPA entities
│       ├── enums/                  # Status types
│       ├── exception/              # Error handling
│       ├── repository/             # Data access
│       ├── security/               # JWT filter
│       ├── service/                # Business logic
│       └── websocket/              # Real-time notifications
└── frontend/                       # React frontend
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SPRING_DATASOURCE_URL` | `jdbc:postgresql://localhost:5432/snapsplit_db` | Database URL |
| `SPRING_DATASOURCE_USERNAME` | `snapsplit_user` | DB username |
| `SPRING_DATASOURCE_PASSWORD` | `snapsplit_password` | DB password |
| `SPRING_DATA_REDIS_HOST` | `localhost` | Redis host |
| `GROQ_API_KEY` | — | Groq API key for AI bill scanning |

## Database

```bash
# Connect to PostgreSQL
docker exec -it snapsplit_postgres psql -U snapsplit_user -d snapsplit_db

# View tables
\dt

# View table structure
\d+ users
```

### Schema: 10 tables with UUID primary keys

`users` · `friend_requests` · `friends` · `groups` · `group_members` · `expenses` · `expense_items` · `splits` · `settlements` · `group_balances`

## Migration Documentation

Detailed migration docs from Python → Java:

| Phase | Doc |
|---|---|
| 0 — Scaffolding | [`phase0_scaffolding.md`](backend-spring/docs/migration/phase0_scaffolding.md) |
| 1 — Entities | [`phase1_entities.md`](backend-spring/docs/migration/phase1_entities.md) |
| 2 — Security | [`phase2_security.md`](backend-spring/docs/migration/phase2_security.md) |
| 3 — Core APIs | [`phase3_core_apis.md`](backend-spring/docs/migration/phase3_core_apis.md) |
| 4 — AI Pipeline | [`phase4_ai_pipeline.md`](backend-spring/docs/migration/phase4_ai_pipeline.md) |
| 5 — Async & WebSocket | [`phase5_async_websocket.md`](backend-spring/docs/migration/phase5_async_websocket.md) |
| 6 — Middleware | [`phase6_middleware.md`](backend-spring/docs/migration/phase6_middleware.md) |
| 7 — Testing | [`phase7_testing.md`](backend-spring/docs/migration/phase7_testing.md) |

## License

MIT
