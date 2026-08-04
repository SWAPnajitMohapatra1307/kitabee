# Kitabee

A book recommendation app that helps readers discover their next favourite read.

Built with React Native + Expo (mobile), FastAPI (backend), PostgreSQL, Redis, and a recommendation engine (in progress).

---

## Status

**Week 2 complete — auth, user system, and full backend API live.**

| Day | What shipped |
|-----|-------------|
| 1 | Docs, architecture decisions, project setup |
| 2 | PostgreSQL schema — 7 tables, Alembic migration applied |
| 3 | Google Books API client — search, detail, retry, 82 tests |
| 4 | Redis cache layer — client, decorator, health endpoint, 30 tests |
| 5 | Book search endpoint — validation, envelope, 503 handling, 25 tests |
| 6 | Book detail + similar endpoints — DB persistence, UUID lookup, 27 tests |
| 7 | Refactor, coverage to 82%, README |
| 8 | JWT authentication — access + refresh tokens, 207 tests |
| 9 | User registration + login endpoints, 237 tests |
| 10 | User profile + password change + soft delete, 267 tests |
| 11 | Ratings system — upsert, delete, book stats recalc, 294 tests |
| 12 | Library management — add, list, update, remove, 322 tests |
| 13 | User preferences — genres, theme, notifications, onboarding, 333 tests |
| 14 | Week 2 integration testing — E2E flow, bug fixes, 351 tests |

Current: 351 tests, 78% coverage.

---

## Stack

| Layer | Technology |
|-------|-----------|
| Mobile | React Native + Expo (Week 3+) |
| Backend | FastAPI + Python 3.11 |
| Database | PostgreSQL 15 (via Docker) |
| Cache | Redis 7 (via Docker) |
| External API | Google Books API |
| ORM | SQLAlchemy 2 async |
| Migrations | Alembic |
| Testing | pytest + httpx + respx |

---

## Local Setup

### Prerequisites

