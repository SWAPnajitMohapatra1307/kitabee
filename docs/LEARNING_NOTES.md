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

## Week 3 — ML Recommendation Engine (Days 15–21)

### TF-IDF + Content Similarity (Day 15)

**ngram_range=(1,2) captures phrases that unigrams miss**
- Unigrams: "dark", "fantasy" — bigrams: "dark fantasy"
- Bigrams dramatically improve similarity between books in the same subgenre
- max_features=5000 keeps the matrix sparse enough to be fast
- Lesson: always prototype with bigrams for book/text metadata — the quality
  jump over unigrams is worth the extra features

**Repeat genre/category tokens to boost their weight**
- TF-IDF weights rare terms higher; common genre words get diluted
- Fix: concatenate categories twice into the corpus string
- Effect: genre similarity outweighs random word overlap between blurbs
- Lesson: manual feature weighting via repetition is simpler and more
  interpretable than custom TF-IDF subclasses

**ContentVectorizer must be content-type agnostic**
- Books and comics share the same corpus structure (title, authors, categories, description)
- One vectorizer handles both — no separate BookVectorizer and ComicVectorizer
- Lesson: design ML components around the data shape, not the content type label

**Save/load pattern prevents cold start on restart**
- Fitting TF-IDF on every startup is expensive if catalog grows
- `save()` / `load()` via joblib persists the fitted matrix and ID list
- Lesson: always build persistence into ML components from day one

---

### External API Clients (Day 16)

**Comic Vine blocks the default httpx User-Agent**
- Default httpx agent returns 403 immediately
- Fix: set `User-Agent: Mozilla/5.0 ... Chrome/120.0.0.0`
- Lesson: always check User-Agent requirements for third-party APIs before
  writing tests — a missing header wastes hours

**Comic Vine API errors return HTTP 200**
- A bad API key or invalid endpoint returns 200 with `status_code != 1` in body
- Must check both the HTTP status code AND the body status code
- Lesson: never trust HTTP status alone for APIs that embed their own error codes

**Internet Archive is fully public — no key needed**
- No rate limiting documented, no auth required
- Lesson: always check if a public API really needs auth before adding complexity

**ID prefixes prevent cross-source collisions**
- `cv_12345` for Comic Vine, `ia_someid` for Internet Archive, `gb_volumeid` for Google Books
- Downstream code can detect source from prefix without extra metadata
- Lesson: embed the source in the ID from day one — retrofitting this later
  is painful

**Format priority matters for Internet Archive**
- EPUB > Text PDF > DjVu > CBZ > CBR
- EPUB is best for text books; CBZ/CBR for comics
- Lesson: define format priority explicitly and document the reasoning —
  "best format" is not obvious to future maintainers

---

### Collection Engine (Day 17)

**Keyword scoring beats ML for short sparse metadata**
- KMeans on raw blurbs gives noisy clusters when descriptions are 2-3 sentences
- Keyword scoring with primary (weight 2) and secondary (weight 1) terms
  gives interpretable, testable, deterministic mood labels
- Lesson: reach for interpretable heuristics before ML when data is sparse

**Stem matching via substring handles inflections without NLTK**
- `"motivat"` matches "motivate", "motivating", "motivated", "motivation"
- No NLTK dependency, no tokenization overhead, no model download
- Lesson: simple substring matching covers 90% of stemming needs for
  domain-specific keyword lists

**KMeans k must be capped at n_samples**
- sklearn raises if k > n_samples
- Always: `k = min(desired_k, len(items))`
- Lesson: any ML component that accepts a hyperparameter must validate
  it against the actual data size

**Deterministic titles via md5(sorted cluster IDs)**
- Same cluster of items always gets the same title across restarts
- `md5("|".join(sorted(ids))).hexdigest()` → index into title list
- Lesson: determinism in ML output is important for caching and debugging —
  random seeds are not enough if item membership changes

**Special collections are metadata-driven, not ML-driven**
- "Free to Read Right Now": `is_public_domain=True` or `source=internet_archive`
- "New This Week": `published_year >= 2023`
- These never need clustering — pure filter logic
- Lesson: not everything on the home screen needs ML; know when a filter
  is the right tool

