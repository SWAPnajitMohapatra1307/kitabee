---

# 🔧 Kitabee — Technical Specification

> **Document Version:** 2.0
> **Last Updated:** [Today's Date]
> **Author:** [Your Name]
> **Status:** 🟢 Approved for Implementation
> **Related Docs:** [PRD.md](./PRD.md) | [SCHEMA.md](./SCHEMA.md) | [IMPLEMENTATIONPLAN.md](./IMPLEMENTATIONPLAN.md)

---

## 📚 Table of Contents

1. [Overview](#-overview)
2. [System Architecture](#-system-architecture)
3. [Technology Stack](#-technology-stack)
4. [Frontend Specification](#-frontend-specification)
5. [Backend Specification](#-backend-specification)
6. [Data Layer](#-data-layer)
7. [AI/ML Specification](#-aiml-specification)
8. [External API Integrations](#-external-api-integrations)
9. [Authentication & Security](#-authentication--security)
10. [Caching Strategy](#-caching-strategy)
11. [Performance Requirements](#-performance-requirements)
12. [Failure Modes & Resilience](#-failure-modes--resilience)
13. [Deployment Architecture](#-deployment-architecture)
14. [CI/CD Pipeline](#-cicd-pipeline)
15. [Monitoring & Observability](#-monitoring--observability)
16. [Development Environment](#-development-environment)
17. [Testing Strategy](#-testing-strategy)
18. [Code Standards](#-code-standards)
19. [Dependency Management](#-dependency-management)
20. [Appendix](#-appendix)

---

## 🎯 Overview

### Purpose
This document specifies the complete technical implementation of Kitabee — an AI-powered books and comics discovery platform with Netflix-style themed collections, series reading order guidance, and free public domain reading.

### What Changed in v2.0
- Added **Comics** as first-class content type (Comic Vine API integration)
- Added **Internet Archive** integration for free public domain reading
- Restructured **ML Layer** into 5 focused modules (Vectorizer, Collection Engine, Series Intelligence, Personalizer, Neural)
- Added **Collections API** for Netflix-style home screen
- Added **Series Order API** for reading order guidance
- Added **Reading Progress API** for in-app reading tracking
- Added **EPUB reader + Comics reader** frontend screens
- Updated deployment for ML model volume persistence

### Scope
- ✅ MVP technical requirements (5-week timeline)
- ✅ Production deployment specifications
- ✅ Books + Comics unified architecture
- ✅ Free reading via Internet Archive

### Guiding Principles

1. **🎯 Pragmatism Over Perfection** — Ship in 5 weeks, iterate later
2. **📚 Learn by Building** — Choose tech that teaches valuable skills
3. **💰 Zero Budget** — Free tiers only
4. **🔒 Security First** — No shortcuts on auth or data protection
5. **⚡ Performance Matters** — p95 latency < 300ms for API calls
6. **📖 Documentation Driven** — Every decision documented
7. **🎬 UX Familiarity** — Netflix-style rows users already understand (New v2.0)
8. **⚖️ Legal Compliance** — Only public domain content for free reading (New v2.0)

---

## 🏗️ System Architecture

### High-Level Architecture Diagram (Updated v2.0)

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                            │
│                                                             │
│  ┌──────────────────┐        ┌──────────────────┐           │
│  │  Web Browser     │        │  Mobile Device   │           │
│  │  (Vercel CDN)    │        │  (Expo Go App)   │           │
│  │                  │        │                  │           │
│  │  React Native    │        │  React Native    │           │
│  │  Web Bundle      │        │  Bundle          │           │
│  │  + EPUB Reader   │        │  + EPUB Reader   │           │
│  │  + Comics Reader │        │  + Comics Reader │           │
│  └────────┬─────────┘        └────────┬─────────┘           │
└───────────┼──────────────────────────┼──────────────────────┘
            │                          │
            │  HTTPS/WSS               │  HTTPS
            └──────────────┬───────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    LOAD BALANCER                            │
│              (Nginx Reverse Proxy)                          │
│              Port 80/443 → Port 8000                        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                  APPLICATION LAYER                          │
│                  (AWS EC2 t3.medium)                        │
│                                                             │
│  ┌──────────────────────────────────────────────────┐       │
│  │       FastAPI Application (Uvicorn)              │       │
│  │                                                  │       │
│  │  ┌────────────────┐  ┌────────────────────┐      │       │
│  │  │ Auth Module    │  │ Books Module       │      │       │
│  │  │ (JWT)          │  │ (Search/Details)   │      │       │
│  │  └────────────────┘  └────────────────────┘      │       │
│  │                                                  │       │
│  │  ┌────────────────┐  ┌────────────────────┐      │       │
│  │  │ Comics Module  │  │ Collections Module │      │       │
│  │  │ 🆕 v2.0        │  │ 🆕 v2.0            │      │       │
│  │  │ (Search/Detail)│  │ (Netflix rows)     │      │       │
│  │  └────────────────┘  └────────────────────┘      │       │
│  │                                                  │       │
│  │  ┌────────────────┐  ┌────────────────────┐      │       │
│  │  │ Series Module  │  │ Reading Progress   │      │       │
│  │  │ 🆕 v2.0        │  │ 🆕 v2.0            │      │       │
│  │  │ (Order guide)  │  │ (Free reading)     │      │       │
│  │  └────────────────┘  └────────────────────┘      │       │
│  │                                                  │       │
│  │  ┌────────────────┐  ┌────────────────────┐      │       │
│  │  │ Ratings Module │  │ Library Module     │      │       │
│  │  │ (books+comics) │  │ (books+comics)     │      │       │
│  │  └────────────────┘  └────────────────────┘      │       │
│  │                                                  │       │
│  │  ┌────────────────┐  ┌────────────────────┐      │       │
│  │  │ Users Module   │  │ Preferences Module │      │       │
│  │  │ (Profile)      │  │ (books/comics/both)│      │       │
│  │  └────────────────┘  └────────────────────┘      │       │
│  └──────────────────────────────────────────────────┘       │
└──────┬─────────────────────────────────────┬────────────────┘
       │                                     │
       ▼                                     ▼
┌──────────────────┐              ┌──────────────────────────┐
│  DATA LAYER      │              │  ML LAYER (5 Modules)    │
│                  │              │                          │
│  ┌────────────┐  │              │  ┌───────────────────┐   │
│  │ PostgreSQL │  │              │  │ 1. Vectorizer     │   │
│  │ 14 tables  │  │              │  │    TF-IDF         │   │
│  │ (books+    │  │              │  │    (Foundation)   │   │
│  │  comics+   │  │              │  └───────────────────┘   │
│  │  collections│ │              │                          │
│  │  +series+  │  │              │  ┌───────────────────┐   │
│  │  reading)  │  │              │  │ 2. Collection     │   │
│  └────────────┘  │              │  │    Engine         │   │
│                  │              │  │    KMeans + Mood  │   │
│  ┌────────────┐  │              │  │    + Titles       │   │
│  │ Redis      │  │              │  │  🆕 v2.0          │   │
│  │ Cache      │  │              │  └───────────────────┘   │
│  └────────────┘  │              │                          │
└──────────────────┘              │  ┌───────────────────┐   │
                                  │  │ 3. Series         │   │
                                  │  │    Intelligence   │   │
                                  │  │    NLP + Metadata │   │
                                  │  │  🆕 v2.0          │   │
                                  │  └───────────────────┘   │
                                  │                          │
                                  │  ┌───────────────────┐   │
                                  │  │ 4. Personalizer   │   │
                                  │  │    KNN Collab     │   │
                                  │  └───────────────────┘   │
                                  │                          │
                                  │  ┌───────────────────┐   │
                                  │  │ 5. Neural         │   │
                                  │  │    Keras CF       │   │
                                  │  └───────────────────┘   │
                                  │                          │
                                  │  ┌───────────────────┐   │
                                  │  │ Hybrid Engine     │   │
                                  │  │ (Weighted mix)    │   │
                                  │  └───────────────────┘   │
                                  └──────────────────────────┘
                                            │
                                            ▼
                        ┌────────────────────────────────────┐
                        │      EXTERNAL SERVICES             │
                        │                                    │
                        │  ┌─────────────────────────────┐   │
                        │  │ Google Books API            │   │
                        │  │ (Books primary)             │   │
                        │  └─────────────────────────────┘   │
                        │                                    │
                        │  ┌─────────────────────────────┐   │
                        │  │ Comic Vine API              │   │
                        │  │ (Comics metadata)           │   │
                        │  │ 🆕 v2.0                     │   │
                        │  └─────────────────────────────┘   │
                        │                                    │
                        │  ┌─────────────────────────────┐   │
                        │  │ Internet Archive API        │   │
                        │  │ (Free books + comics)       │   │
                        │  │ 🆕 v2.0                     │   │
                        │  └─────────────────────────────┘   │
                        │                                    │
                        │  ┌─────────────────────────────┐   │
                        │  │ NYT Books API               │   │
                        │  │ (Trending)                  │   │
                        │  └─────────────────────────────┘   │
                        └────────────────────────────────────┘
```

### Architecture Patterns Used

| Pattern | Where Applied | Why |
|---------|---------------|-----|
| **Layered Architecture** | Backend (API → Service → Data) | Separation of concerns |
| **Repository Pattern** | Data access layer | Abstract database logic |
| **Dependency Injection** | FastAPI dependencies | Testability + flexibility |
| **Cache-Aside** | Redis with PostgreSQL | Performance |
| **Circuit Breaker** | External API calls | Resilience |
| **Retry with Backoff** | HTTP client (tenacity) | Handle transient failures |
| **Async/Await** | Backend I/O operations | Concurrent request handling |
| **Polymorphic Content** 🆕 | recommendations, reading_progress | Books + Comics unified |
| **Denormalized JSON** 🆕 | collections.items_json | Fast Netflix row rendering |
| **Content-Type Symmetry** 🆕 | books/comics parallel tables | ML content-agnostic |
| **Component-Based** | React Native frontend | Reusable UI |
| **WebView Embedding** 🆕 | EPUB reader | Reuse mature EPUB libraries |

---

## 🛠️ Technology Stack

### Complete Stack Overview

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend Framework** | React Native + Expo | SDK 51+ | Cross-platform UI |
| **Frontend Language** | TypeScript | 5.3+ | Type-safe development |
| **State Management** | Zustand | 5.0+ | Global state |
| **Navigation** | React Navigation | 7.x | Screen routing |
| **HTTP Client (FE)** | Axios | 1.7+ | API calls |
| **EPUB Reader** 🆕 | react-native-webview | Latest | Embed EPUB.js for reading |
| **Image Reader** 🆕 | react-native-image-viewer | Latest | Comics page viewer |
| **Backend Framework** | FastAPI | 0.115+ | REST API |
| **Backend Language** | Python | 3.11 | ML ecosystem |
| **ASGI Server** | Uvicorn | 0.32+ | Async server |
| **HTTP Client (BE)** | httpx | 0.27+ | Async external calls |
| **Retry Library** | tenacity | 9.0+ | External API resilience |
| **ORM** | SQLAlchemy | 2.0+ | Database abstraction |
| **Validation** | Pydantic | 2.9+ | Data validation |
| **Auth** | python-jose (JWT) | 3.3+ | Token generation |
| **Password Hashing** | Passlib (bcrypt 4.0.1) | 1.7+ | Secure storage |
| **Primary Database** | PostgreSQL | 16 | Relational data |
| **Cache** | Redis | 7 | Fast key-value store |
| **DB Migrations** | Alembic | 1.13+ | Schema versioning |
| **ML - Classical** | scikit-learn | 1.5+ | TF-IDF, KMeans, KNN |
| **ML - Deep Learning** | Keras/TensorFlow | 3.6+ / 2.18+ | Neural recommender |
| **NLP** | NLTK + TextBlob | 3.9+ / 0.18+ | Mood + sentiment |
| **Data Processing** | Pandas + NumPy | 2.2+ / 1.26+ | ML data pipelines |
| **Testing (BE)** | pytest | 8.3+ | Unit/integration tests |
| **Testing (FE)** | Jest + RN Testing Library | Latest | Component tests |
| **Containerization** | Docker + Compose | 27+ / v2+ | Environment consistency |
| **Reverse Proxy** | Nginx | Alpine latest | Load balancing, SSL |
| **Cloud (Backend)** | AWS EC2 | t3.medium | Backend hosting |
| **Cloud (Frontend Web)** | Vercel | Free tier | Web deployment |
| **CI/CD** | GitHub Actions | Latest | Automation |
| **Version Control** | Git + GitHub | Latest | Source control |

### Why NOT These Alternatives?

*[Unchanged from v1.0]*

### New v2.0 Choices Explained

**Comic Vine over other comics APIs:**
- Best free comics database
- No paid tier required
- Rich metadata (characters, publishers, issues)
- 200 req/hour is enough with caching

**Internet Archive over Open Library CDL:**
- Public domain content is unrestricted (no borrowing system)
- Provides direct EPUB/PDF/image URLs
- No user account required on their side
- Same organization as Open Library

**react-native-webview over native EPUB reader:**
- Mature EPUB.js library works inside WebView
- Cross-platform (iOS + Android + web) with same code
- Avoids native module complexity
- Progress tracking via postMessage bridge

---

## 📱 Frontend Specification

### Framework: React Native + Expo (Managed Workflow)

*[Rationale unchanged from v1.0]*

### Project Structure (Updated v2.0)

```
mobile/
├── src/
│   ├── screens/
│   │   ├── auth/
│   │   │   ├── WelcomeScreen.tsx
│   │   │   ├── LoginScreen.tsx
│   │   │   └── RegisterScreen.tsx
│   │   ├── onboarding/
│   │   │   ├── ContentChoiceScreen.tsx  🆕 books/comics/both
│   │   │   ├── RateBooksScreen.tsx
│   │   │   └── GenreSelectScreen.tsx
│   │   ├── main/
│   │   │   ├── HomeScreen.tsx           🔄 Netflix-style rows
│   │   │   ├── SearchScreen.tsx         🔄 Books + Comics tabs
│   │   │   ├── LibraryScreen.tsx        🔄 Books + Comics tabs
│   │   │   ├── ProfileScreen.tsx
│   │   │   └── InsightsScreen.tsx
│   │   ├── detail/
│   │   │   ├── DetailScreen.tsx         🔄 Works for books + comics
│   │   │   └── FullCollectionScreen.tsx 🆕 Full collection view
│   │   ├── reader/                      🆕 v2.0
│   │   │   ├── EPUBReaderScreen.tsx     🆕 EPUB WebView reader
│   │   │   └── ComicsReaderScreen.tsx   🆕 Image-based reader
│   │   └── settings/
│   │       └── SettingsScreen.tsx
│   │
│   ├── components/
│   │   ├── common/
│   │   ├── content/                      🆕 v2.0 (books + comics)
│   │   │   ├── ContentCard.tsx           🆕 Card for books + comics
│   │   │   ├── CollectionRow.tsx         🆕 Netflix-style row
│   │   │   ├── SearchResultCard.tsx      🆕
│   │   │   └── SeriesOrderSection.tsx    🆕 Series reading order
│   │   ├── ratings/
│   │   │   └── RatingModal.tsx
│   │   └── insights/
│   │
│   ├── navigation/
│   │   ├── RootNavigator.tsx
│   │   ├── AuthStack.tsx
│   │   ├── OnboardingStack.tsx
│   │   ├── MainTabs.tsx
│   │   └── ReaderStack.tsx               🆕 v2.0
│   │
│   ├── services/
│   │   ├── api.ts
│   │   ├── authService.ts
│   │   ├── bookService.ts
│   │   ├── comicService.ts               🆕 v2.0
│   │   ├── collectionService.ts          🆕 v2.0
│   │   ├── seriesService.ts              🆕 v2.0
│   │   ├── readingProgressService.ts     🆕 v2.0
│   │   ├── ratingService.ts
│   │   └── libraryService.ts
│   │
│   ├── stores/
│   │   ├── userStore.ts
│   │   ├── libraryStore.ts
│   │   └── readingStore.ts               🆕 v2.0
│   │
│   ├── types/
│   │   ├── book.ts
│   │   ├── comic.ts                      🆕 v2.0
│   │   ├── collection.ts                 🆕 v2.0
│   │   ├── series.ts                     🆕 v2.0
│   │   ├── reading.ts                    🆕 v2.0
│   │   ├── user.ts
│   │   └── api.ts
│   │
│   └── theme/
│       ├── colors.ts
│       ├── typography.ts
│       └── spacing.ts
```

### Screen Architecture (Updated v2.0)

| Screen | Purpose | Key Features |
|--------|---------|--------------|
| **WelcomeScreen** | New user welcome | Get started CTA |
| **LoginScreen** | User login | Email + password |
| **RegisterScreen** | Account creation | Email + password + name |
| **ContentChoiceScreen** 🆕 | Onboarding: what do you love? | Books / Comics / Both |
| **RateBooksScreen** | Onboarding: rate 5 items | Star selector on popular items |
| **GenreSelectScreen** | Onboarding: pick genres | Multi-select chips |
| **HomeScreen** 🔄 | Netflix-style discovery hub | 6+ themed collection rows |
| **SearchScreen** 🔄 | Books + Comics search | Tabs: All / Books / Comics |
| **DetailScreen** 🔄 | Book or Comic details | Cover, description, series order, free read |
| **FullCollectionScreen** 🆕 | See all items in a collection | Grid view |
| **LibraryScreen** 🔄 | User's collection | Want/Reading/Read × Books/Comics/All |
| **EPUBReaderScreen** 🆕 | Read public domain books | WebView + EPUB.js, progress tracking |
| **ComicsReaderScreen** 🆕 | Read public domain comics | Image pages, swipe, pinch zoom |
| **InsightsScreen** | Reading DNA | Charts, personality profile |
| **ProfileScreen** | User settings | Avatar, stats, edit |
| **SettingsScreen** | App settings | Theme, content preference, logout |

### Netflix-Style Home Screen (New v2.0)

**Layout pattern:**
```
┌─────────────────────────────────────┐
│  Header: Greeting + Profile Icon    │
│                                     │
│  ▶ Continue Reading (if any)        │
│    Horizontal scroll                │
│                                     │
│  🔥 [Personalized Row Title]        │
│    Horizontal scroll (8-12 cards)   │
│                                     │
│  🌍 [Mood Row Title]                │
│    Horizontal scroll                │
│                                     │
│  📖 Free to Read Right Now          │
│    Horizontal scroll                │
│                                     │
│  🦸 Comics — Perfect Starting Point │
│    Horizontal scroll                │
│                                     │
│  ✅ Complete Series — Start to End  │
│    Horizontal scroll                │
│                                     │
│  🔥 Everyone Is Reading This        │
│    Horizontal scroll                │
└─────────────────────────────────────┘
```

**Key components:**
- `<CollectionRow title="..." items={[...]} onSeeAll={...} />`
- `<ContentCard content={book | comic} size="normal|large" />`
- Pull-to-refresh triggers re-fetch of `/api/v1/collections`

### EPUB Reader Architecture (New v2.0)

**Approach:** WebView + EPUB.js

**Flow:**
```
User taps "Read Free" on book detail
         ↓
Navigate to EPUBReaderScreen(book_id)
         ↓
Fetch reading link from /api/v1/reading/{book_id}/link
         ↓
Backend returns Internet Archive EPUB URL
         ↓
WebView loads static HTML page with EPUB.js
         ↓
EPUB.js fetches EPUB from Internet Archive URL
         ↓
User reads. Progress tracked via postMessage bridge:
         ↓
onMessage(progress) → POST /api/v1/reading/{book_id}/progress
```

**Sample HTML (embedded in app):**
```html
<!DOCTYPE html>
<html>
<head><script src="https://cdn.jsdelivr.net/npm/epubjs/dist/epub.min.js"></script></head>
<body>
  <div id="viewer"></div>
  <script>
    const epubUrl = window.EPUB_URL; // Injected from React Native
    const book = ePub(epubUrl);
    const rendition = book.renderTo("viewer", { width: "100%", height: "100%" });
    rendition.display(window.START_CFI || undefined);

    rendition.on("relocated", (location) => {
      window.ReactNativeWebView.postMessage(JSON.stringify({
        type: "progress",
        cfi: location.start.cfi,
        percent: location.start.percentage * 100
      }));
    });
  </script>
</body>
</html>
```

### Comics Reader Architecture (New v2.0)

**Approach:** Native FlatList with images

**Flow:**
```
User taps "Read Free" on comic detail
         ↓
Navigate to ComicsReaderScreen(comic_id)
         ↓
Fetch image URLs from /api/v1/reading/{comic_id}/link
         ↓
Backend returns array of page image URLs from Internet Archive
         ↓
FlatList with horizontal paging renders images
         ↓
User swipes between pages
         ↓
Current page index saved to backend on exit
```

**Features:**
- Pinch to zoom (react-native-image-viewer)
- Page number indicator
- Pre-load next 2 pages for smooth swiping
- Save progress every 5 pages or on exit

---

## 🖥️ Backend Specification

### Framework: FastAPI

*[Rationale unchanged]*

### Project Structure (Updated v2.0)

```
backend/
├── src/
│   ├── main.py
│   ├── config.py
│   │
│   ├── api/
│   │   ├── deps.py
│   │   ├── response.py
│   │   └── routes/
│   │       ├── health.py                ✅ Built
│   │       ├── auth.py                  ✅ Built
│   │       ├── users.py                 ✅ Built
│   │       ├── books.py                 ✅ Built
│   │       ├── ratings.py               ✅ Built
│   │       ├── library.py               ✅ Built
│   │       ├── preferences.py           ✅ Built
│   │       ├── comics.py                🆕 v2.0
│   │       ├── collections.py           🆕 v2.0
│   │       ├── series.py                🆕 v2.0
│   │       └── reading.py               🆕 v2.0
│   │
│   ├── services/
│   │   ├── book_service.py              ✅ Built
│   │   ├── user_service.py              ✅ Built
│   │   ├── rating_service.py            ✅ Built
│   │   ├── library_service.py           ✅ Built
│   │   ├── preferences_service.py       ✅ Built
│   │   ├── comic_service.py             🆕 v2.0
│   │   ├── collection_service.py        🆕 v2.0
│   │   ├── series_service.py            🆕 v2.0
│   │   └── reading_service.py           🆕 v2.0
│   │
│   ├── external/
│   │   ├── google_books.py              ✅ Built
│   │   ├── comic_vine.py                🆕 v2.0
│   │   ├── internet_archive.py          🆕 v2.0
│   │   └── nyt_books.py                 🆕 (Week 3)
│   │
│   ├── ml/                              🆕 v2.0 (all)
│   │   ├── __init__.py
│   │   ├── vectorizer.py                🆕 TF-IDF foundation
│   │   ├── mood_detector.py             🆕 NLP mood tags
│   │   ├── title_templates.py           🆕 Catchy titles
│   │   ├── collection_engine.py         🆕 KMeans + orchestration
│   │   ├── series_detector.py           🆕 Series detection
│   │   ├── series_builder.py            🆕 Reading order builder
│   │   ├── collaborative.py             🆕 KNN
│   │   ├── personalizer.py              🆕 Per-user ranking
│   │   ├── neural.py                    🆕 Keras
│   │   └── hybrid.py                    🆕 Weighted combination
│   │
│   ├── database/
│   │   ├── session.py                   ✅ Built
│   │   ├── base.py                      ✅ Built
│   │   ├── models/
│   │   │   ├── user.py                  ✅ Built
│   │   │   ├── book.py                  ✅ Built (updated v2.0)
│   │   │   ├── rating.py                ✅ Built
│   │   │   ├── library_item.py          ✅ Built
│   │   │   ├── recommendation.py        ✅ Built (updated v2.0)
│   │   │   ├── user_preferences.py      ✅ Built (updated v2.0)
│   │   │   ├── search_history.py        ✅ Built (updated v2.0)
│   │   │   ├── comic.py                 🆕 v2.0
│   │   │   ├── comic_rating.py          🆕 v2.0
│   │   │   ├── comic_library_item.py    🆕 v2.0
│   │   │   ├── collection.py            🆕 v2.0
│   │   │   ├── user_collection.py       🆕 v2.0
│   │   │   ├── reading_progress.py      🆕 v2.0
│   │   │   └── series_metadata.py       🆕 v2.0
│   │   └── crud/
│   │       ├── book.py                  ✅ Built
│   │       ├── user.py                  ✅ Built
│   │       ├── rating.py                ✅ Built
│   │       ├── library.py               ✅ Built
│   │       ├── preferences.py           ✅ Built
│   │       ├── comic.py                 🆕 v2.0
│   │       ├── comic_rating.py          🆕 v2.0
│   │       ├── comic_library.py         🆕 v2.0
│   │       ├── collection.py            🆕 v2.0
│   │       ├── reading_progress.py      🆕 v2.0
│   │       └── series.py                🆕 v2.0
│   │
│   ├── cache/
│   │   ├── redis_client.py              ✅ Built
│   │   └── decorators.py                ✅ Built
│   │
│   ├── auth/
│   │   ├── password.py                  ✅ Built
│   │   ├── jwt_handler.py               ✅ Built
│   │   └── dependencies.py              ✅ Built
│   │
│   ├── schemas/
│   │   ├── user.py                      ✅ Built
│   │   ├── book.py                      ✅ Built
│   │   ├── rating.py                    ✅ Built
│   │   ├── library.py                   ✅ Built
│   │   ├── preferences.py               ✅ Built
│   │   ├── comic.py                     🆕 v2.0
│   │   ├── collection.py                🆕 v2.0
│   │   ├── series.py                    🆕 v2.0
│   │   └── reading_progress.py          🆕 v2.0
│   │
│   └── utils/
│       └── logger.py
│
├── notebooks/                            🆕 v2.0
│   ├── 01_tfidf_vectorizer.ipynb
│   ├── 02_collection_engine.ipynb
│   ├── 03_series_intelligence.ipynb
│   ├── 04_collaborative.ipynb
│   ├── 05_neural.ipynb
│   └── 06_evaluation.ipynb
│
├── ml_models/                            🆕 v2.0 (persisted volume)
│   ├── vectorizer.pkl
│   ├── kmeans.pkl
│   ├── knn.pkl
│   └── neural_recommender.h5
│
├── tests/                                ✅ 351 tests passing
├── alembic/versions/
├── requirements.txt
├── Dockerfile
└── .env
```

### API Design Principles

*[Unchanged from v1.0]*

### Endpoint Overview (Updated v2.0)

| Method | Endpoint | Purpose | Auth | Status |
|--------|----------|---------|------|--------|
| **POST** | `/api/v1/auth/register` | Create account | ❌ | ✅ Built |
| **POST** | `/api/v1/auth/login` | Get JWT token | ❌ | ✅ Built |
| **POST** | `/api/v1/auth/refresh` | Refresh token | ✅ | ✅ Built |
| **GET** | `/api/v1/users/me` | Current user profile | ✅ | ✅ Built |
| **PATCH** | `/api/v1/users/me` | Update profile | ✅ | ✅ Built |
| **DELETE** | `/api/v1/users/me` | Soft delete account | ✅ | ✅ Built |
| **PATCH** | `/api/v1/users/me/password` | Change password | ✅ | ✅ Built |
| **GET** | `/api/v1/books/search?q=` | Search books | ❌ | ✅ Built |
| **GET** | `/api/v1/books/{book_id}` | Book details | ❌ | ✅ Built |
| **GET** | `/api/v1/books/{book_id}/similar` | Similar books | ❌ | ✅ Built |
| **POST** | `/api/v1/books/{book_id}/ratings` | Rate a book | ✅ | ✅ Built |
| **GET** | `/api/v1/books/{book_id}/ratings/me` | My rating for book | ✅ | ✅ Built |
| **DELETE** | `/api/v1/books/{book_id}/ratings/me` | Remove rating | ✅ | ✅ Built |
| **GET** | `/api/v1/users/me/ratings` | My all ratings | ✅ | ✅ Built |
| **POST** | `/api/v1/library` | Add book to library | ✅ | ✅ Built |
| **GET** | `/api/v1/library` | My book library | ✅ | ✅ Built |
| **PATCH** | `/api/v1/library/{book_id}` | Update library entry | ✅ | ✅ Built |
| **DELETE** | `/api/v1/library/{book_id}` | Remove from library | ✅ | ✅ Built |
| **GET** | `/api/v1/users/me/preferences` | Get preferences | ✅ | ✅ Built |
| **PUT** | `/api/v1/users/me/preferences` | Update preferences | ✅ | ✅ Built |
| **POST** | `/api/v1/users/me/preferences/complete` | Complete onboarding | ✅ | ✅ Built |
| **GET** | `/api/v1/comics/search?q=` | Search comics | ❌ | 🆕 Day 25 |
| **GET** | `/api/v1/comics/{comic_id}` | Comic details | ❌ | 🆕 v2.0 |
| **POST** | `/api/v1/comics/{comic_id}/ratings` | Rate a comic | ✅ | 🆕 v2.0 |
| **POST** | `/api/v1/comics/library` | Add comic to library | ✅ | 🆕 v2.0 |
| **GET** | `/api/v1/comics/library` | My comic library | ✅ | 🆕 v2.0 |
| **GET** | `/api/v1/collections` | Home screen collections | ✅ | 🆕 Day 20 |
| **GET** | `/api/v1/collections/{name}` | Full collection view | ✅ | 🆕 Day 20 |
| **GET** | `/api/v1/books/{book_id}/series` | Book series order | ❌ | 🆕 Day 18 |
| **GET** | `/api/v1/comics/{comic_id}/series` | Comic series order | ❌ | 🆕 v2.0 |
| **GET** | `/api/v1/reading/{content_id}/link` | Get reading URL | ✅ | 🆕 v2.0 |
| **GET** | `/api/v1/reading/progress` | My reading progress list | ✅ | 🆕 v2.0 |
| **PATCH** | `/api/v1/reading/{content_id}/progress` | Update progress | ✅ | 🆕 v2.0 |
| **GET** | `/health` | Health check | ❌ | ✅ Built |
| **GET** | `/health/cache` | Redis health | ❌ | ✅ Built |

### Response Format Standard

*[Unchanged from v1.0]*

### HTTP Status Codes Used

*[Unchanged from v1.0]*

---

## 🗄️ Data Layer

### Primary Database: PostgreSQL 16

**Full schema documented in [SCHEMA.md](./SCHEMA.md) v2.0.**

### Tables Summary (v2.0)

**Original 7 tables (Days 1-14) ✅:**
- users, books, ratings, library_items, recommendations, user_preferences, search_history

**New 7 tables (Week 3) 🆕:**
- comics, comic_ratings, comic_library_items, collections, user_collections, reading_progress, series_metadata

**Total: 14 tables** after Week 3 completes.

### ORM: SQLAlchemy 2.0

*[Rationale unchanged from v1.0]*

### Migrations: Alembic

**v2.0 migration workflow requires 13 sequential migrations** documented in SCHEMA.md §14.

### Cache: Redis 7

**Updated TTL Strategy (v2.0):**

| Data | TTL | Reason |
|------|-----|--------|
| Book details | 24h | Books rarely change |
| Comic details | 24h | Comics rarely change |
| Search results (books) | 30m | Fresh but reusable |
| Search results (comics) | 30m | Same pattern |
| Unified search | 30m | Books + comics combined |
| Trending books | 1w | NYT updates weekly |
| User recommendations | 1h | Refresh often |
| **Home collections** 🆕 | 6h | Balance freshness vs cost |
| **Series metadata** 🆕 | 7d | Series order rarely changes |
| **Internet Archive links** 🆕 | 24h | Static once known |
| **Continue reading list** 🆕 | 5m | Updates frequently |
| Rate limit counters | Sliding window | Real-time |

---

## 🤖 AI/ML Specification (Restructured v2.0)

### The 5 ML Modules

Kitabee ML is organized as 5 focused modules that compose together:

---

### Module 1: Vectorizer (Foundation)

**File:** `ml/vectorizer.py`
**Technique:** TF-IDF + Cosine Similarity
**Library:** scikit-learn

**Purpose:** Represent every book and comic as a numeric vector so ML can measure similarity.

**Input:** Text content (title + description + genres + authors)
**Output:** Sparse TF-IDF vector
**Used by:** Modules 2, 3, 4, 5

**Hyperparameters:**
- `max_features`: 5000
- `ngram_range`: (1, 2)
- `min_df`: 2
- `stop_words`: 'english'

**Key methods:**
```python
class BookVectorizer:
    def fit(self, books_and_comics: List[Content]) -> None
    def transform(self, content: Content) -> sparse_matrix
    def similarity(self, id_a: str, id_b: str) -> float
    def similar_to(self, content_id: str, top_n: int) -> List[ScoredItem]
```

---

### Module 2: Collection Engine (Core Feature)

**Files:** `ml/collection_engine.py`, `ml/mood_detector.py`, `ml/title_templates.py`
**Techniques:** KMeans Clustering + NLP Mood Detection + Template Title Generation
**Libraries:** scikit-learn + NLTK + TextBlob

**Purpose:** Group books and comics into Netflix-style themed rows with catchy titles.

**Pipeline:**
```
1. All content vectorized (Module 1)
2. KMeans clusters similar content
3. Mood detector scans descriptions:
   Dark words → "Dark But You Cannot Put It Down"
   Funny words → "Laugh Out Loud Reads"
   Epic words → "Epic Worlds Built From Scratch"
4. Title template engine generates catchy display name
5. Free reading collection assembled from Internet Archive items
6. Trending collection assembled from recent activity
7. Collections cached in DB + Redis
```

**Mood word dictionary (curated):**
```python
MOOD_WORDS = {
    "dark":       ["dark", "grim", "bleak", "sinister", "haunting", "disturbing"],
    "funny":      ["funny", "comedy", "humor", "laugh", "witty", "hilarious"],
    "epic":       ["epic", "vast", "legendary", "grand", "sweeping", "saga"],
    "romantic":   ["love", "romance", "heart", "passion", "tender"],
    "thrilling":  ["thriller", "suspense", "tension", "chase", "danger"],
    "inspiring":  ["inspiring", "courage", "triumph", "hope", "overcome"],
    "cozy":       ["cozy", "warm", "comfort", "gentle", "peaceful", "charming"],
}
```

**Sample collection titles generated:**
```
"Epic Worlds Built From Scratch"
"Dark But You Cannot Put It Down"
"Read It Before Bed Tonight"
"Your Next Obsession — Guaranteed"
"From the Mind of Brandon Sanderson"
"Free to Read Right Now"
"Comics — Perfect Starting Points"
"The Full Journey — Start to Finish"
"Everyone Is Reading This Right Now"
```

**Metrics:**
- Silhouette Score target: > 0.35
- Manual title quality inspection: 8/10 must feel catchy

---

### Module 3: Series Intelligence

**Files:** `ml/series_detector.py`, `ml/series_builder.py`
**Techniques:** Regex + NLP + Metadata Parsing
**Libraries:** NLTK + Python regex + external API metadata

**Purpose:** Detect series membership and generate correct reading order with contextual labels.

**Pipeline:**
```
1. Parse metadata fields (series_name, series_order from books/comics tables)
2. NLP on description for series indicators:
   - "Book 2 of Foundation"
   - "sequel to Dune"
   - "part 3 in the Wheel of Time series"
3. Cross-reference Comic Vine issue numbers for comics
4. Classify entry type: main / prequel / spinoff / companion
5. Build ordered list with labels ("Start Here" on first)
6. Generate contextual tip for complex universes
7. Cache in series_metadata table (TTL 7 days)
```

**Output example:**
```json
{
  "series_name": "Dune",
  "content_type": "book",
  "main_series": [
    {"id": "...", "title": "Dune", "order": 1, "label": "Start Here"},
    {"id": "...", "title": "Dune Messiah", "order": 2, "label": null},
    ...
  ],
  "companion_series": [
    {
      "name": "Prequel Series by Brian Herbert",
      "entries": [...],
      "tip": "Read after Book 1 or after all 6 originals."
    }
  ],
  "tip": "Books 1-3 are the core trilogy. Books 4-6 are for dedicated fans."
}
```

---

### Module 4: Personalizer (Collaborative Filtering)

**Files:** `ml/collaborative.py`, `ml/personalizer.py`
**Technique:** KNN User-Based Collaborative Filtering
**Library:** scikit-learn

**Purpose:** Rank collections per user and generate "Because you loved X..." rows.

**Pipeline:**
```
1. Build user-item ratings matrix from ratings + comic_ratings tables
2. Fit KNN model (k=20, cosine metric)
3. For target user:
   - Find 20 most similar users
   - Aggregate their highly-rated content
   - Generate "Because you loved [top rated item]" row
4. Rank generic collections higher/lower based on user's content type preference
5. Filter out content types user doesn't want (books-only user sees no comics)
```

**Cold start handling:**
- New user with < 5 ratings → skip personalized rows, show mood + trending rows only
- Content type preference from onboarding acts as fallback signal

**Hyperparameters:**
- `n_neighbors`: 20
- `metric`: 'cosine'
- `algorithm`: 'brute' (small dataset)

---

### Module 5: Neural Recommender

**File:** `ml/neural.py`
**Technique:** Neural Collaborative Filtering
**Library:** Keras + TensorFlow

**Purpose:** Learn complex user-content patterns beyond simple similarity. Adds depth to collection ranking.

**Architecture:**
```
Input: (user_id, content_id, content_type)
      ↓
User Embedding (dim=50) + Content Embedding (dim=50)
      ↓
Concatenate → Dense(128, relu) → Dropout(0.3)
      ↓
Dense(64, relu) → Dropout(0.3)
      ↓
Dense(1, sigmoid) → Predicted rating (0-1)
```

**Training:**
- Loss: MSE
- Optimizer: Adam (lr=0.001)
- Epochs: 50 with early stopping
- Batch size: 256
- Target RMSE: < 0.9

**Graceful fallback:** If DB has < 100 total ratings, skip neural training and use content-based + collaborative only.

---

### Hybrid Engine (Orchestration)

**File:** `ml/hybrid.py`

**Purpose:** Combine all modules into final ranked recommendations.

**Weighted formula:**
```python
final_score = (
    0.30 * vectorizer_score +      # Content similarity
    0.30 * personalizer_score +    # Collaborative filtering
    0.40 * neural_score            # Deep learning
)
```

**Additional layers:**
1. **Diversity filter** — max 3 items per genre in one row
2. **Explainability** — attach "Because you loved X" reason
3. **Content type preference** — respect user's books/comics/both setting

---

### Collection Service Assembly (Home Screen)

**File:** `services/collection_service.py`

**`get_home_collections(user_id)` returns minimum 6 rows:**

```
1. "Because you loved [Top Rated Book]..." (Personalizer)
2. Mood-based row e.g. "Epic Worlds Built From Scratch" (Collection Engine)
3. "Free to Read Right Now" (Internet Archive collection)
4. "Complete Series — Start to Finish" (Series Intelligence)
5. "Everyone Is Reading This" (Trending)
6. "Comics — Perfect Starting Points" or "Hidden Gems" (varies)
7+ Additional mood/genre rows based on user taste
```

Result cached in Redis for 6h. Invalidated on new rating.

---

### ML Techniques Summary

| # | Technique | Module | Library |
|---|-----------|--------|---------|
| 1 | TF-IDF Vectorization | Vectorizer | scikit-learn |
| 2 | Cosine Similarity | Vectorizer | scikit-learn |
| 3 | KMeans Clustering | Collection Engine | scikit-learn |
| 4 | NLP Mood Detection | Collection Engine | NLTK + TextBlob |
| 5 | Template Title Generation | Collection Engine | Custom rules |
| 6 | Regex Series Detection | Series Intelligence | Python re |
| 7 | Metadata NLP Parsing | Series Intelligence | NLTK |
| 8 | KNN Collaborative Filtering | Personalizer | scikit-learn |
| 9 | Neural Collaborative Filtering | Neural | Keras |
| 10 | Weighted Hybrid Ranking | Hybrid | Custom |

**Total: 10 ML techniques across 5 modules + 1 hybrid engine.**

### Evaluation Metrics

| Module | Metric | Target |
|--------|--------|--------|
| Vectorizer | Precision@10 (manual) | > 0.65 |
| Collection Engine | Silhouette Score | > 0.35 |
| Collection Engine | Title Quality (manual) | 8/10 catchy |
| Series Intelligence | Order accuracy (top 50 series) | > 90% |
| Personalizer | Recall@10 | > 0.55 |
| Neural | RMSE | < 0.9 |
| Mood Detection | Accuracy (manual sample) | > 80% |

### Model Serving

**Approach:** Pre-computed + On-demand hybrid
- **Batch:** Collections regenerated every 6h for active users
- **Real-time:** New rating triggers async re-rank of user's collections
- **Series metadata:** Computed once, cached 7 days

### ML Model Persistence

**Volume mount in production Docker:**
```yaml
volumes:
  - ./ml_models:/app/ml_models
```

Files persisted:
- `vectorizer.pkl` — TF-IDF model
- `kmeans.pkl` — Cluster centers
- `knn.pkl` — Collaborative filter
- `neural_recommender.h5` — Keras model

Retraining triggered:
- Nightly cron (offline)
- Manual via admin endpoint (future)

---

## 🌐 External API Integrations

### API 1: Google Books API (Books Primary) ✅

**Base URL:** `https://www.googleapis.com/books/v1/`
**Authentication:** API Key
**Rate Limits:** 100,000 req/day with key

**Endpoints Used:**
- `GET /volumes?q={query}` — Search books
- `GET /volumes/{id}` — Book details

**Wrapper:** `external/google_books.py` (already built, 82 tests)

---

### API 2: Comic Vine API (Comics Primary) 🆕

**Base URL:** `https://comicvine.gamespot.com/api/`
**Authentication:** API Key (query parameter)
**Rate Limits:** 200 req/hour (generous with 24h caching)
**Registration:** Free at comicvine.gamespot.com/api

**Endpoints Used:**
- `GET /volumes/?filter=name:{query}` — Search comic volumes
- `GET /volume/4050-{id}/` — Volume details
- `GET /issues/?filter=volume:{volume_id}` — All issues in a series

**Response Structure:**
```json
{
  "error": "OK",
  "results": [
    {
      "id": 42165,
      "name": "Batman: Year One",
      "publisher": {"id": 10, "name": "DC Comics"},
      "description": "<p>Bruce Wayne returns...</p>",
      "start_year": "1987",
      "count_of_issues": 4,
      "image": {
        "original_url": "https://...",
        "medium_url": "https://..."
      },
      "characters": [
        {"id": 1699, "name": "Batman"},
        {"id": 3, "name": "James Gordon"}
      ]
    }
  ]
}
```

**Our Wrapper:**
```python
class ComicVineClient:
    async def search_comics(self, query: str, max_results: int = 20) -> List[Comic]
    async def get_comic_details(self, volume_id: int) -> Comic
    async def get_series_issues(self, volume_id: int) -> List[Comic]
```

**Caching:** All responses cached in Redis for 24h.

---

### API 3: Internet Archive API (Free Reading) 🆕

**Base URL:** `https://archive.org/`
**Authentication:** None required
**Rate Limits:** Be respectful (add User-Agent header)

**Endpoints Used:**
- `GET /advancedsearch.php?q={query}&output=json` — Search
- `GET /metadata/{identifier}` — Item metadata + file listing
- `GET /download/{identifier}/{filename}` — Direct file download

**Search filter for public domain books:**
```
q=title:{query} AND mediatype:texts AND collection:opensource
```

**Search filter for public domain comics:**
```
q=title:{query} AND mediatype:image AND collection:comics
```

**Metadata Response Structure:**
```json
{
  "metadata": {
    "identifier": "prideandprejudice00aust",
    "title": "Pride and Prejudice",
    "creator": "Jane Austen",
    "year": "1813",
    "mediatype": "texts"
  },
  "files": [
    {"name": "pride.epub", "format": "EPUB", "size": "..."},
    {"name": "pride.pdf", "format": "PDF", "size": "..."}
  ]
}
```

**Our Wrapper:**
```python
class InternetArchiveClient:
    async def search_free_books(self, query: str, max_results: int = 20) -> List[Book]
    async def search_free_comics(self, query: str, max_results: int = 20) -> List[Comic]
    async def get_reading_links(self, identifier: str) -> ReadingLinks
    def is_public_domain(self, item: dict) -> bool
```

**Legal:** Only items from `collection:opensource` or explicitly public_domain flagged are consumed.

---

### API 4: NYT Books API (Trending) 🆕

*[Same as v1.0 — used for "Everyone Is Reading This" collection row]*

**Base URL:** `https://api.nytimes.com/svc/books/v3/`
**Rate Limits:** 500 req/day, 5 req/sec

---

### API Resilience Strategy (Updated v2.0)

```python
async def get_content_with_fallback(content_id: str, content_type: str):
    # Try cache first
    cached = await redis.get(f"{content_type}:{content_id}")
    if cached:
        return parse(cached)

    # Try primary API based on content type
    try:
        if content_type == "book":
            content = await google_books.get_details(content_id)
        elif content_type == "comic":
            content = await comic_vine.get_comic_details(content_id)
    except (APIError, TimeoutError):
        # Try DB (previously cached full record)
        content = await db.get_by_external_id(content_id)
        if not content:
            raise HTTPException(404, "Content not found")

    # Cache 24h
    await redis.setex(f"{content_type}:{content_id}", 86400, content.json())
    return content
```

---

## 🔐 Authentication & Security

*[All content unchanged from v1.0 — 351 tests already validate this layer]*

### Additional v2.0 Considerations

**Reading Progress Privacy:**
- `reading_progress` table is fully private
- Never exposed in public library views
- Only user themselves can query their own progress
- Deleted immediately on account deletion (not soft delete)

---

## ⚡ Caching Strategy

*[Base strategy unchanged from v1.0]*

### New Cache Keys in v2.0

| Key Pattern | TTL | Purpose |
|-------------|-----|---------|
| `comic:{comic_id}` | 24h | Comic details |
| `search:comics:{query}` | 30m | Comic search |
| `search:all:{query}` | 30m | Unified search |
| `collections:home:{user_id}` | 6h | Home screen collections |
| `collection:{name}` | 6h | Individual collection |
| `series:{name}:{content_type}` | 7d | Series order |
| `ia:reading_links:{identifier}` | 24h | Internet Archive URLs |
| `reading_progress:{user_id}` | 5m | Continue reading list |

### Cache Invalidation (Updated)

| Event | Keys Invalidated |
|-------|------------------|
| New book rating | `recs:user:{user_id}*`, `collections:home:{user_id}` |
| New comic rating | `recs:user:{user_id}*`, `collections:home:{user_id}` |
| Book/comic added to library | `collections:home:{user_id}` |
| Reading progress update | `reading_progress:{user_id}` |
| Preferences update | `collections:home:{user_id}` |

---

## 📊 Performance Requirements

### Latency Targets (p95) — Updated v2.0

| Endpoint | Target | Reason |
|----------|--------|--------|
| `GET /books/search` | < 500ms | Interactive search |
| `GET /comics/search` 🆕 | < 500ms | Interactive search |
| `GET /books/{id}` (cached) | < 100ms | Instant book details |
| `GET /comics/{id}` (cached) 🆕 | < 100ms | Instant comic details |
| `GET /collections` (cached) 🆕 | < 300ms | Home screen load |
| `GET /collections` (fresh) 🆕 | < 3s | Full ML regeneration |
| `GET /books/{id}/series` 🆕 | < 50ms | Series order (cached 7d) |
| `GET /reading/{id}/link` 🆕 | < 200ms | Fetch reading URL |
| `POST /ratings` | < 200ms | Snappy interaction |
| `POST /auth/login` | < 400ms | Includes bcrypt |

### Throughput Targets
*[Unchanged from v1.0]*

---

## 🚨 Failure Modes & Resilience

### Failure Scenarios & Handling (Updated v2.0)

| Failure | Detection | Response | User Experience |
|---------|-----------|----------|-----------------|
| **Google Books down** | HTTP timeout | Fallback to DB cache | Slower but works |
| **Comic Vine down** 🆕 | HTTP timeout | Fallback to DB cache | Slower for new comics |
| **Internet Archive down** 🆕 | HTTP timeout | Hide "Free to Read" row | Graceful, no error shown |
| **All external APIs down** | All failed | Serve from DB cache | Older data warning |
| **Database down** | Connection error | 503 Service Unavailable | "Try again in a moment" |
| **Redis down** | Connection error | Bypass cache (slow) | Slower but functional |
| **ML model fails** 🆕 | Exception | Return popular items | Generic recs transparent |
| **Collection engine fails** 🆕 | Exception | Show fallback popular rows | User sees generic Netflix rows |
| **Series detection empty** 🆕 | No series found | Hide series section | Clean detail page |
| **EPUB fetch fails** 🆕 | Timeout/404 | Show retry button | "Content unavailable" |
| **Auth service down** | JWT fails | 401 Unauthorized | Login screen |

### Graceful Degradation (Updated v2.0)

**Priority order for home screen collections:**
1. Personalized rows (ML models) — best
2. Mood-based rows (Collection Engine) — good
3. Free reading row (Internet Archive) — always works
4. Trending row (NYT) — cached weekly
5. Popular items (static fallback) — last resort

**Priority order for content details:**
1. Full metadata from cache
2. Metadata from external API
3. Basic metadata from DB
4. Error state with retry

---

## 🚀 Deployment Architecture

*[Base architecture unchanged from v1.0]*

### v2.0 Updates

**ML Model Volume Mount (production docker-compose.yml):**
```yaml
services:
  api:
    build: ./backend
    ports:
      - "127.0.0.1:8000:8000"
    environment:
      - DATABASE_URL=postgresql://kitabee:pass@postgres:5432/kitabee_db
      - REDIS_URL=redis://redis:6379
      - COMIC_VINE_API_KEY=${COMIC_VINE_API_KEY}
      - NYT_API_KEY=${NYT_API_KEY}
    volumes:
      - ./ml_models:/app/ml_models   # 🆕 v2.0: persist trained models
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
```

**Backend Dockerfile (v2.0):**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data (v2.0)
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Create ml_models directory (v2.0)
RUN mkdir -p /app/ml_models

RUN useradd -m -u 1000 appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

---

## 🔄 CI/CD Pipeline

*[Unchanged from v1.0]*

---

## 📈 Monitoring & Observability

*[Unchanged from v1.0]*

### v2.0 Additions

**ML Model Health Check:**
```python
@app.get("/health/ml")
async def ml_health():
    return {
        "status": "healthy",
        "models_loaded": {
            "vectorizer": vectorizer.is_loaded(),
            "collection_engine": collection_engine.is_ready(),
            "collaborative": collaborative.is_loaded(),
            "neural": neural.is_loaded(),
        },
        "last_training": {...}
    }
```

---

## 💻 Development Environment

*[Unchanged from v1.0]*

### v2.0 Additions

**New dev requirements:**
```
pip install scikit-learn keras tensorflow nltk textblob jupyter pandas numpy
```

**New env vars:**
```
COMIC_VINE_API_KEY=xxx
NYT_API_KEY=xxx
```

**Jupyter for ML experimentation:**
```bash
jupyter notebook backend/notebooks/
```

---

## 🧪 Testing Strategy

*[Unchanged from v1.0]*

### Current Status
- **351 tests passing** (Days 1-14 complete)
- **78% coverage** (above 70% target)
- Zero regressions across all changes

### v2.0 Test Additions Planned

- `test_comic_vine.py` — Comic Vine client tests
- `test_internet_archive.py` — Internet Archive client tests
- `test_vectorizer.py` — TF-IDF vectorizer tests
- `test_collection_engine.py` — Collection generation tests
- `test_series_intelligence.py` — Series ordering tests
- `test_collaborative.py` — KNN filter tests
- `test_neural.py` — Neural recommender tests
- `test_collection_service.py` — Orchestration tests
- `test_collections_api.py` — Collections endpoint tests
- `test_comics_api.py` — Comics endpoints tests

**Target after Week 3:** 500+ tests, 75%+ coverage maintained.

---

## 📏 Code Standards

*[Unchanged from v1.0 — see RULES.md for full standards]*

---

## 📦 Dependency Management

### Backend (Python) — Updated v2.0

New dependencies added:
```
scikit-learn==1.5.2
keras==3.6.0
tensorflow==2.18.0
nltk==3.9.1
textblob==0.18.0
pandas==2.2.3
numpy==1.26.4
jupyter==1.1.1
```

### Frontend (Node.js) — Updated v2.0

New dependencies added:
```
react-native-webview: ^13.x  (EPUB reader)
react-native-image-viewer: ^3.x  (Comics reader)
```

---

## 📎 Appendix

### Reference Documents (Updated v2.0)

- [PRD.md](./PRD.md) v2.0 — Product requirements
- [SCHEMA.md](./SCHEMA.md) v2.0 — Database schema
- [IMPLEMENTATIONPLAN.md](./IMPLEMENTATIONPLAN.md) v2.0 — Daily execution plan
- [TRACKER.md](./TRACKER.md) v2.0 — Progress tracking
- [APPFLOW.md](./APPFLOW.md) — User flows (v2.0 update pending)

### External Documentation

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Expo Docs](https://docs.expo.dev)
- [React Native Docs](https://reactnative.dev)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Redis Docs](https://redis.io/docs/)
- [scikit-learn Docs](https://scikit-learn.org)
- [Keras Docs](https://keras.io)
- [Comic Vine API Docs](https://comicvine.gamespot.com/api/documentation)
- [Internet Archive API Docs](https://archive.org/developers/)

### Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Original] | [Your Name] | Initial Tech Spec |
| 2.0 | [Today] | [Your Name] | Added Comics + Internet Archive + Netflix-style Collections + Series Intelligence. Restructured ML into 5 focused modules. Added EPUB/Comics reader frontend architecture. Added new API endpoints for collections, comics, series, reading progress. Updated deployment for ML model persistence. |

---

**End of Tech Spec** 🔧

*"Design like an architect. Build like an engineer. Ship like a pro."*

---