- Python 3.11
- Docker Desktop
- Google Books API key ([get one here](https://developers.google.com/books/docs/v1/using#APIKey))

### 1. Clone

```bash
git clone https://github.com/SWAPnajitMohapatra1307/kitabee.git
cd kitabee
2. Start Docker containers
PowerShell

docker run -d --name kitabee_postgres \
  -e POSTGRES_USER=kitabee \
  -e POSTGRES_PASSWORD=kitabee \
  -e POSTGRES_DB=kitabee \
  -p 5433:5432 \
  postgres:15

docker run -d --name kitabee_redis \
  -p 6379:6379 \
  redis:7
On subsequent runs:

PowerShell

docker start kitabee_postgres
docker start kitabee_redis
3. Python environment
PowerShell

cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
4. Environment variables
PowerShell

copy .env.example .env
Edit .env:

env

DATABASE_URL=postgresql+asyncpg://kitabee:kitabee@localhost:5433/kitabee
REDIS_URL=redis://localhost:6379
GOOGLE_BOOKS_API_KEY=your_key_here
5. Run migrations
PowerShell

alembic upgrade head
6. Start the server
PowerShell

uvicorn src.main:app --reload
API available at http://localhost:8000.

API Endpoints
All responses follow the standard envelope:

JSON

{
  "success": true,
  "data": {},
  "meta": {
    "timestamp": "2025-01-01T00:00:00+00:00",
    "version": "v1"
  }
}
Errors:

JSON

{
  "success": false,
  "error": {
    "code": "BOOK_NOT_FOUND",
    "message": "No book found with id <uuid>."
  },
  "meta": {
    "timestamp": "2025-01-01T00:00:00+00:00",
    "version": "v1"
  }
}
GET /health
Basic liveness check.

Response

JSON

{
  "success": true,
  "data": { "status": "ok" },
  "meta": { "timestamp": "...", "version": "v1" }
}
GET /health/cache
Redis connectivity and metrics.

Response — connected

JSON

{
  "success": true,
  "data": {
    "connected": true,
    "info": {
      "connected_clients": 1,
      "used_memory_human": "1.00M",
      "keyspace_hits": 42,
      "keyspace_misses": 7,
      "uptime_in_seconds": 3600
    }
  },
  "meta": { "timestamp": "...", "version": "v1" }
}
Response — Redis down

JSON

{
  "success": true,
  "data": { "connected": false, "info": null },
  "meta": { "timestamp": "...", "version": "v1" }
}
GET /api/v1/books/search
Search books via Google Books API. Results are persisted to PostgreSQL.

Query parameters

Parameter	Type	Required	Default	Constraints
q	string	yes	—	2–200 chars
limit	int	no	20	1–40
offset	int	no	0	≥ 0
Example

text

GET /api/v1/books/search?q=dune&limit=5
Response

JSON

{
  "success": true,
  "data": {
    "query": "dune",
    "total_count": 5,
    "limit": 5,
    "offset": 0,
    "results": [
      {
        "google_books_id": "ydQR_YorfqMC",
        "title": "Dune",
        "authors": ["Frank Herbert"],
        "description": "...",
        "categories": ["Fiction"],
        "thumbnail_url": "http://...",
        "average_rating": 4.5,
        "ratings_count": 1200,
        "published_date": "1965",
        "publisher": "Chilton Books",
        "page_count": 412,
        "language": "en"
      }
    ]
  },
  "meta": { "timestamp": "...", "version": "v1" }
}
GET /api/v1/books/{book_id}
Fetch full book details by Kitabee UUID. UUID is assigned on first search hit.

Path parameters

Parameter	Type	Description
book_id	UUID	Kitabee internal book ID
Example

text

GET /api/v1/books/123e4567-e89b-12d3-a456-426614174000
Response

JSON

{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "external_id": "ydQR_YorfqMC",
    "external_source": "google_books",
    "title": "Dune",
    "authors": ["Frank Herbert"],
    "kitabee_rating": null,
    "kitabee_ratings_count": 0,
    "metadata_json": {}
  },
  "meta": { "timestamp": "...", "version": "v1" }
}
Errors

Code	Status	Meaning
BOOK_NOT_FOUND	404	UUID not in database
UPSTREAM_UNAVAILABLE	503	Google Books API failed
GET /api/v1/books/{book_id}/similar
Find books similar to a given Kitabee UUID. Similarity based on author + genre.

Path parameters

Parameter	Type	Description
book_id	UUID	Kitabee internal book ID
Query parameters

Parameter	Type	Required	Default	Constraints
limit	int	no	10	1–40
Example

text

GET /api/v1/books/123e4567-e89b-12d3-a456-426614174000/similar?limit=5
Response — same shape as /search.

Errors

Code	Status	Meaning
BOOK_NOT_FOUND	404	UUID not in database
UPSTREAM_UNAVAILABLE	503	Google Books API failed
Running Tests
PowerShell

# All tests
pytest

# With coverage
pytest --cov=src --cov-report=term-missing

# Single file
pytest tests/test_books_api.py -v
Current: 182 tests, 82% coverage.

Project Structure
text

kitabee/
    backend/
        src/
            api/
                deps.py          # FastAPI dependency providers
                response.py      # Envelope helpers (single source of truth)
                routes/
                    health.py    # GET /health, GET /health/cache
                    books.py     # GET /api/v1/books/*
            cache/
                redis_client.py  # Redis wrapper
                decorators.py    # @cached decorator
            database/
                models/          # 7 SQLAlchemy models
                crud/
                    book.py      # Repository layer — upsert, lookup
                session.py       # AsyncSessionLocal factory
            external/
                google_books.py  # Google Books API client
            services/
                book_service.py  # Business logic layer
            schemas/
                book.py          # Pydantic request/response models
            config.py
            main.py              # App entry point, lifespan, exception handlers
        tests/                   # 182 tests
        alembic/                 # Migrations
Roadmap
Week 2 — Auth (JWT), user profiles, library management ✅
Week 3 — ML recommendation engine, ratings
Week 4 — React Native mobile app
Week 5 — Polish, deployment, launch
text


Save. Confirm it saved:

```powershell
Get-Content "C:\Users\CONFUSED CRUSADER\Documents\kitabee\README.md" | Select-Object -First 5