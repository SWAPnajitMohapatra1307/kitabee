# 📅 Kitabee — Implementation Plan

> **Document Version:** 2.0
> **Last Updated:** [Today's Date]
> **Author:** [Your Name]
> **Timeline:** 5 Weeks (Weeks 1-5)
> **Status:** 🟢 Active
> **Related Docs:** [PRD.md](./PRD.md) | [TECHSPEC.md](./TECHSPEC.md) | [APPFLOW.md](./APPFLOW.md) | [SCHEMA.md](./SCHEMA.md)

---

## 📚 Table of Contents

1. [Overview](#-overview)
2. [Timeline at a Glance](#-timeline-at-a-glance)
3. [Success Metrics](#-success-metrics)
4. [Prerequisites Checklist](#-prerequisites-checklist)
5. [Week 1: Foundation & Book APIs](#-week-1-foundation--book-apis)
6. [Week 2: Auth & User System](#-week-2-auth--user-system)
7. [Week 3: AI/ML Recommendation Engine](#-week-3-aiml-recommendation-engine)
8. [Week 4: Mobile App Development](#-week-4-mobile-app-development)
9. [Week 5: Deployment & Polish](#-week-5-deployment--polish)
10. [Daily Workflow](#-daily-workflow)
11. [Dependency Graph](#-dependency-graph)
12. [Time Estimates](#-time-estimates)
13. [Risk Register](#-risk-register)
14. [Definition of Done](#-definition-of-done)
15. [Buffer & Contingencies](#-buffer--contingencies)
16. [Learning Time Allocation](#-learning-time-allocation)
17. [Communication & Progress Tracking](#-communication--progress-tracking)
18. [Post-Launch Checklist](#-post-launch-checklist)

---

## 🎯 Overview

### Purpose
This document breaks down the Kitabee project into **executable daily tasks** with dependencies, time estimates, and success criteria.

### What Kitabee Is (Updated Vision)
Kitabee is a **books + comics discovery platform** with:
- **Netflix-style themed collection rows** on the home screen (curated by ML)
- **Series reading order guide** for any book series or comic run
- **Free reading** of public domain books and comics via Internet Archive
- **Personalized AI recommendations** powering every collection row
- **Unified library** for books and comics

### Guiding Principles

1. **🏗️ Foundations First** — Database before features
2. **🎯 Vertical Slices** — One feature end-to-end before next
3. **✅ Definition of Done** — Task is not done until tested and documented
4. **📊 Daily Wins** — Every day produces working code
5. **🔄 Iterate Fast** — MVP first, polish later
6. **⏰ Time-box Ruthlessly** — If task exceeds 2x estimate, reassess
7. **📝 Document as You Go** — Future you will thank current you

### Time Commitment Assumption

- **Weekdays:** 3-4 hours/day
- **Weekends:** 6-8 hours/day
- **Total per week:** ~30 hours
- **Total project:** ~150 hours

### What This Plan Assumes

- ✅ Days 1-14 complete (351 tests passing, 78% coverage)
- ✅ All docs read (PRD, TECHSPEC, APPFLOW, SCHEMA)
- ✅ Google Books API key in use
- ✅ GitHub account with SSH set up
- ✅ Can commit at least 4 hours daily

---

## 🗓️ Timeline at a Glance

```
┌──────────────────────────────────────────────────────────────────┐
│                    KITABEE 5-WEEK ROADMAP                        │
└──────────────────────────────────────────────────────────────────┘

WEEK 1: FOUNDATION & BOOK APIs                     [Backend — DONE ✅]
├── Day 1:  ✅ Environment setup + docs
├── Day 2:  ✅ Database + models + Alembic
├── Day 3:  ✅ Google Books API integration (82 tests)
├── Day 4:  ✅ Redis caching layer (30 tests)
├── Day 5:  ✅ Book search endpoint (25 tests)
├── Day 6:  ✅ Book details endpoint (27 tests)
└── Day 7:  ✅ Week 1 review + documentation (182 tests)

WEEK 2: AUTH & USER SYSTEM                         [Backend — DONE ✅]
├── Day 8:  ✅ JWT authentication setup (207 tests)
├── Day 9:  ✅ User registration + login (237 tests)
├── Day 10: ✅ User profile + password security (267 tests)
├── Day 11: ✅ Ratings system (294 tests)
├── Day 12: ✅ Library management (322 tests)
├── Day 13: ✅ User preferences (333 tests)
└── Day 14: ✅ Week 2 integration testing (351 tests, 78% coverage)

WEEK 3: AI/ML ENGINE + COMICS + COLLECTIONS        [ML Focus — NEXT]
├── Day 15: TF-IDF Vectorizer (books foundation)
├── Day 16: Comic Vine API + Internet Archive API clients
├── Day 17: Collection Engine (KMeans + mood detection + title templates)
├── Day 18: Series Intelligence (reading order guide)
├── Day 19: KNN Collaborative Filtering + Personalizer
├── Day 20: Neural Recommender (Keras) + Hybrid Collection API
└── Day 21: ML testing + evaluation + Week 3 review

WEEK 4: MOBILE APP DEVELOPMENT                     [Frontend Focus]
├── Day 22: Expo project + navigation setup
├── Day 23: Auth screens (Login, Register, Onboarding)
├── Day 24: Netflix-style Home screen (collection rows)
├── Day 25: Search screen (books + comics unified)
├── Day 26: Book/comic detail page + series order UI
├── Day 27: Library screen + free reading (EPUB + comics reader)
└── Day 28: Profile + Insights + cross-platform testing

WEEK 5: DEPLOYMENT & POLISH                        [DevOps + Polish]
├── Day 29: Dockerize backend + local prod test
├── Day 30: AWS EC2 setup + PostgreSQL + Redis
├── Day 31: Deploy backend + Nginx + SSL
├── Day 32: Deploy web (Vercel) + Expo publish
├── Day 33: CI/CD (GitHub Actions)
├── Day 34: Demo video + README + Blog post
└── Day 35: Launch! 🚀
```

### Weekly Deliverables

| Week | Deliverable | User Can... |
|------|-------------|-------------|
| **1** | Working book API ✅ | Search books via Swagger |
| **2** | Auth + Rating system ✅ | Register, login, rate books via API |
| **3** | ML Collections + Comics | Get Netflix-style themed collections via API |
| **4** | Mobile app (Expo Go) | Use full app on phone including free reading |
| **5** | Live deployment | Share URL with recruiters |

---

## 📊 Success Metrics

### Quantitative Goals

| Metric | Target | Measured By |
|--------|--------|-------------|
| **Tasks completed on time** | 85%+ | Daily checklist |
| **Backend test coverage** | 70%+ | pytest --cov |
| **API response time (p95)** | < 500ms | Manual testing |
| **Collection generation time** | < 3s | Manual testing |
| **All PRD MVP features shipped** | 100% | Feature checklist |
| **Live demo URL** | Working 24/7 | Uptime check |
| **GitHub commits** | Daily | git log |

### Qualitative Goals

- ✅ Code is readable and documented
- ✅ Netflix-style home screen feels engaging
- ✅ Series order guide is accurate for top 50 series
- ✅ Free reading works smoothly in-app
- ✅ Recruiter can demo in 2 minutes
- ✅ You understand every line you wrote

---

## ✅ Prerequisites Checklist

### Already Complete (Days 1-14)
- [x] Environment setup complete
- [x] All docs read (PRD, TECHSPEC, APPFLOW, SCHEMA)
- [x] Google Books API key in use
- [x] Docker Desktop running
- [x] PostgreSQL + Redis containers verified
- [x] 351 tests passing, 78% coverage
- [x] Auth, ratings, library, preferences all working

### Needed Before Week 3 Starts
- [ ] **Comic Vine API key** — Register free at comicvine.gamespot.com/api
- [ ] **Internet Archive API** — No key needed, free and open
- [ ] **NYT Books API key** — Register free at developer.nytimes.com
- [ ] scikit-learn, Keras, NLTK, TextBlob added to requirements.txt
- [ ] Jupyter installed for ML notebooks

```powershell
# Activate venv first
cd "C:\Users\CONFUSED CRUSADER\Documents\kitabee\backend"
venv\Scripts\activate

# Install ML dependencies
pip install scikit-learn keras tensorflow nltk textblob jupyter pandas numpy

# Get Comic Vine key
# Visit: https://comicvine.gamespot.com/api/
# Add to .env: COMIC_VINE_API_KEY=xxx

# Get NYT key
# Visit: https://developer.nytimes.com/
# Add to .env: NYT_API_KEY=xxx
```

---

## 🏗️ Week 1: Foundation & Book APIs ✅ COMPLETE

### Summary
All Week 1 goals met. 182 tests passing by end of Day 7.

- Day 1: Environment setup + docs ✅
- Day 2: Database + models + Alembic (7 tables) ✅
- Day 3: Google Books API client (82 tests) ✅
- Day 4: Redis cache + decorator (30 tests) ✅
- Day 5: Book search endpoint (25 tests) ✅
- Day 6: Book details + similar books (27 tests) ✅
- Day 7: Week 1 review + documentation ✅

---

## 🔐 Week 2: Auth & User System ✅ COMPLETE

### Summary
All Week 2 goals met. 351 tests passing, 78% coverage by end of Day 14.

- Day 8: JWT authentication (207 tests) ✅
- Day 9: User registration + login (237 tests) ✅
- Day 10: User profile + password security (267 tests) ✅
- Day 11: Ratings system (294 tests) ✅
- Day 12: Library management (322 tests) ✅
- Day 13: User preferences (333 tests) ✅
- Day 14: Week 2 integration testing (351 tests, 78% coverage) ✅

---

## 🤖 Week 3: AI/ML Engine + Comics + Collections

### 🎯 Week Goal
By end of Week 3:
- TF-IDF vectorizer working for books
- Comic Vine + Internet Archive clients built
- Netflix-style collection engine generating themed rows
- Series reading order guide working
- KNN collaborative filtering personalizing collections
- Neural recommender adding deep personalization
- Full `/api/v1/collections` endpoint serving home screen data

### 📚 Skills You Will Learn
- TF-IDF vectorization + cosine similarity
- KMeans clustering
- NLP mood detection
- KNN collaborative filtering
- Keras neural networks
- External API integration (Comic Vine, Internet Archive)
- Collection title template generation
- Series metadata parsing

---

### 📅 Day 15: TF-IDF Vectorizer (Books Foundation)

**🎯 Goal:** Build TF-IDF vectorizer for books. This is the foundation every other ML module uses.

**⏱️ Estimated Time:** 5-6 hours (2h learning + 3-4h coding)

**📋 Tasks:**

- [ ] **T15.1** Study TF-IDF theory (1h)
  - Term frequency, inverse document frequency
  - Cosine similarity
  - Why it works for book descriptions

- [ ] **T15.2** Create Jupyter notebook (`notebooks/01_tfidf_vectorizer.ipynb`) (1h)
  - Load sample books from DB
  - Preprocess text (lowercase, stopwords, stemming)
  - Build TF-IDF matrix
  - Test similarity queries manually

- [ ] **T15.3** Create `ml/vectorizer.py` (2h)
  - `BookVectorizer` class
  - `fit(books)` — train on book corpus
  - `transform(book)` — vectorize single book
  - `similarity(book_id_a, book_id_b)` — cosine similarity score
  - `similar_to(book_id, top_n)` — find top N similar books
  - `save_model()` / `load_model()` — persist to disk
  - Handles books + comics (content_type agnostic)

- [ ] **T15.4** Create `ml/__init__.py` exports (15min)

- [ ] **T15.5** Test vectorizer (1h)
  - Load 50+ sample books
  - Verify similar books make sense
  - Test with comics data too (if available)
  - Measure Precision@10

- [ ] **T15.6** Commit + update notes (30min)
  ```
  git add .
  git commit -m "feat(ml): TF-IDF vectorizer for books + comics"
  ```

**✅ Success Criteria:**
- [ ] TF-IDF matrix builds without errors
- [ ] Similar books returned for any book_id
- [ ] Results feel relevant (manual inspection)
- [ ] Works for both books and comics
- [ ] Model saves and loads correctly

**🚧 Dependencies:** Week 2 complete, books in DB

**Files to create:**
```
backend/
  notebooks/
    01_tfidf_vectorizer.ipynb
  src/
    ml/
      __init__.py
      vectorizer.py
```

---

### 📅 Day 16: Comic Vine API + Internet Archive API Clients

**🎯 Goal:** Build external API clients for comics metadata and free reading content.

**⏱️ Estimated Time:** 5-6 hours

**📋 Tasks:**

- [ ] **T16.1** Study Comic Vine API (30min)
  - Endpoints: /volumes, /issues, /characters
  - Authentication (api_key param)
  - Rate limits (200 requests/hour)
  - Response structure

- [ ] **T16.2** Study Internet Archive API (30min)
  - Search endpoint: archive.org/advancedsearch.php
  - Metadata endpoint: archive.org/metadata/{identifier}
  - Download links for EPUB/PDF/images
  - What makes content public domain

- [ ] **T16.3** Create `external/comic_vine.py` (2h)
  - `ComicVineClient` class
  - `search_comics(query, max_results)` method
  - `get_comic_details(volume_id)` method
  - `get_series(series_name)` method — returns all issues in order
  - Response mapper → our comic schema
  - Retry logic + timeout (same pattern as google_books.py)
  - Cache with Redis (TTL 24h)

- [ ] **T16.4** Create `external/internet_archive.py` (2h)
  - `InternetArchiveClient` class
  - `search_free_books(query, max_results)` method
  - `search_free_comics(query, max_results)` method
  - `get_reading_links(identifier)` method → returns EPUB/PDF/image URLs
  - `is_public_domain(item)` method → bool check
  - Response mapper → our schema
  - Cache with Redis (TTL 24h)

- [ ] **T16.5** Add new config fields (15min)
  - `COMIC_VINE_API_KEY` to config.py and .env.example
  - `INTERNET_ARCHIVE_BASE_URL` constant

- [ ] **T16.6** Write tests (1h)
  - `tests/test_comic_vine.py` — mock HTTP, test mapper
  - `tests/test_internet_archive.py` — mock HTTP, test public domain check

- [ ] **T16.7** Manual smoke test (30min)
  ```python
  # Quick test in Python shell
  client = ComicVineClient()
  results = await client.search_comics("Batman")
  print(results[0])

  ia_client = InternetArchiveClient()
  books = await ia_client.search_free_books("Dickens")
  print(books[0])
  ```

- [ ] **T16.8** Commit + update notes (30min)
  ```
  git commit -m "feat(external): Comic Vine + Internet Archive API clients"
  ```

**✅ Success Criteria:**
- [ ] Can search comics via Comic Vine
- [ ] Can fetch free books/comics from Internet Archive
- [ ] Public domain check works correctly
- [ ] Redis caching applied to both clients
- [ ] All new tests passing
- [ ] Zero regressions on existing 351 tests

**🚧 Dependencies:** Day 15 complete, Comic Vine API key in .env

**Files to create:**
```
backend/
  src/
    external/
      comic_vine.py
      internet_archive.py
  tests/
    test_comic_vine.py
    test_internet_archive.py
```

---

### 📅 Day 17: Collection Engine (KMeans + Mood + Title Templates)

**🎯 Goal:** Build the engine that groups books/comics into Netflix-style themed collections with catchy titles.

**⏱️ Estimated Time:** 6-7 hours

**📋 Tasks:**

- [ ] **T17.1** Study KMeans clustering (1h)
  - How KMeans works
  - Choosing K (elbow method)
  - Silhouette score for evaluation

- [ ] **T17.2** Create notebook `notebooks/02_collection_engine.ipynb` (1h)
  - Load books + TF-IDF vectors
  - Run KMeans with different K values
  - Inspect clusters manually
  - Test mood word detection on descriptions

- [ ] **T17.3** Create `ml/mood_detector.py` (1.5h)
  - Mood word lists (curated):
    ```python
    MOOD_WORDS = {
        "dark": ["dark", "grim", "bleak", "sinister", "haunting", "disturbing"],
        "funny": ["funny", "comedy", "humor", "laugh", "witty", "hilarious"],
        "epic": ["epic", "vast", "legendary", "grand", "sweeping", "saga"],
        "romantic": ["love", "romance", "heart", "passion", "tender"],
        "thrilling": ["thriller", "suspense", "tension", "chase", "danger"],
        "inspiring": ["inspiring", "courage", "triumph", "hope", "overcome"],
        "cozy": ["cozy", "warm", "comfort", "gentle", "peaceful", "charming"],
    }
    ```
  - `detect_mood(text)` → returns primary mood + confidence
  - `detect_moods(texts)` → batch detection

- [ ] **T17.4** Create `ml/title_templates.py` (1h)
  - Template dictionary keyed by cluster properties:
    ```python
    TEMPLATES = {
        ("fantasy", "epic", "series"): "Epic Worlds Built From Scratch",
        ("thriller", "dark"): "Dark But You Cannot Put It Down",
        ("romance", "contemporary"): "Fall in Love This Weekend",
        ("sci_fi", "epic"): "Universes Worth Getting Lost In",
        ("funny", "contemporary"): "Laugh Out Loud Reads",
        ("inspiring", "nonfiction"): "Books That Change How You Think",
        ("cozy", "mystery"): "Mysteries for a Rainy Afternoon",
        ("same_author",): "From the Mind of {author}",
        ("free_reading",): "Free to Read Right Now",
        ("comics", "beginner"): "Comics — Perfect Starting Points",
        ("series", "complete"): "The Full Journey — Start to Finish",
        ("trending",): "Everyone Is Reading This Right Now",
        ("short",): "Finish Before Bedtime Tonight",
        ("award",): "Critically Loved, Criminally Underread",
    }
    ```
  - `generate_title(cluster_properties, context)` → catchy string
  - Fallback titles for unknown cluster types

- [ ] **T17.5** Create `ml/collection_engine.py` (2h)
  - `CollectionEngine` class
  - `fit(books, comics)` — cluster all content
  - `generate_collections(user_id=None)` → list of Collection objects
    ```python
    Collection(
        name="epic_fantasy_cluster_3",
        title="Epic Worlds Built From Scratch",
        description="...",
        items=[book_id_1, book_id_2, ...],
        collection_type="mood",
        mood="epic",
    )
    ```
  - `get_free_reading_collection()` → Internet Archive items
  - `get_trending_collection()` → recent high-activity items
  - `rotate_collections()` — ensures freshness, avoid staleness
  - Results cached in Redis (TTL 6h)

- [ ] **T17.6** Write tests (1h)
  - `tests/test_collection_engine.py`
  - Test cluster generation
  - Test title templates
  - Test mood detection accuracy
  - Test free reading collection

- [ ] **T17.7** Commit + update notes (30min)
  ```
  git commit -m "feat(ml): collection engine with KMeans + mood detection + title templates"
  ```

**✅ Success Criteria:**
- [ ] At least 8 distinct collections generated
- [ ] Each collection has unique catchy title
- [ ] Mood detection feels accurate on test descriptions
- [ ] Free reading collection populated from Internet Archive
- [ ] Silhouette score > 0.35
- [ ] All tests passing

**Files to create:**
```
backend/
  notebooks/
    02_collection_engine.ipynb
  src/
    ml/
      mood_detector.py
      title_templates.py
      collection_engine.py
  tests/
    test_collection_engine.py
```

---

### 📅 Day 18: Series Intelligence (Reading Order Guide)

**🎯 Goal:** Build the series detection and reading order system. For any book or comic series, Kitabee shows the correct reading order with labels.

**⏱️ Estimated Time:** 5-6 hours

**📋 Tasks:**

- [ ] **T18.1** Study series metadata patterns (30min)
  - Google Books `seriesInfo` field
  - Comic Vine volume + issue structure
  - Common patterns in descriptions ("Book 2 of...", "sequel to...")

- [ ] **T18.2** Create notebook `notebooks/03_series_intelligence.ipynb` (1h)
  - Load 10 known series (Dune, Harry Potter, Batman: Year One run)
  - Extract series info from metadata
  - Test NLP pattern matching on descriptions
  - Manually verify ordering

- [ ] **T18.3** Create `ml/series_detector.py` (1.5h)
  - `detect_series(book_metadata)` → SeriesInfo or None
  - Regex patterns for common series indicators:
    ```python
    PATTERNS = [
        r"book (\d+) of",
        r"volume (\d+)",
        r"part (\d+) of",
        r"#(\d+) in the",
        r"sequel to",
        r"prequel to",
        r"companion to",
    ]
    ```
  - `classify_entry_type(book, series)` → "main" | "prequel" | "spinoff" | "companion"
  - `extract_volume_number(metadata)` → int or None

- [ ] **T18.4** Create `ml/series_builder.py` (2h)
  - `SeriesBuilder` class
  - `build_series_order(series_name, content_type)` → OrderedSeries
    ```python
    OrderedSeries(
        series_name="Dune",
        content_type="book",
        main_series=[
            SeriesEntry(book_id=..., title="Dune", order=1, label="Start Here"),
            SeriesEntry(book_id=..., title="Dune Messiah", order=2, label=None),
            ...
        ],
        companion_series=[
            CompanionSeries(
                name="Prequel Series by Brian Herbert",
                entries=[...],
                tip="Read after Book 1 or after completing all 6 originals."
            )
        ],
        tip="Books 1-3 are the core trilogy. Books 4-6 are for dedicated fans.",
    )
    ```
  - `get_start_here(series)` → first entry with "Start Here" label
  - `get_series_for_book(book_id)` → finds which series this book belongs to
  - Cache series data in Redis (TTL 7 days — series order rarely changes)

- [ ] **T18.5** Create series API route (1h)
  - Add to `api/routes/books.py`:
    - `GET /api/v1/books/{book_id}/series` → OrderedSeries or 404
  - Add to future comics route:
    - `GET /api/v1/comics/{comic_id}/series` → OrderedSeries or 404

- [ ] **T18.6** Write tests (1h)
  - `tests/test_series_intelligence.py`
  - Test series detection for known series
  - Test entry type classification
  - Test volume number extraction
  - Test API endpoint

- [ ] **T18.7** Commit + update notes (30min)
  ```
  git commit -m "feat(ml): series intelligence + reading order guide"
  ```

**✅ Success Criteria:**
- [ ] Correctly orders Dune, Harry Potter, Lord of the Rings
- [ ] Correctly orders Batman: Year One comic run
- [ ] "Start Here" label appears on first entry
- [ ] Prequel/spinoff classified correctly
- [ ] API endpoint returns clean JSON
- [ ] All tests passing

**Files to create:**
```
backend/
  notebooks/
    03_series_intelligence.ipynb
  src/
    ml/
      series_detector.py
      series_builder.py
  tests/
    test_series_intelligence.py
```

---

### 📅 Day 19: KNN Collaborative Filtering + Personalizer

**🎯 Goal:** Build user-based collaborative filtering so collections are personalized per user. "Because you loved X..." rows become possible.

**⏱️ Estimated Time:** 5-6 hours

**📋 Tasks:**

- [ ] **T19.1** Study collaborative filtering (1h)
  - User-item matrix
  - KNN with cosine similarity
  - Cold start handling
  - Why it complements content-based

- [ ] **T19.2** Create notebook `notebooks/04_collaborative.ipynb` (1h)
  - Build user-item ratings matrix from DB
  - Fit KNN model
  - Find similar users
  - Recommend based on what similar users liked

- [ ] **T19.3** Create `ml/collaborative.py` (2h)
  - `CollaborativeRecommender` class
  - `fit(ratings_df)` — build user-item matrix + fit KNN
  - `find_similar_users(user_id, k=20)` → list of similar user_ids
  - `recommend_for_user(user_id, top_n=20)` → list of book/comic ids
  - `get_because_you_loved_row(user_id)` → collection row based on top-rated item
  - Cold start: return None if user has < 5 ratings (fallback to mood rows)

- [ ] **T19.4** Create `ml/personalizer.py` (1.5h)
  - `Personalizer` class
  - `rank_collections_for_user(user_id, collections)` → sorted collections
  - `inject_personalized_rows(user_id, collections)` → adds "Because you loved X" row
  - `filter_by_content_preference(user_id, collections)` → respects books/comics/both preference
  - Reads user preferences from DB

- [ ] **T19.5** Write tests (1h)
  - `tests/test_collaborative.py`
  - `tests/test_personalizer.py`
  - Test with mock ratings data
  - Test cold start handling
  - Test content preference filtering

- [ ] **T19.6** Commit + update notes (30min)
  ```
  git commit -m "feat(ml): KNN collaborative filtering + personalizer"
  ```

**✅ Success Criteria:**
- [ ] Finds similar users correctly
- [ ] "Because you loved X" row generates correctly
- [ ] Cold start handled gracefully (no crash, fallback works)
- [ ] Content preference filter works (books-only user sees no comics)
- [ ] All tests passing

**Files to create:**
```
backend/
  notebooks/
    04_collaborative.ipynb
  src/
    ml/
      collaborative.py
      personalizer.py
  tests/
    test_collaborative.py
    test_personalizer.py
```

---

### 📅 Day 20: Neural Recommender + Hybrid Collection API

**🎯 Goal:** Add deep learning layer and wire everything into a single `/api/v1/collections` endpoint that serves the Netflix-style home screen.

**⏱️ Estimated Time:** 6-7 hours

**📋 Tasks:**

- [ ] **T20.1** Create notebook `notebooks/05_neural.ipynb` (1.5h)
  - User embedding + content embedding architecture
  - Training on ratings data
  - Evaluate RMSE

- [ ] **T20.2** Create `ml/neural.py` (2h)
  - `NeuralRecommender` class
  - `build_model(num_users, num_items)` — Keras model
  - `fit(ratings_df)` — train
  - `predict(user_id, item_ids)` → scored list
  - `save_model()` / `load_model()`
  - Graceful fallback if not enough data to train

- [ ] **T20.3** Create `ml/hybrid.py` (1h)
  - `HybridEngine` class
  - Combines: Content-based (30%) + Collaborative (30%) + Neural (40%)
  - Diversity filter: max 3 items per genre in one collection row
  - `score_items_for_user(user_id, candidate_items)` → ranked list
  - `explain(user_id, item_id)` → "Because you loved X" or "Similar to books you rated 5 stars"

- [ ] **T20.4** Create `services/collection_service.py` (1h)
  - `get_home_collections(user_id)` → list of Collection objects
  - Orchestrates: CollectionEngine → Personalizer → HybridEngine
  - Assembles minimum 6 collection rows:
    1. "Because you loved [X]..." (personalized)
    2. Mood-based row (e.g. "Epic Worlds Built From Scratch")
    3. "Free to Read Right Now" (Internet Archive)
    4. "Complete Series — Start to Finish"
    5. "Everyone Is Reading This" (trending)
    6. "Comics — Perfect Starting Points" (or books equivalent)
    7. Additional mood/genre rows based on user taste
  - Caches result in Redis (TTL 6h)
  - Invalidates cache on new rating

- [ ] **T20.5** Create collections API route (1h)
  - `api/routes/collections.py`
  - `GET /api/v1/collections` → home screen collections (auth required)
  - `GET /api/v1/collections/{collection_name}` → full collection (paginated)
  - `GET /api/v1/books/{book_id}/similar` → updated to use HybridEngine
  - Register in `main.py`

- [ ] **T20.6** Write tests (1h)
  - `tests/test_collection_service.py`
  - `tests/test_collections_api.py`
  - Test minimum 6 rows returned
  - Test each row has title + items
  - Test cache invalidation on new rating
  - Test unauthenticated request → 403

- [ ] **T20.7** Commit + update notes (30min)
  ```
  git commit -m "feat(ml): neural recommender + hybrid engine + collections API"
  ```

**✅ Success Criteria:**
- [ ] `GET /api/v1/collections` returns 6+ themed rows
- [ ] Each row has catchy title + 8-12 items
- [ ] "Because you loved X" row personalizes correctly
- [ ] "Free to Read Right Now" row contains Internet Archive items
- [ ] Response time < 300ms (cached)
- [ ] RMSE < 0.9 on neural model
- [ ] All tests passing

**Files to create:**
```
backend/
  notebooks/
    05_neural.ipynb
  src/
    ml/
      neural.py
      hybrid.py
    services/
      collection_service.py
    api/
      routes/
        collections.py
  tests/
    test_collection_service.py
    test_collections_api.py
```

---

### 📅 Day 21: ML Testing + Evaluation + Week 3 Review

**🎯 Goal:** Validate all ML models, measure quality, document the ML strategy, prepare for frontend week.

**⏱️ Estimated Time:** 4-5 hours

**📋 Tasks:**

- [ ] **T21.1** Create evaluation script `notebooks/06_evaluation.ipynb` (2h)
  - Precision@10 for content-based
  - Recall@10 for collaborative
  - RMSE for neural
  - Silhouette score for collection clusters
  - Manual inspection of 20 collection rows
  - Manual inspection of 5 series order outputs

- [ ] **T21.2** Fix any quality issues found (1h)
  - Tune KMeans K if clusters feel wrong
  - Expand mood word lists if detection feels off
  - Fix any series ordering errors

- [ ] **T21.3** Create `docs/ML_STRATEGY.md` (1h)
  - Document each ML module
  - Show metrics achieved
  - Explain collection title system
  - Include sample collection output
  - This becomes a key portfolio document

- [ ] **T21.4** Update TRACKER.md + LEARNING_NOTES.md (30min)

- [ ] **T21.5** Week 3 reflection + commit (30min)
  ```
  git commit -m "chore(tracker): mark Week 3 complete, ML engine ready"
  ```

**✅ Success Criteria:**
- [ ] All ML metric targets met (see PRD Success Metrics)
- [ ] At least 10 distinct collection types working
- [ ] Series order correct for 5 manually tested series
- [ ] ML_STRATEGY.md written and committed
- [ ] Zero regressions on existing 351 tests
- [ ] Ready for frontend week

---

## 📱 Week 4: Mobile App Development

### 🎯 Week Goal
By end of Week 4, full mobile app works on phone via Expo Go including:
- Netflix-style home screen with collection rows
- Unified books + comics search
- Book/comic detail with series order
- In-app free reading (EPUB + comics)
- Personal library

### 📚 Skills You Will Learn
- React Native + Expo
- TypeScript in mobile
- React Navigation
- Zustand state management
- API integration (Axios)
- EPUB reader (WebView-based)
- Responsive design for mobile

---

### 📅 Day 22: Expo Project + Navigation Setup

**🎯 Goal:** App skeleton with all screens wired up and navigation working.

**⏱️ Estimated Time:** 5-6 hours

**📋 Tasks:**

- [ ] **T22.1** Verify Expo setup from Day 1 (15min)
- [ ] **T22.2** Install dependencies (30min)
  ```bash
  npm install @react-navigation/native @react-navigation/bottom-tabs @react-navigation/stack
  npm install zustand axios @react-native-async-storage/async-storage
  npm install react-native-webview
  ```
- [ ] **T22.3** Create folder structure (30min)
  ```
  src/
    screens/
    components/
    services/
    stores/
    theme/
    navigation/
  ```
- [ ] **T22.4** Setup theme system (1h)
  - `theme/colors.ts` — Kitabee brand colors
  - `theme/typography.ts` — Poppins + Inter
  - `context/ThemeContext.tsx` — dark/light toggle

- [ ] **T22.5** Setup navigation (2h)
  - Auth Stack (Welcome, Login, Register)
  - Onboarding Stack (ContentChoice, RateBooks, GenreSelect)
  - Main Tabs (Home, Search, Library, Profile)
  - Root navigator with auth check

- [ ] **T22.6** Create placeholder screens (1h)
  - All screens — just title text for now
  - Verify navigation between all of them

- [ ] **T22.7** Test on phone + commit (30min)

**✅ Success Criteria:**
- [ ] App runs on phone via Expo Go
- [ ] All screens reachable via navigation
- [ ] Theme applies consistently
- [ ] Bottom tabs work

---

### 📅 Day 23: Auth Screens (Login, Register, Onboarding)

**🎯 Goal:** Complete auth flow including content type preference onboarding (books/comics/both).

**⏱️ Estimated Time:** 5-6 hours

**📋 Tasks:**

- [ ] **T23.1** Setup Axios client (`services/api.ts`) (1h)
  - Base URL from env
  - Auth token interceptor
  - Error handling

- [ ] **T23.2** Setup Zustand user store (45min)
- [ ] **T23.3** Setup AsyncStorage for tokens (30min)
- [ ] **T23.4** Build WelcomeScreen (30min)
- [ ] **T23.5** Build LoginScreen (1h)
- [ ] **T23.6** Build RegisterScreen (1h)
- [ ] **T23.7** Build Onboarding flow (1h)
  - Screen 1: "What do you love?" — Books / Comics / Both selector
  - Screen 2: Rate 5 popular items (based on choice above)
  - Screen 3: Pick 3 favorite genres
  - Calls `POST /api/v1/users/me/preferences/complete`

- [ ] **T23.8** Test full auth + onboarding on phone + commit (30min)

**✅ Success Criteria:**
- [ ] Can register on phone
- [ ] Can login on phone
- [ ] Onboarding captures books/comics/both preference
- [ ] Token persists across app restarts
- [ ] Redirects to home after onboarding

---

### 📅 Day 24: Netflix-Style Home Screen (Collection Rows)

**🎯 Goal:** The flagship screen. Horizontally scrollable themed collection rows, exactly like Netflix.

**⏱️ Estimated Time:** 6-7 hours

**📋 Tasks:**

- [ ] **T24.1** Create `ContentCard` component (1h)
  - Works for both books and comics
  - Shows cover, title, free badge (if applicable)
  - Tap navigates to detail page

- [ ] **T24.2** Create `CollectionRow` component (1.5h)
  - Catchy title (large, bold)
  - Horizontal FlatList of ContentCards
  - "See all" button → taps to full collection screen
  - Loading skeleton state

- [ ] **T24.3** Build `HomeScreen` (2.5h)
  - Fetch `GET /api/v1/collections`
  - Render collection rows from API response
  - "Continue Reading" row at top (if reading progress exists)
  - Pull-to-refresh
  - Loading + error states
  - Empty state for new users (show popular rows)

- [ ] **T24.4** Build `FullCollectionScreen` (1h)
  - Tapping "See all" on any row
  - Grid view of all items in that collection
  - Collection title + description at top

- [ ] **T24.5** Test on phone + commit (30min)

**✅ Success Criteria:**
- [ ] Home screen shows minimum 6 collection rows
- [ ] Each row scrolls horizontally
- [ ] Catchy titles visible and readable
- [ ] Feels like Netflix — engaging and familiar
- [ ] Pull-to-refresh works
- [ ] Free reading badge visible on eligible items

---

### 📅 Day 25: Search Screen (Books + Comics Unified)

**🎯 Goal:** Search that returns both books and comics, clearly distinguished.

**⏱️ Estimated Time:** 5-6 hours

**📋 Tasks:**

- [ ] **T25.1** Build `SearchScreen` (2.5h)
  - Search input with debouncing (300ms)
  - Content type filter tabs: All / Books / Comics
  - Results list with ContentCard
  - "Free" badge on Internet Archive items
  - Empty state (show trending or popular)
  - Loading state

- [ ] **T25.2** Build `SearchResultCard` component (1h)
  - Slightly larger than home screen card
  - Shows content type label (Book / Comic)
  - Shows free badge
  - Shows series name if applicable ("Book 1 of Dune")

- [ ] **T25.3** Wire search to backend (1h)
  - `GET /api/v1/books/search?q=...` for books
  - `GET /api/v1/comics/search?q=...` for comics (new endpoint)
  - Merge and sort results

- [ ] **T25.4** Test on phone + commit (30min)

**✅ Success Criteria:**
- [ ] Search returns both books and comics
- [ ] Content type filter works
- [ ] Debouncing prevents excessive API calls
- [ ] Free badge visible
- [ ] Series info shown in results

---

### 📅 Day 26: Book/Comic Detail Page + Series Order UI

**🎯 Goal:** Rich detail page with series order section — the key differentiating screen.

**⏱️ Estimated Time:** 5-6 hours

**📋 Tasks:**

- [ ] **T26.1** Build `DetailScreen` (works for both books and comics) (3h)
  - Large cover image
  - Title, author/creator, publisher, year
  - Content type badge (Book / Comic)
  - Description with "Show more" expand
  - Rating bar + "Rate this" button
  - Add to Library button
  - Free Read button (if available via Internet Archive)
  - "Why we recommend this" chip (from hybrid explainer)

- [ ] **T26.2** Build `SeriesOrderSection` component (1.5h)
  - Appears on detail screen if book/comic is part of series
  - Shows full series in order
  - "Start Here" badge on first entry
  - "Prequel", "Spin-off" badges where applicable
  - Tip text shown below list
  - Tap any series entry → navigate to its detail page

- [ ] **T26.3** Build `RatingModal` (1h)
  - Star selector (1-5)
  - Optional review text input
  - Submit button
  - Calls `POST /api/v1/books/{book_id}/ratings`

- [ ] **T26.4** Test on phone + commit (30min)

**✅ Success Criteria:**
- [ ] Detail page loads for any book or comic
- [ ] Series order section appears and is accurate
- [ ] "Start Here" label visible
- [ ] Free Read button visible when available
- [ ] Rating modal works end-to-end

---

### 📅 Day 27: Library Screen + Free Reading (EPUB + Comics Reader)

**🎯 Goal:** User library management + in-app reading for public domain content.

**⏱️ Estimated Time:** 6-7 hours

**📋 Tasks:**

- [ ] **T27.1** Build `LibraryScreen` (2h)
  - Three tabs: Want to Read / Currently Reading / Read
  - Toggle: Books / Comics / All
  - Grid of ContentCards
  - Swipe actions: move status, remove
  - Empty state per tab

- [ ] **T27.2** Build `EPUBReaderScreen` (2h)
  - WebView-based reader
  - Loads EPUB URL from Internet Archive
  - Reading progress bar at top
  - Tap edges to turn pages
  - Save progress on exit → calls `PATCH /api/v1/reading-progress`
  - Back button with progress confirmation

- [ ] **T27.3** Build `ComicsReaderScreen` (2h)
  - Image-based reader (one page at a time)
  - Loads image URLs from Internet Archive
  - Swipe left/right to turn pages
  - Pinch to zoom
  - Page number indicator
  - Save progress on exit

- [ ] **T27.4** Test reading on phone + commit (30min)

**✅ Success Criteria:**
- [ ] Library shows items in correct tabs
- [ ] EPUB reader opens and loads content
- [ ] Comics reader shows pages cleanly on mobile
- [ ] Reading progress saves and resumes correctly
- [ ] "Continue Reading" shows on home screen after starting

---

### 📅 Day 28: Profile + Insights + Cross-Platform Testing

**🎯 Goal:** Complete remaining screens and ensure everything works on web and mobile.

**⏱️ Estimated Time:** 5-6 hours

**📋 Tasks:**

- [ ] **T28.1** Build `ProfileScreen` (1h)
  - Avatar, name, bio
  - Stats: books read, comics read, ratings given
  - Edit profile button

- [ ] **T28.2** Build `InsightsScreen` (1.5h)
  - Reading DNA card (AI-generated personality)
  - Genre pie chart (books + comics breakdown)
  - Top authors/creators list
  - Books vs comics ratio

- [ ] **T28.3** Build `SettingsScreen` (45min)
  - Dark/light mode toggle
  - Content preference (books/comics/both)
  - Logout

- [ ] **T28.4** Cross-platform testing (2h)
  - Test on web (`npx expo start --web`)
  - Test on Android (Expo Go)
  - Fix responsive issues
  - Fix platform-specific crashes

- [ ] **T28.5** Commit + week 4 reflection (30min)

**✅ Success Criteria:**
- [ ] All screens complete and navigable
- [ ] Works on web without errors
- [ ] Works on Android via Expo Go
- [ ] UI adapts to screen sizes
- [ ] No platform-specific crashes

---

## 🚀 Week 5: Deployment & Polish

### 🎯 Week Goal
Kitabee is LIVE and shareable with recruiters. Both web and mobile accessible publicly.

### 📚 Skills You Will Learn
- Docker + Docker Compose
- AWS EC2 setup
- Nginx reverse proxy
- SSL certificates (Let's Encrypt)
- Vercel deployment
- CI/CD (GitHub Actions)

---

### 📅 Day 29: Dockerize Backend

**🎯 Goal:** Backend runs in production Docker container.

**⏱️ Estimated Time:** 4-5 hours

**📋 Tasks:**

- [ ] **T29.1** Update backend `Dockerfile` (already exists, verify prod-ready) (1h)
- [ ] **T29.2** Create production `docker-compose.prod.yml` (1h)
  - backend + postgres + redis services
  - Volume mounts for data persistence
  - Environment variable injection
- [ ] **T29.3** Add ML model volume mount (30min)
  - Trained models persist between container restarts
- [ ] **T29.4** Test locally (1.5h)
  ```powershell
  docker compose -f docker-compose.prod.yml up --build
  ```
- [ ] **T29.5** Fix issues + commit (1h)

**✅ Success Criteria:**
- [ ] Container builds without errors
- [ ] All services start correctly
- [ ] API accessible on localhost:8000
- [ ] ML models load correctly inside container

---

### 📅 Day 30: AWS EC2 Setup

**🎯 Goal:** Provision AWS instance and prepare it for deployment.

**⏱️ Estimated Time:** 4-5 hours

**📋 Tasks:**

- [ ] **T30.1** Create AWS account + free tier setup (30min)
- [ ] **T30.2** Launch EC2 t3.medium Ubuntu 22.04 (30min)
  - Security groups: ports 22, 80, 443
  - Download key pair
- [ ] **T30.3** SSH into instance (30min)
- [ ] **T30.4** Install Docker + Docker Compose (1h)
- [ ] **T30.5** Setup UFW firewall (30min)
- [ ] **T30.6** Clone repo + configure .env (1h)
- [ ] **T30.7** Smoke test deployment (1h)

**✅ Success Criteria:**
- [ ] Can SSH into EC2
- [ ] Docker installed and running
- [ ] Repo cloned with correct .env
- [ ] API responds on port 8000

---

### 📅 Day 31: Deploy Backend + Nginx + SSL

**🎯 Goal:** Backend publicly accessible over HTTPS.

**⏱️ Estimated Time:** 4-5 hours

**📋 Tasks:**

- [ ] **T31.1** Start Docker stack on EC2 (30min)
- [ ] **T31.2** Configure Nginx as reverse proxy (2h)
- [ ] **T31.3** Setup Let's Encrypt SSL via Certbot (1.5h)
- [ ] **T31.4** Test HTTPS endpoint (30min)
- [ ] **T31.5** Setup domain (optional, ~₹800) (30min)

**✅ Success Criteria:**
- [ ] `https://your-domain.com/docs` works
- [ ] SSL certificate valid
- [ ] All API endpoints accessible
- [ ] Collections endpoint returns data

---

### 📅 Day 32: Deploy Web + Publish Expo

**🎯 Goal:** Web version live on Vercel + mobile accessible via Expo Go QR code.

**⏱️ Estimated Time:** 3-4 hours

**📋 Tasks:**

- [ ] **T32.1** Update mobile API base URL to production (15min)
- [ ] **T32.2** Export web build (30min)
  ```bash
  npx expo export -p web
  ```
- [ ] **T32.3** Deploy to Vercel (30min)
- [ ] **T32.4** Publish Expo update (30min)
  ```bash
  eas update --branch production
  ```
- [ ] **T32.5** Test both platforms end-to-end (1.5h)
  - Collections load on home screen
  - Search works
  - Free reading works
- [ ] **T32.6** Generate QR code for README (30min)

**✅ Success Criteria:**
- [ ] Web app live on Vercel URL
- [ ] Mobile app updates via Expo Go
- [ ] Netflix-style home screen loads on phone
- [ ] Free reading opens in app on phone

---

### 📅 Day 33: CI/CD (GitHub Actions)

**🎯 Goal:** Auto-test and auto-deploy on every git push.

**⏱️ Estimated Time:** 3-4 hours

**📋 Tasks:**

- [ ] **T33.1** Setup backend test workflow (1.5h)
  - Runs pytest on every push
  - Coverage report as comment
- [ ] **T33.2** Setup backend deploy workflow (1.5h)
  - Deploys to EC2 on merge to main
- [ ] **T33.3** Add secrets to GitHub repository (30min)
- [ ] **T33.4** Test pipeline end-to-end (1h)

**✅ Success Criteria:**
- [ ] Tests run automatically on push
- [ ] Auto-deploy on main branch merge
- [ ] Badge shows passing in README

---

### 📅 Day 34: Demo Video + README + Blog Post

**🎯 Goal:** Portfolio-ready presentation materials.

**⏱️ Estimated Time:** 4-5 hours

**📋 Tasks:**

- [ ] **T34.1** Record 2-min demo video (1.5h)
  - Show: Netflix-style home screen scrolling
  - Show: Series order guide in action
  - Show: Free reading opening in-app
  - Show: Comics + books unified search
  - Record on both web and mobile

- [ ] **T34.2** Rewrite README (2h)
  - Hero GIF showing Netflix-style home screen
  - Feature highlights with screenshots
  - Tech stack badges
  - ML architecture diagram
  - Live URLs + Expo Go QR code
  - Setup instructions

- [ ] **T34.3** Write blog post (1.5h)
  - "How I Built a Netflix-Style Book + Comics Discovery App in 5 Weeks"
  - Publish on Medium or Dev.to

**✅ Success Criteria:**
- [ ] Demo video uploaded and linked in README
- [ ] README looks professional with screenshots
- [ ] Blog published and linked

---

### 📅 Day 35: Launch! 🚀

**🎯 Goal:** Share with the world.

**⏱️ Estimated Time:** 3-4 hours

**📋 Tasks:**

- [ ] **T35.1** Final QA pass — test every feature (1h)
- [ ] **T35.2** LinkedIn post with demo video (30min)
- [ ] **T35.3** Twitter/X announcement (30min)
- [ ] **T35.4** Share on Reddit: r/reactnative, r/Python, r/MachineLearning (30min)
- [ ] **T35.5** Update resume + LinkedIn profile (30min)
- [ ] **T35.6** Celebrate 🎉

**✅ Success Criteria:**
- [ ] Everything works publicly
- [ ] Portfolio updated
- [ ] Shared on at least 2 platforms
- [ ] First external user (even a friend)

---

## 🔄 Daily Workflow

### Morning Ritual (30 min)
```
1. ☕ Coffee/tea
2. 📖 Review yesterday's LEARNING_NOTES
3. 📋 Open today's task list
4. 🎯 Identify any blockers
5. 🚀 Start with easiest task for momentum
```

### Evening Ritual (30 min)
```
1. ✅ Update task checkboxes
2. 💾 Commit + push
3. 📝 Update LEARNING_NOTES
4. 📅 Preview tomorrow's tasks
5. 🎉 Celebrate wins
```

---

## 🔗 Dependency Graph

```
Week 1 (Backend Foundation) ✅
├── Day 2: Database
├── Day 3: Google Books
├── Day 4: Redis
├── Day 5: Search
├── Day 6: Details
└── Day 7: Review
     ↓
Week 2 (Auth + Users) ✅
├── Day 8: JWT
├── Day 9: Register/Login
├── Day 10: Profile
├── Day 11: Ratings ──────────────┐ Ratings data needed for ML
├── Day 12: Library               │
├── Day 13: Preferences           │
└── Day 14: Testing ──────────────┘
     ↓
Week 3 (ML + Comics + Collections)
├── Day 15: TF-IDF Vectorizer ────┐
├── Day 16: Comic Vine + IA API   │ All feed into
├── Day 17: Collection Engine ────┤ Day 20 (Hybrid API)
├── Day 18: Series Intelligence   │
├── Day 19: Collaborative + ──────┤
│           Personalizer          │
├── Day 20: Neural + Hybrid API ──┘
└── Day 21: Evaluation + Docs
     ↓
Week 4 (Frontend)
├── Day 22: Setup + Navigation
├── Day 23: Auth + Onboarding
├── Day 24: Netflix Home Screen ──── Needs Day 20 (collections API)
├── Day 25: Search (books+comics) ── Needs Day 16 (Comic Vine)
├── Day 26: Detail + Series UI ───── Needs Day 18 (Series Intelligence)
├── Day 27: Library + Free Reading ─ Needs Day 16 (Internet Archive)
└── Day 28: Profile + Insights + Testing
     ↓
Week 5 (Deploy)
├── Day 29: Dockerize
├── Day 30: AWS Setup
├── Day 31: Deploy Backend
├── Day 32: Deploy Frontend
├── Day 33: CI/CD
├── Day 34: Demo + README + Blog
└── Day 35: Launch 🚀
```

---

## ⏱️ Time Estimates

### Per Week Breakdown

| Week | Coding | Learning | Testing | Docs | Total |
|------|--------|----------|---------|------|-------|
| **Week 1** ✅ | 15h | 6h | 5h | 4h | 30h |
| **Week 2** ✅ | 18h | 4h | 5h | 3h | 30h |
| **Week 3** | 22h | 6h | 3h | 3h | 34h |
| **Week 4** | 24h | 3h | 4h | 2h | 33h |
| **Week 5** | 12h | 4h | 4h | 8h | 28h |
| **Total** | **91h** | **23h** | **21h** | **20h** | **155h** |

### Reality Check
- 155 hours over 5 weeks = ~31 hours/week = ~4-5 hours/day
- Add 20% buffer for unknowns = 186 hours
- If falling behind: cut P2 features aggressively

---

## ⚠️ Risk Register

| # | Risk | Impact | Likelihood | Mitigation |
|---|------|--------|------------|------------|
| 1 | **External API rate limits** | High | Medium | Aggressive Redis caching, fallback sources |
| 2 | **Comic Vine API rate limit (200/hr)** | Medium | Medium | Cache aggressively (TTL 24h), batch requests |
| 3 | **Internet Archive slow response** | Medium | Medium | Cache links (TTL 24h), timeout + graceful fallback |
| 4 | **ML collections feel generic** | High | Medium | Tune clustering K, expand mood word lists, user feedback |
| 5 | **Series order data incomplete** | Medium | Medium | Manual curation for top 50 series, tip for complex universes |
| 6 | **EPUB reader WebView complexity** | Medium | Medium | Use proven react-native-webview, test early on real device |
| 7 | **Comics image reader performance** | Medium | Medium | Lazy load images, pre-load next page |
| 8 | **Neural model needs enough data** | High | High | Fallback to content-based if < 100 ratings in DB |
| 9 | **Cold start for comics users** | Medium | High | Mood + popular rows work without personalization |
| 10 | **AWS free tier exceeded** | Medium | Low | Set billing alerts, monitor storage (ML models are large) |
| 11 | **Timeline slip on ML week** | High | Medium | Ship with 3 modules minimum (Vectorizer + Collection Engine + Series) |
| 12 | **Burnout mid-project** | High | Medium | Take breaks, celebrate wins daily |

### Emergency Contingencies

**If Week 3 slips:**
- Ship with Vectorizer + Collection Engine only (skip Neural)
- Series Intelligence is P1 — keep it
- Collaborative filtering is P1 — keep it
- Neural is P2 — defer to post-MVP

**If Week 4 slips:**
- Cut Insights screen (P1 → Phase 2)
- Cut Comics Reader (ship EPUB only)
- Simplify Library (single status view)

**If Week 5 slips:**
- Deploy backend only, use ngrok for demo
- Skip CI/CD (manual deploy for now)

---

## ✅ Definition of Done

A task is **DONE** when:
- ✅ Code written and works locally
- ✅ Manual testing passed
- ✅ Unit tests written for new logic
- ✅ No linter or type errors
- ✅ Committed to Git with meaningful message
- ✅ Pushed to GitHub
- ✅ LEARNING_NOTES.md updated
- ✅ Docstrings added

A feature is **DONE** when:
- ✅ All related tasks DONE
- ✅ Integration tested
- ✅ Works on web and mobile
- ✅ Handles errors gracefully
- ✅ Performance meets SLA
- ✅ Screenshot captured for demo

---

## 🎯 Buffer & Contingencies

### Weekly Buffer Days
- **Day 7:** Week 1 buffer ✅
- **Day 14:** Week 2 buffer ✅
- **Day 21:** Week 3 buffer — ML evaluation + docs
- **Day 28:** Week 4 buffer — cross-platform testing
- **Days 34-35:** Week 5 buffer — polish + launch

### If You Fall Behind
- 1-2 days: Work weekends harder, catch up on buffer day
- 3-5 days: Cut a P2 feature (Insights, dark mode, comics reader)
- 5+ days: Extend timeline by 1 week, reassess scope

---

## 📚 Learning Time Allocation

| Topic | Hours | Priority |
|-------|-------|----------|
| **TF-IDF + cosine similarity** | 3h | 🔴 Critical |
| **KMeans clustering** | 2h | 🔴 Critical |
| **KNN collaborative filtering** | 2h | 🔴 Critical |
| **Neural CF (Keras)** | 4h | 🟡 High |
| **NLP mood detection (NLTK)** | 2h | 🟡 High |
| **Comic Vine API** | 1h | 🟡 High |
| **Internet Archive API** | 1h | 🟡 High |
| **React Native basics** | 4h | 🔴 Critical |
| **react-native-webview (EPUB)** | 2h | 🟡 High |
| **Docker + AWS EC2** | 5h | 🟡 High |
| **Nginx + SSL** | 2h | 🟢 Medium |
| **GitHub Actions** | 2h | 🟢 Medium |

---

## 📈 Communication & Progress Tracking

### Daily Progress Log (in LEARNING_NOTES.md)

```markdown
## Day X: [Date]

### Done Today
- [x] T15.1: Studied TF-IDF theory
- [x] T15.2: Created vectorizer notebook
- [ ] T15.3: ml/vectorizer.py (in progress)

### Time Spent
- Learning: 1h
- Coding: 3h
- Debugging: 1h
- Total: 5h

### Wins 🎉
- First collection row generated with catchy title!

### Challenges 😅
- KMeans choosing right K was tricky

### Tomorrow
- Complete T15.3
- Start Day 16 (Comic Vine API)
```

---

## 🎊 Post-Launch Checklist

### Portfolio Updates
- [ ] Add to resume (top position)
- [ ] Add to LinkedIn Featured section
- [ ] Update GitHub pinned repos
- [ ] Add to portfolio website

### Community Sharing
- [ ] LinkedIn post with demo video
- [ ] Tweet: #ReactNative #Python #MachineLearning #ComicBooks
- [ ] Reddit: r/reactnative, r/Python, r/comicbooks, r/MachineLearning
- [ ] Show HN submission
- [ ] Product Hunt (optional)

### Interview Prep
- [ ] Practice 2-min demo showing Netflix home + series order + free reading
- [ ] Prepare answers: "How does the collection engine work?"
- [ ] Prepare answers: "How do you handle cold start?"
- [ ] Prepare answers: "Why books AND comics?"
- [ ] Rehearse "walk me through your project" pitch

### Maintenance
- [ ] Monitor errors weekly
- [ ] Respond to user feedback
- [ ] Fix critical bugs immediately
- [ ] Plan Phase 2 (social features, affiliate links, more APIs)

---

## 📎 Appendix

### Task ID Convention
Format: `T<day>.<sequence>`
Examples: T15.3 = Day 15 Task 3, T20.5 = Day 20 Task 5

### New APIs Added in v2.0
- **Comic Vine API** — comicvine.gamespot.com/api (free key required)
- **Internet Archive API** — archive.org/developers (no key required)
- **NYT Books API** — developer.nytimes.com (free key required)

### New ML Modules Added in v2.0
- `ml/vectorizer.py` — TF-IDF foundation
- `ml/mood_detector.py` — NLP mood detection for collection titles
- `ml/title_templates.py` — Catchy collection name generator
- `ml/collection_engine.py` — KMeans + mood → Netflix-style rows
- `ml/series_detector.py` — Series membership detection
- `ml/series_builder.py` — Reading order generation
- `ml/collaborative.py` — KNN collaborative filtering
- `ml/personalizer.py` — Per-user collection ranking
- `ml/neural.py` — Keras deep recommender
- `ml/hybrid.py` — Weighted combination of all models

### Related Documents
- [PRD.md](./PRD.md)
- [TECHSPEC.md](./TECHSPEC.md)
- [APPFLOW.md](./APPFLOW.md)
- [SCHEMA.md](./SCHEMA.md)

### Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Original] | [Your Name] | Initial implementation plan |
| 2.0 | [Today] | [Your Name] | Added comics discovery, Internet Archive free reading, Netflix-style collection engine, series reading order guide, Comic Vine API, restructured Week 3 ML days, updated Week 4 frontend for new features, updated risk register |

---

**End of Implementation Plan** 📅

*"A goal without a plan is just a wish. A plan without action is just a document."*

**Days 1-14 done. Day 15 is next. Let's build.** 🚀

---