**PowerShell python -c breaks on nested quotes**
- Single-quoted outer string + double-quoted inner = parse error
- Fix: write smoke test to a temp `.py` file and run that instead
- Lesson: establish this pattern early, use it for every multi-line
  Python one-liner in PowerShell

---

### Series Intelligence (Day 18)

**Always inspect real client method signatures before writing routes**
- Assumed `get_volume()` returns issues list — it does not
- `get_volume()` returns volume metadata only
- Comic series items fetched via `search_comics(series_name)`
- Lesson: `inspect.signature()` before writing any code that calls
  an external client method

**Confidence-weighted rule engine is more honest than binary detection**
- Rule 1 Comic Vine volume+issue: 0.95 (most reliable)
- Rule 2 Google Books seriesInfo: 0.90
- Rule 3 title pattern Book N: 0.60
- Rule 4 keywords saga/trilogy: 0.40
- Downstream consumers can threshold on confidence rather than trusting binary flags
- Lesson: express uncertainty in outputs — binary true/false hides information

**Module-level private helpers make routes testable without DB**
- `_fetch_item(item_id)` and `_fetch_series_items(series_name, source)`
  as module-level functions, not inline in the route handler
- Monkeypatch at the module level in tests — no DB needed
- Lesson: route-level helper functions are the correct seam for testing
  routes that call external services

---

### Collaborative Filtering (Day 19)

**String coercion on user_id and content_id prevents silent mismatches**
- Ratings from DB have integer user IDs; ML components may see strings
- Always `str(user_id)` and `str(content_id)` at matrix build time
- Lesson: normalise ID types at the boundary between DB and ML layers

**Cold start is a hard requirement, not an edge case**
- Fewer than 2 ratings → no meaningful similarity → return empty list
- Never return random items as "recommendations" to a cold-start user
- Lesson: cold start must be explicitly handled and tested — do not let
  the happy path silently degrade into noise

**Cosine similarity on zero vectors returns 0 without crashing**
- A user who rated only one item produces a zero vector after centering
- sklearn's cosine_similarity handles this — returns 0.0, not NaN or error
- Lesson: verify numerical edge cases before shipping any similarity function

---

### Neural Recommender (Day 20)

**Keras GPU warnings on Windows are normal — not errors**
- `oneDNN custom operations are on` is informational
- `TF_CPP_MIN_LOG_LEVEL=3` silences TF logs in test output
- `TF_ENABLE_ONEDNN_OPTS=0` suppresses the oneDNN notice
- Lesson: set both env vars at top of every test file that imports TF

**Embedding + dot product is the minimal viable neural recommender**
- User embedding (n_factors,) · Item embedding (n_factors,) = predicted rating
- No hidden layers needed for a proof-of-concept — keeps training fast
- Cold start: fewer than min_ratings → `is_fitted = False` → fall back to content
- Lesson: start minimal; add complexity only when metrics prove it helps

**fit() must return self**
- Enables method chaining: `nr.fit(ratings).recommend(...)`
- Also enables the cold-start early return to be consistent:
  `return self` whether or not training ran
- Lesson: always return self from fit() in scikit-learn-style classes

**_reset_state() prevents stale embeddings across re-fits**
- If fit() is called twice, old model + user/item maps must be cleared
- Otherwise new ratings silently use old index mappings
- Lesson: stateful ML classes must have an explicit reset mechanism

---

### Hybrid Engine (Day 20)

**Blend signals via rank-decay, not raw scores**
- Content similarity, collaborative rank, neural score all live on different scales
- Rank-decay: score = 1 / (rank + 1) normalises all signals to [0, 1]
- Weighted sum: `content_weight * sim + collab_weight * rank_decay + neural_weight * neural_score`
- Lesson: when blending heterogeneous signals, normalise to rank first

**All external calls must be wrapped in try/except**
- If collaborative filter crashes mid-recommend, hybrid must still return something
- Pattern: try the signal, log the exception, skip that signal's contribution
- Lesson: in a blended system, one component's failure must never kill the response

**Backfill unseen items when no scored candidates exist**
- Cold-start user has no ratings → no seeds → no scored candidates
- Fall back to shuffled unseen catalog items so the response is never empty
- Lesson: every recommender must have a non-empty fallback path

