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

## Week 2 — Auth & User System (Days 8—14)

### Authentication

**bcrypt must be pinned to 4.0.1**
- Newer bcrypt versions break passlib integration silently
- Always pin: `bcrypt==4.0.1` in requirements.txt
- Lesson: third-party auth libraries have fragile transitive dependencies;
  pin everything that touches passwords

**72-byte bcrypt hard limit**
- bcrypt silently truncates passwords longer than 72 bytes
- Two different passwords that share the same first 72 bytes will match
- Fix: enforce the limit explicitly in both hash_password and verify_password
- Lesson: never trust a library to enforce its own constraints; check at
  the boundary you control

**Token type claim is required**
- Access and refresh tokens must carry a "type" claim ("access" or "refresh")
- Without it, a refresh token could be used where an access token is expected
- Lesson: JWTs are only as safe as the claims you verify

**FastAPI OAuth2PasswordBearer returns 403, not 401**
- When no credentials are sent, FastAPI returns 403 FORBIDDEN
- Tests that assert 401 on missing auth will fail
- Lesson: test the actual framework behaviour, not the RFC behaviour

---

### Testing

**monkeypatch target must be where the name is used, not where it is defined**
- `soft_delete_user` is defined in `crud/user.py` but imported into
  `routes/users.py`
- Patching `crud.user.soft_delete_user` has no effect on the route
- Patch `src.api.routes.users.soft_delete_user` instead
- Lesson: always patch the import reference, not the definition

**Async stubs must be async**
- If a route does `await some_function(...)`, the monkeypatched replacement
  must also be an async function
- A plain lambda or sync function causes `TypeError: object can't be used
  in 'await' expression`
- Lesson: match the async signature of whatever you are replacing

**dependency_overrides is the cleanest auth bypass**
- `app.dependency_overrides[get_current_user] = lambda: fake_user`
- Cleaner than patching JWT internals
- Always clear overrides after each test via autouse fixture
- Lesson: override at the dependency boundary, not inside the handler

**SimpleNamespace for fake ORM objects**
- SQLAlchemy model instances have descriptor machinery that crashes when
  accessed outside a session
- SimpleNamespace gives plain attribute access with no descriptor overhead
- Always use `defaults.update(kwargs)` then `SimpleNamespace(**defaults)`
- Never pass **kwargs directly alongside hardcoded fields — causes duplicate
  keyword argument crash

---

### API Design

**PUT = full replace, PATCH = partial update**
- Preferences uses PUT: all fields have defaults, omitted fields reset to defaults
- Profile uses PATCH: only sent fields are updated, omitted fields unchanged
- Lesson: choose the verb based on semantics, not convenience

**Soft delete vs hard delete**
- Users are soft-deleted: `deleted_at` timestamp set, row kept
- Ratings and library items are hard-deleted: row removed
- Lesson: decide per entity based on audit and recovery requirements

**Upsert via lookup + IntegrityError fallback**
- Pattern: SELECT → update if found → INSERT → catch IntegrityError →
  SELECT again → update
- Handles race conditions without raw SQL ON CONFLICT
- Lesson: async SQLAlchemy makes ON CONFLICT awkward; this pattern is the
  pragmatic alternative

**onboarding_completed lives on User, not UserPreferences**
- Onboarding state is a user account concern, not a preferences concern
- complete_onboarding is idempotent: if already True, return user unchanged
- Lesson: put state on the entity that owns the lifecycle

---

### Integration Testing

**E2E tests should cover the full happy path in one file**
- Register → login → profile → rate → library → preferences → onboarding → delete
- Catches contract mismatches between route, service, and schema layers
- Lesson: unit tests catch isolated bugs; E2E tests catch integration gaps

**78% coverage at end of Week 2 with 351 tests**
- Route and schema layers: 95-100% covered
- Crud and service layers: 25-52% covered (stubbed out in most tests)
- Lesson: high route coverage does not mean high business logic coverage;
  crud/service layers need dedicated unit tests in a future pass
  
## Week 3 — ML Recommendation Engine (Days 15–21)

*To be filled in after Week 3.*

---

## Week 4 — Mobile App (Days 22–28)

*To be filled in after Week 4.*

---

## Week 5 — Deployment & Launch (Days 29–35)

*To be filled in after Week 5.*