# SnapSplit - Expense Splitting Application

A full-stack expense splitting application (Splitwise-like) with AI-powered bill scanning, built with FastAPI and PostgreSQL.

## Features

- 👥 **Friends & Groups** - Manage friendships and create expense groups
- 💰 **Manual + Bill-based Expenses** - Add expenses manually or scan bills
- 📝 **Item-level Splits** - Split expenses by individual items
- 💳 **Partial Settlements** - Track and settle debts incrementally
- 🤖 **AI Pipeline** - Async OCR processing for bill images (coming soon)

## Tech Stack

- **Backend**: FastAPI, Python 3.10+
- **Database**: PostgreSQL 15 (with Connection Pooling)
- **Cache**: Redis 7
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Containerization**: Docker & Docker Compose
- **Testing**: k6 (Load Testing)

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.10+

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd SnapSplit
   ```

2. **Start the infrastructure**
   ```bash
   docker-compose up -d
   ```

3. **Set up Python environment**
   ```bash
   cd backend
   python -m venv venv
   
   # Windows
   .\venv\Scripts\Activate.ps1
   
   # Linux/Mac
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`

## Database Schema

The application uses a comprehensive PostgreSQL schema with:

- **10 tables**: users, friends, groups, expenses, splits, settlements, etc.
- **6 native ENUMs**: for status tracking and type safety
- **UUID primary keys**: for better security and scalability
- **Comprehensive indexes**: for optimal query performance

### Core Models

- `users` - User accounts and authentication
- `friend_requests` - Friend connection requests
- `friends` - Established friendships
- `groups` - Expense groups (including direct/1-on-1)
- `group_members` - Group membership tracking
- `expenses` - Expense records with OCR support
- `expense_items` - Individual items within expenses
- `splits` - How expenses are divided among users
- `settlements` - Payment records between users
- `group_balances` - Cached balance calculations

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Development

### Database Operations

```bash
# Connect to PostgreSQL
docker exec -it snapsplit_postgres psql -U snapsplit_user -d snapsplit_db

# View tables
\dt

# View table structure
\d+ users
```

### Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Environment Variables

Copy `.env.example` to `.env` and update:

```bash
DATABASE_URL=postgresql://snapsplit_user:snapsplit_password@127.0.0.1:5432/snapsplit_db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-in-production
ENVIRONMENT=development
```

## Project Structure

```
SnapSplit/
├── docker-compose.yml          # Docker services
├── .env                         # Environment variables
└── backend/
    ├── main.py                  # FastAPI application
    ├── requirements.txt         # Dependencies
    ├── alembic/                 # Database migrations
    └── app/
        ├── database.py          # Database configuration
        └── models/              # SQLAlchemy models
```

## License

[Your License Here]

## Load Testing & Performance

The application is validated for high-concurrency production scenarios using **k6**.

- **Verified Environment**: PostgreSQL 14+ with `psycopg2` driver and SQLAlchemy Connection Pooling.
- **Benchmarks**: Verified stable up to 20 concurrent VUs with <50ms p95 latency on core endpoints.
- **Reports**: See [docs/LOAD_TESTING_POSTGRES.md](docs/LOAD_TESTING_POSTGRES.md) for detailed results.

### Running Load Tests
```bash
# Install k6
winget install k6  # Windows
brew install k6    # Mac

# Run scenarios
k6 run backend/tests/load/auth.js
k6 run backend/tests/load/groups.js
k6 run backend/tests/load/expenses.js
```

## Contributing

[Contributing guidelines]