**_catalog_to_metadata() bridges the id/content_id key mismatch**
- CollectionEngine uses `id` key (from raw catalog dicts)
- Personalizer and HybridEngine use `content_id` key
- Bridge: `[{**item, "content_id": item["id"]} for item in catalog]`
- Lesson: document key naming conventions per component and bridge explicitly
  at the service layer — do not fix it inside the ML components

---

### CollectionService (Day 20)

**Row build order matters for perceived quality**
- "Because you loved X" first — most personal, highest engagement
- "Picked for You" second — broad personalisation
- Cluster rows third — mood/genre themed
- Special rows last — free, new
- Lesson: order signals editorial intent; do not let it be arbitrary

**Deduplication by row id prevents duplicate rows on re-build**
- CollectionEngine may produce a cluster row with the same id as a special row
- Track seen row ids in a set, skip duplicates
- Lesson: any system that assembles rows from multiple sources needs deduplication

**Graceful degradation per row, not per response**
- If "Because you loved" crashes → skip it, build the rest
- If cluster engine crashes → skip cluster rows, return special rows
- Never let one row failure kill the entire home screen
- Lesson: wrap each row builder in try/except independently

---

### ML Evaluation (Day 21)

**precision@k penalises short recommendation lists**
- If you recommend 1 item and k=10, denominator is still 10
- A single hit gives precision = 0.1, not 1.0
- This is correct — the system is penalised for not filling the top-k slots
- Lesson: understand what the denominator is before interpreting metric values

**NDCG rewards correct ranking, not just correct items**
- Two systems with same hits but different rank positions get different NDCG
- Ideal DCG (IDCG) normalises by the best possible ranking of the relevant items
- Lesson: use NDCG when rank position matters, not just presence in top-k

**Catalog coverage reveals popularity bias**
- A system that only recommends the top 100 popular items will have low coverage
- Low coverage = the long tail never gets surfaced to any user
- Lesson: track coverage alongside accuracy metrics — optimising accuracy
  alone produces popularity bias

**Intra-list diversity measures recommendation variety**
- Average pairwise cosine distance between recommended items
- 0.0 = all items identical; 1.0 = all items orthogonal
- Lesson: diversity is a separate axis from accuracy — a system can be
  accurate but completely non-diverse

**Float epsilon dust in cosine similarity**
- Two identical vectors produce similarity = 1.0 - 2.22e-16 due to float arithmetic
- `math.isclose(value, 1.0, abs_tol=1e-12)` clamps cleanly to 1.0
- Lesson: always clamp similarity values to [-1, 1] before downstream use

**Always inspect real API signatures before writing tests**
- Assumed `CollaborativeFilter(min_ratings=999)` — parameter does not exist
- Assumed `create_token(...)` — function is `create_access_token(user_id: UUID)`
- Assumed `SeriesDetector.detect(items)` — takes a single item dict, not a list
- Fix each time: `inspect.signature(fn)` before writing any call
- Lesson: assumptions about internal APIs cost more time to fix than
  the 30 seconds it takes to inspect the signature

---

### Week 3 Numbers

| Metric | Value |
|--------|-------|
| Days | 15-21 (7 days) |
| New tests | 441 |
| Total tests | 792 |
| Total coverage | 86% |
| ML modules built | 9 |
| ML modules at ≥96% coverage | 10/10 |
| New files created | 18 |
| Regressions | 0 |

### ML Modules Built This Week

| Module | Purpose | Coverage |
|--------|---------|----------|
| vectorizer.py | TF-IDF content similarity | 100% |
| mood_detector.py | Keyword mood labelling | 100% |
| collection_engine.py | KMeans + Netflix titles | 100% |
| series_detector.py | 4-rule series detection | 100% |
| series_builder.py | Reading order labels | 100% |
| collaborative.py | KNN user-based filtering | 99% |
| personalizer.py | Rank + filter + inject | 100% |
| neural.py | Keras embedding model | 99% |
| hybrid.py | Blended signal engine | 98% |
| evaluation.py | IR metrics | 96% |

## Week 4 — Mobile App (Days 22–28)

*To be filled in after Week 4.*

---

## Week 5 — Deployment & Launch (Days 29–35)

*To be filled in after Week 5.*