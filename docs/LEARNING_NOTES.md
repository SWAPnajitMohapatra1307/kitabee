# Kitabee — Learning Notes

Lessons learned during development. Updated at end of each week.
Raw and honest — what worked, what didn't, what to remember.

---

## Week 1 — Backend Foundation (Days 1–7)

### Python / FastAPI

**Circular imports with SQLAlchemy model registry**
- `base.py` imports all models to register them with `DeclarativeBase`
- Importing a model directly from its file (`models/book.py`) inside
  code that `base.py` also touches causes circular import at runtime
- Fix: always import ORM models from `src.database.base`, not from
  the individual model file
- Lesson: when you have a registry pattern, treat the registry as the
  single import source for everything it owns

**SQLAlchemy reserved attribute names**
- `metadata` is a reserved attribute on SQLAlchemy's `DeclarativeBase`
- Naming a column `metadata` causes silent or confusing errors
- Fix: name the Python attribute `metadata_json`, keep the DB column
  name as `metadata` via `Column("metadata", ...)`
- Lesson: check SQLAlchemy reserved names before finalising schema

**`TYPE_CHECKING` forward references**
- Forward refs in `TYPE_CHECKING` blocks must match the exact filename
  on disk, not just the class name
- A mismatch silently fails at import time or gives confusing errors
- Lesson: verify every forward ref against the actual file path

**FastAPI route order is critical**
- FastAPI matches routes top-to-bottom
- `/search` must be declared before `/{book_id}/similar` before
  `/{book_id}` or FastAPI matches the wrong handler
- `GET /books/search` would be matched as `GET /books/{book_id}`
  with `book_id = "search"` if order is wrong
- Lesson: always put specific routes before parameterised routes

**`bool({})` vs `is not None`**
- `bool({})` is `False` even when Redis responded with an empty dict
- Empty dict = connected but no data; `None` = not connected
- Always use explicit `is not None` checks for optional return values
- Lesson: never use truthiness checks on containers when None-ness
  is what you actually care about

**FastAPI dependency wiring bug**
- `deps.py` was returning `BookService(google_books_client)` — missing
  the `db` argument that `BookService.__init__` required
- FastAPI didn't catch this at startup; it would only fail at runtime
  when a route tried to use the DB
- Fix: `deps.py` now injects both `google_books` and `db`
- Lesson: dependency providers are not type-checked by FastAPI —
  unit test them explicitly (`test_deps.py`)

---

### Testing

**`app.dependency_overrides` pattern**
- Cleanest way to stub FastAPI dependencies in tests
- Override at test level, reset after, never bleed between tests
- Avoids patching internals — tests stay close to real request path
- Pattern established Day 5, used consistently through Day 7

**`ASGITransport` + `httpx.AsyncClient`**
- Prefer over `TestClient` for async FastAPI apps
- `TestClient` wraps async in sync — hides async bugs
- `httpx.AsyncClient(transport=ASGITransport(app=app))` tests the
  real async path end-to-end

**Stub services over mocking internals**
- `StubBookService` that returns controlled data is more stable than
  patching `GoogleBooksClient` internals
- Stubs are explicit about what the route layer actually needs
- Mocks on internals break when internals change; stubs don't

**Never mock at the wrong level**
- For `test_deps.py`: mock `AsyncSessionLocal` at the deps module level
  (`src.api.deps.AsyncSessionLocal`), not at the session module level
- Patch where the name is used, not where it is defined

**`fast_retry` fixture pattern**
- Tenacity retry logic slows tests with real wait times
- Monkeypatch `wait_exponential` to `wait_fixed(0)` at the source
  module level before import
- Must patch the module-level reference, not the stdlib reference

---

### External APIs

**Never leak API keys in error messages**
- `httpx` response objects carry the full URL including query params
- Logging `response.url` or putting it in an exception message leaks
  the API key
- Fix: strip query string — `str(url).split("?")[0]`
- Lesson: always audit what goes into logs and exception messages

**Google Books quirks**
- Returns 503 (not 404) for nonexistent volume IDs
- Empty search results return 200 with `totalItems: 0`, not 404
- `imageLinks` key is missing entirely when no cover exists
- `pageCount` can be `False` (bool) instead of `None` or `0`
- Dates can be `"1965"`, `"1965-01"`, or `"1965-06-01"` — all valid
- Lesson: external APIs lie about types; defensive mapping is not
  paranoia, it is required

---

### Caching

**Never cache None or exceptions**
- Caching a `None` result poisons the cache for the TTL duration
- A transient failure becomes a permanent miss until TTL expires
- Fix: check result before writing to cache, skip if None

**Manual cache-aside beats decorator for external clients**
- `@cached` decorator puts `self` in the cache key hash
- For instance methods this produces unstable keys across requests
- Manual cache-aside in the method body gives full control over
  key naming and skip conditions

**Redis failure at startup is non-fatal**
- App should boot and serve requests even if Redis is down
- Cache misses are acceptable; hard failures are not
- Log a warning at startup, degrade gracefully

---

### Database

**Upsert via lookup + IntegrityError fallback**
- Cleaner than raw `INSERT ... ON CONFLICT` for async SQLAlchemy
- Pattern: lookup → update if found → insert → catch IntegrityError
  → lookup again → update
- Handles race conditions without needing raw SQL
- Lesson: async SQLAlchemy makes ON CONFLICT awkward; this pattern
  is the pragmatic alternative

**DB persistence as search side-effect**
- Persisting books during search means detail lookups always hit DB
- Failures in persistence must never bubble up to the caller
- Pattern: wrap each persist in try/except, log warning, continue
- Lesson: side-effects in request handlers must be fault-tolerant

**`_MUTABLE_FIELDS` tuple for upsert updates**
- Listing every field explicitly in `_apply_book_updates` is fragile
- When schema grows, easy to forget to add new field to the update
- Fix: define `_MUTABLE_FIELDS` tuple, loop with `setattr`
- Adding a new mutable field = one line in the tuple

---

## Week 2 — Auth & User System (Days 8–14)

*To be filled in after Week 2.*

---

## Week 3 — ML Recommendation Engine (Days 15–21)

*To be filled in after Week 3.*

---

## Week 4 — Mobile App (Days 22–28)

*To be filled in after Week 4.*

---

## Week 5 — Deployment & Launch (Days 29–35)

*To be filled in after Week 5.*