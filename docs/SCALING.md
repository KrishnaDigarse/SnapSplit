# Scalability & Load Testing

## Strategy
We use **k6** for load testing to simulate user traffic and identify bottlenecks.

## Scenarios
Scripts are located in `backend/tests/load/`.

1.  **Auth**: Simulates login bursts.
2.  **Groups**: Tests fetching group lists under load.
3.  **Expenses**: Tests expense creation throughput.

## Scaling Plan
- **Horizontal Scaling**: The Stateless Backend Architecture allows running multiple API replicas.
- **Async Workers**: Celery workers can be scaled independently to handle AI load.
- **Database**: Use connection pooling (SQLAlchemy) and read replicas (future).

## Installation
You need to install k6 first.

**Windows (using Winget):**
```powershell
winget install k6 --source winget
```

**Windows (using Chocolatey):**
```powershell
choco install k6
```

**Mac (using Homebrew):**
```bash
brew install k6
```

## Running Tests
After installing (you may need to restart your terminal), run:
```bash
k6 run backend/tests/load/auth.js
```
