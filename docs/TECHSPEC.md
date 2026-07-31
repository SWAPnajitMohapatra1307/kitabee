# 🔧 Kitabee — Technical Specification

> **Document Version:** 1.0  
> **Last Updated:** [Today's Date]  
> **Author:** [Your Name]  
> **Status:** 🟢 Approved for Implementation  
> **Related Docs:** [PRD.md](./PRD.md)

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
This document specifies the complete technical implementation of Kitabee — an AI-powered book discovery platform. It defines technology choices, architecture patterns, and engineering standards.

### Scope
- ✅ MVP technical requirements (5-week timeline)
- ✅ Production deployment specifications
- ✅ Development environment setup
- ❌ Post-MVP scaling considerations (see [Future Roadmap](#future-roadmap))

### Target Audience
- Solo developer (project owner)
- Recruiters evaluating engineering depth
- Future contributors (if open-sourced)

### Guiding Principles

1. **🎯 Pragmatism Over Perfection** — Ship in 5 weeks, iterate later
2. **📚 Learn by Building** — Choose tech that teaches valuable skills
3. **💰 Zero Budget** — Free tiers only (AWS free tier, open-source)
4. **🔒 Security First** — No shortcuts on auth or data protection
5. **⚡ Performance Matters** — p95 latency < 300ms for API calls
6. **📖 Documentation Driven** — Every decision documented

---

## 🏗️ System Architecture

### High-Level Architecture Diagram

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
│  └────────┬─────────┘        └────────┬─────────┘           │
└───────────┼──────────────────────────┼──────────────────────┘
            │                          │
            │  HTTPS/WSS               │  HTTPS
            │                          │
            ▼                          ▼
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
│  │  │ Ratings Module │  │ Recommendations    │      │       │
│  │  │ (CRUD)         │  │ Module (ML)        │      │       │
│  │  └────────────────┘  └────────────────────┘      │       │
│  │                                                  │       │
│  │  ┌────────────────┐  ┌────────────────────┐      │       │
│  │  │ Users Module   │  │ Insights Module    │      │       │
│  │  │ (Profile)      │  │ (Analytics)        │      │       │
│  │  └────────────────┘  └────────────────────┘      │       │
│  └──────────────────────────────────────────────────┘       │
└──────┬─────────────────────────────────────┬────────────────┘
       │                                     │
       ▼                                     ▼
┌──────────────────┐              ┌──────────────────────┐
│  DATA LAYER      │              │  ML LAYER            │
│                  │              │                      │
│  ┌────────────┐  │              │  ┌───────────────┐   │
│  │ PostgreSQL │  │              │  │ scikit-learn  │   │
│  │ (Docker)   │  │              │  │ models        │   │
│  │ Port 5432  │  │              │  └───────────────┘   │
│  └────────────┘  │              │                      │
│                  │              │  ┌───────────────┐   │
│  ┌────────────┐  │              │  │ Keras Neural  │   │
│  │ Redis      │  │              │  │ Recommender   │   │
│  │ (Docker)   │  │              │  └───────────────┘   │
│  │ Port 6379  │  │              │                      │
│  └────────────┘  │              │  ┌───────────────┐   │
└──────────────────┘              │  │ NLTK/TextBlob │   │
                                  │  │ (NLP)         │   │
                                  │  └───────────────┘   │
                                  └──────────────────────┘
                                            │
                                            ▼
                        ┌────────────────────────────────────┐
                        │      EXTERNAL SERVICES             │
                        │                                    │
                        │  ┌─────────────────────────────┐   │
                        │  │ Google Books API            │   │
                        │  │ (Primary - 100K req/day)    │   │
                        │  └─────────────────────────────┘   │
                        │                                    │
                        │  ┌─────────────────────────────┐   │
                        │  │ Open Library API            │   │
                        │  │ (Fallback - Unlimited)      │   │
                        │  └─────────────────────────────┘   │
                        │                                    │
                        │  ┌─────────────────────────────┐   │
                        │  │ NYT Books API               │   │
                        │  │ (Bestsellers - 500/day)     │   │
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
| **Component-Based** | React Native frontend | Reusable UI |
| **Context API** | Frontend state | Avoid prop drilling |

---

## 🛠️ Technology Stack

### Complete Stack Overview

| Layer | Technology | Version | Purpose |
|-------|-----------|---------|---------|
| **Frontend Framework** | React Native + Expo | SDK 51+ | Cross-platform UI |
| **Frontend Language** | TypeScript | 5.3+ | Type-safe development |
| **Web Bundler** | Metro / Webpack (Expo) | Built-in | Bundle for web export |
| **Mobile Distribution** | Expo Go | Latest | Bypass app stores |
| **State Management** | Zustand | 5.0+ | Global state |
| **Navigation** | React Navigation | 7.x | Screen routing |
| **HTTP Client (FE)** | Axios | 1.7+ | API calls |
| **Backend Framework** | FastAPI | 0.115+ | REST API |
| **Backend Language** | Python | 3.11 | ML ecosystem |
| **ASGI Server** | Uvicorn | 0.32+ | Async server |
| **HTTP Client (BE)** | httpx | 0.27+ | Async external calls |
| **ORM** | SQLAlchemy | 2.0+ | Database abstraction |
| **Validation** | Pydantic | 2.9+ | Data validation |
| **Auth** | python-jose (JWT) | 3.3+ | Token generation |
| **Password Hashing** | Passlib (bcrypt) | 1.7+ | Secure storage |
| **Primary Database** | PostgreSQL | 16 | Relational data |
| **Cache** | Redis | 7 | Fast key-value store |
| **DB Migrations** | Alembic | 1.13+ | Schema versioning |
| **ML - Classical** | scikit-learn | 1.5+ | TF-IDF, KNN, KMeans |
| **ML - Deep Learning** | Keras/TensorFlow | 3.6+ / 2.18+ | Neural recommender |
| **NLP** | NLTK + TextBlob | 3.9+ / 0.18+ | Sentiment analysis |
| **Data Processing** | Pandas + NumPy | 2.2+ / 1.26+ | Data manipulation |
| **Testing (BE)** | pytest | 8.3+ | Unit/integration tests |
| **Testing (FE)** | Jest + RN Testing Library | Latest | Component tests |
| **Containerization** | Docker + Compose | 27+ / v2+ | Environment consistency |
| **Reverse Proxy** | Nginx | Alpine latest | Load balancing, SSL |
| **Cloud (Backend)** | AWS EC2 | t3.medium | Backend hosting |
| **Cloud (Frontend Web)** | Vercel | Free tier | Web deployment |
| **CI/CD** | GitHub Actions | Latest | Automation |
| **Version Control** | Git + GitHub | Latest | Source control |
| **Package Managers** | pip / npm | Latest | Dependencies |
| **Code Formatter (BE)** | Black + isort | 24.10+ / 5.13+ | Python formatting |
| **Code Formatter (FE)** | Prettier | Latest | JS/TS formatting |
| **Linter (BE)** | flake8 | 7.1+ | Python linting |
| **Linter (FE)** | ESLint | Latest | JS/TS linting |
| **API Testing** | Thunder Client / Postman | Latest | Manual testing |
| **DB Client** | pgAdmin / DBeaver | Latest | Database GUI |

### Why NOT These Alternatives?

| Considered | Rejected Because |
|------------|------------------|
| **Django REST** (vs FastAPI) | Overhead for our size; less async-native |
| **Flask** (vs FastAPI) | No async, no auto-docs, needs many extensions |
| **Express (Node)** (vs FastAPI) | Would require context-switching from Python ML |
| **MongoDB** (vs PostgreSQL) | Our data is highly relational; ACID needed |
| **Firebase** (vs custom backend) | Vendor lock-in; hides valuable learning |
| **Bare React Native** (vs Expo) | Requires Xcode/Android Studio; complex setup |
| **Flutter** (vs React Native) | Less ecosystem for ML backend integration |
| **Redux** (vs Zustand) | Boilerplate-heavy for our size |
| **Native Android/iOS** | 3x development time; not portfolio priority |
| **Heroku** (vs AWS) | Less industry-relevant for jobs |
| **GCP/Azure** (vs AWS) | AWS has larger job market share |
| **MySQL** (vs PostgreSQL) | Postgres has better JSON support + performance |
| **Memcached** (vs Redis) | Redis has more features (pub/sub, structures) |
| **Poetry** (vs pip) | Simpler workflow with venv + pip for MVP |

---

## 📱 Frontend Specification

### Framework: React Native + Expo (Managed Workflow)

**Rationale:**
- ✅ Single codebase for iOS, Android, Web
- ✅ Expo Go enables QR-code distribution (no app store)
- ✅ TypeScript support out-of-box
- ✅ Rich ecosystem (React Navigation, Reanimated)
- ✅ Web export via `npx expo export:web`

### Project Structure

```
mobile/
├── src/
│   ├── screens/              # Top-level screens
│   │   ├── OnboardingScreen.tsx
│   │   ├── HomeScreen.tsx
│   │   ├── SearchScreen.tsx
│   │   ├── BookDetailsScreen.tsx
│   │   ├── LibraryScreen.tsx
│   │   ├── InsightsScreen.tsx
│   │   └── ProfileScreen.tsx
│   │
│   ├── components/           # Reusable UI components
│   │   ├── common/          # Buttons, Cards, Inputs
│   │   ├── books/           # BookCard, BookGrid, BookList
│   │   ├── ratings/         # StarRating, ReviewInput
│   │   └── insights/        # Charts, DNACard
│   │
│   ├── navigation/          # React Navigation setup
│   │   ├── AppNavigator.tsx
│   │   └── TabNavigator.tsx
│   │
│   ├── context/             # Global state (Context API)
│   │   ├── AuthContext.tsx
│   │   ├── ThemeContext.tsx
│   │   └── LibraryContext.tsx
│   │
│   ├── services/            # API clients
│   │   ├── api.ts           # Axios instance
│   │   ├── authService.ts
│   │   ├── bookService.ts
│   │   ├── ratingService.ts
│   │   └── recommendationService.ts
│   │
│   ├── hooks/               # Custom React hooks
│   │   ├── useAuth.ts
│   │   ├── useBooks.ts
│   │   └── useDebounce.ts
│   │
│   ├── store/               # Zustand stores
│   │   ├── userStore.ts
│   │   └── libraryStore.ts
│   │
│   ├── types/               # TypeScript definitions
│   │   ├── book.ts
│   │   ├── user.ts
│   │   └── api.ts
│   │
│   ├── utils/               # Helper functions
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── constants.ts
│   │
│   └── theme/               # Design system
│       ├── colors.ts
│       ├── typography.ts
│       └── spacing.ts
│
├── assets/                  # Images, fonts, animations
├── App.tsx                  # Root component
├── app.json                 # Expo config
├── tsconfig.json            # TypeScript config
└── package.json
```

### Screen Architecture

| Screen | Purpose | Key Features |
|--------|---------|--------------|
| **OnboardingScreen** | New user welcome | Login/Signup, tutorial |
| **HomeScreen** | Discovery hub | Recommendations, trending |
| **SearchScreen** | Book search | Real-time search, filters |
| **BookDetailsScreen** | Book info | Full metadata, similar books |
| **LibraryScreen** | User's books | Tabs: Want to Read, Reading, Read |
| **InsightsScreen** | Reading DNA | Charts, stats, personality |
| **ProfileScreen** | User settings | Theme, logout, account |

### State Management: Zustand

**Why Zustand?**
- ✅ Simpler than Redux (no reducers, actions boilerplate)
- ✅ TypeScript-friendly
- ✅ 1KB bundle size (vs Redux's 20KB+)
- ✅ Perfect for MVP scale

**Example Store:**
```typescript
// stores/userStore.ts
import { create } from 'zustand';

interface UserState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (user: User, token: string) => void;
  logout: () => void;
}

export const useUserStore = create<UserState>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,
  login: (user, token) => set({ user, token, isAuthenticated: true }),
  logout: () => set({ user: null, token: null, isAuthenticated: false }),
}));
```

### Navigation: React Navigation v7

**Structure:**
- **Auth Stack** (Login, Register, Onboarding)
- **Main Tab Navigator** (Home, Search, Library, Insights, Profile)
- **Modal Stack** (Book Details, Rating Modal)

### Styling Approach

**Custom Theme Context** (inspired by industry pattern):
```typescript
// theme/colors.ts
export const lightColors = {
  primary: '#FFC93C',      // Honey Yellow
  secondary: '#1E3A8A',    // Deep Blue
  accent: '#10B981',       // Green
  background: '#FFF8E7',
  surface: '#FFFFFF',
  textPrimary: '#1F2937',
  textSecondary: '#6B7280',
  border: '#E5E7EB',
};

export const darkColors = {
  primary: '#FFD65C',
  secondary: '#3B82F6',
  accent: '#34D399',
  background: '#0F172A',
  surface: '#1E293B',
  textPrimary: '#F9FAFB',
  textSecondary: '#9CA3AF',
  border: '#374151',
};
```

### Fonts

**Google Fonts (via Expo):**
- Headings: **Poppins** (400, 600, 700)
- Body: **Inter** (400, 500, 600)

### Cross-Platform Considerations

| Feature | Web | Mobile | Handling |
|---------|-----|--------|----------|
| **Storage** | localStorage | AsyncStorage | Wrapper utility |
| **Navigation** | URL-based | Stack-based | React Navigation handles both |
| **Fonts** | Web fonts | Expo fonts | Same package |
| **Images** | `<img>` | `<Image>` | React Native Image works both |
| **Icons** | @expo/vector-icons | @expo/vector-icons | Same package |
| **Alerts** | window.alert | Alert.alert | Platform.OS check |

---

## 🖥️ Backend Specification

### Framework: FastAPI

**Rationale:**
- ✅ **Native async/await** (critical for external API calls)
- ✅ **Auto-generated OpenAPI docs** (Swagger UI + ReDoc)
- ✅ **Pydantic integration** (runtime type validation)
- ✅ **High performance** (comparable to NodeJS/Go)
- ✅ **Modern Python** (type hints, async)
- ✅ **Growing job market**

### Project Structure

```
backend/
├── src/
│   ├── main.py                    # FastAPI app entry
│   ├── config.py                  # Settings (Pydantic Settings)
│   │
│   ├── api/                       # API layer
│   │   ├── __init__.py
│   │   ├── deps.py               # Dependency injection
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py           # /auth endpoints
│   │       ├── books.py          # /books endpoints
│   │       ├── users.py          # /users endpoints
│   │       ├── ratings.py        # /ratings endpoints
│   │       ├── recommendations.py # /recommendations endpoints
│   │       └── health.py         # /health endpoint
│   │
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── book_service.py       # Multi-API book search
│   │   ├── user_service.py       # User management
│   │   ├── rating_service.py     # Rating logic
│   │   └── recommendation_service.py # ML orchestration
│   │
│   ├── external/                  # External API clients
│   │   ├── __init__.py
│   │   ├── google_books.py
│   │   ├── open_library.py
│   │   └── nyt_books.py
│   │
│   ├── ml/                        # ML models
│   │   ├── __init__.py
│   │   ├── content_based.py      # TF-IDF recommender
│   │   ├── collaborative.py      # KNN recommender
│   │   ├── neural.py             # Keras deep model
│   │   ├── sentiment.py          # NLTK sentiment
│   │   ├── clustering.py         # KMeans users
│   │   └── evaluation.py         # Model metrics
│   │
│   ├── database/                  # Database layer
│   │   ├── __init__.py
│   │   ├── session.py            # SQLAlchemy session
│   │   ├── base.py               # Base model
│   │   └── models/               # ORM models
│   │       ├── user.py
│   │       ├── book.py
│   │       ├── rating.py
│   │       └── library.py
│   │
│   ├── cache/                     # Caching layer
│   │   ├── __init__.py
│   │   ├── redis_client.py
│   │   └── decorators.py         # @cached decorator
│   │
│   ├── auth/                      # Authentication
│   │   ├── __init__.py
│   │   ├── jwt_handler.py
│   │   ├── password.py           # bcrypt hashing
│   │   └── dependencies.py       # get_current_user
│   │
│   ├── schemas/                   # Pydantic models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── book.py
│   │   ├── rating.py
│   │   └── recommendation.py
│   │
│   └── utils/                     # Utilities
│       ├── __init__.py
│       ├── logger.py
│       └── validators.py
│
├── tests/                         # Test suite
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_books.py
│   └── test_recommendations.py
│
├── notebooks/                     # ML experimentation
│   ├── 01_data_exploration.ipynb
│   ├── 02_content_based.ipynb
│   └── 03_neural_recommender.ipynb
│
├── models/                        # Trained model artifacts
├── alembic/                       # DB migrations
│   └── versions/
├── alembic.ini
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── .dockerignore
└── .env
```

### API Design Principles

1. **RESTful** — Standard HTTP verbs (GET, POST, PUT, DELETE)
2. **Versioned** — `/api/v1/` prefix (future-proof)
3. **Consistent** — Predictable URL patterns
4. **Documented** — OpenAPI spec auto-generated
5. **Validated** — Pydantic schemas for all requests/responses
6. **Async** — All endpoints async where beneficial

### Endpoint Overview

| Method | Endpoint | Purpose | Auth |
|--------|----------|---------|------|
| **POST** | `/api/v1/auth/register` | Create account | ❌ |
| **POST** | `/api/v1/auth/login` | Get JWT token | ❌ |
| **POST** | `/api/v1/auth/refresh` | Refresh token | ✅ |
| **GET** | `/api/v1/users/me` | Current user profile | ✅ |
| **GET** | `/api/v1/books/search?q=` | Search books | ❌ |
| **GET** | `/api/v1/books/{book_id}` | Book details | ❌ |
| **GET** | `/api/v1/books/trending` | NYT bestsellers | ❌ |
| **POST** | `/api/v1/ratings` | Rate a book | ✅ |
| **GET** | `/api/v1/ratings/user` | User's ratings | ✅ |
| **GET** | `/api/v1/recommendations` | Get personalized recs | ✅ |
| **GET** | `/api/v1/recommendations/{book_id}/similar` | Similar books | ❌ |
| **POST** | `/api/v1/library` | Add to library | ✅ |
| **GET** | `/api/v1/library` | Get user library | ✅ |
| **GET** | `/api/v1/insights/dna` | Reading DNA | ✅ |
| **GET** | `/health` | Health check | ❌ |

### Response Format Standard

**Success Response:**
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": "2025-01-15T10:30:00Z",
    "version": "v1"
  }
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "BOOK_NOT_FOUND",
    "message": "Book with ID xyz not found",
    "details": { ... }
  },
  "meta": {
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
```

### HTTP Status Codes Used

| Code | Meaning | When |
|------|---------|------|
| **200** | OK | Successful GET/PUT/DELETE |
| **201** | Created | Successful POST creation |
| **204** | No Content | Successful DELETE |
| **400** | Bad Request | Invalid input |
| **401** | Unauthorized | Missing/invalid JWT |
| **403** | Forbidden | Auth valid but no permission |
| **404** | Not Found | Resource doesn't exist |
| **409** | Conflict | Duplicate resource |
| **422** | Unprocessable Entity | Validation errors (Pydantic) |
| **429** | Too Many Requests | Rate limit hit |
| **500** | Internal Server Error | Unhandled exception |
| **503** | Service Unavailable | Downstream API failure |

---

## 🗄️ Data Layer

### Primary Database: PostgreSQL 16

**Rationale:**
- ✅ **ACID compliance** for rating consistency
- ✅ **Strong relational model** matches our data
- ✅ **JSON support** for flexible fields (user preferences)
- ✅ **Full-text search** built-in (fallback for book search)
- ✅ **Industry standard** — universal skill

### Database Schema

```sql
-- ============================================
-- USERS TABLE
-- ============================================
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    avatar_url TEXT,
    preferences JSONB DEFAULT '{}',
    onboarding_completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

-- ============================================
-- BOOKS TABLE (Cache of external data)
-- ============================================
CREATE TABLE books (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id VARCHAR(100) UNIQUE NOT NULL, -- Google Books ID
    external_source VARCHAR(50), -- 'google_books', 'open_library'
    title VARCHAR(500) NOT NULL,
    authors TEXT[] NOT NULL,
    description TEXT,
    genres TEXT[],
    isbn_10 VARCHAR(10),
    isbn_13 VARCHAR(13),
    published_year INTEGER,
    publisher VARCHAR(200),
    page_count INTEGER,
    language VARCHAR(10) DEFAULT 'en',
    cover_url TEXT,
    average_rating DECIMAL(3,2),
    ratings_count INTEGER DEFAULT 0,
    embedding VECTOR(384), -- For content-based ML (optional with pgvector)
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_books_external_id ON books(external_id);
CREATE INDEX idx_books_title ON books USING GIN(to_tsvector('english', title));
CREATE INDEX idx_books_isbn_13 ON books(isbn_13);

-- ============================================
-- RATINGS TABLE (ML training data)
-- ============================================
CREATE TABLE ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    book_id UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    rating SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, book_id)
);

CREATE INDEX idx_ratings_user_id ON ratings(user_id);
CREATE INDEX idx_ratings_book_id ON ratings(book_id);
CREATE INDEX idx_ratings_created_at ON ratings(created_at);

-- ============================================
-- LIBRARY TABLE (User's books)
-- ============================================
CREATE TYPE library_status AS ENUM ('want_to_read', 'currently_reading', 'read');

CREATE TABLE library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    book_id UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    status library_status NOT NULL DEFAULT 'want_to_read',
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    started_reading_at TIMESTAMP,
    finished_reading_at TIMESTAMP,
    UNIQUE(user_id, book_id)
);

CREATE INDEX idx_library_user_status ON library(user_id, status);

-- ============================================
-- RECOMMENDATIONS TABLE (Cached ML output)
-- ============================================
CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    book_id UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    score DECIMAL(5,4) NOT NULL,
    model_type VARCHAR(50) NOT NULL, -- 'content', 'collaborative', 'neural', 'hybrid'
    explanation TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_recommendations_user_score ON recommendations(user_id, score DESC);
```

### ORM: SQLAlchemy 2.0

**Why SQLAlchemy?**
- ✅ Industry standard for Python
- ✅ Type-safe with mypy
- ✅ Handles complex queries
- ✅ Migration tool (Alembic) included

**Example Model:**
```python
# database/models/user.py
from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from ..base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100), nullable=False)
    preferences = Column(JSON, default={})
    onboarding_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

### Migrations: Alembic

**Workflow:**
1. Modify SQLAlchemy models
2. Generate migration: `alembic revision --autogenerate -m "add users table"`
3. Review generated migration file
4. Apply: `alembic upgrade head`
5. Rollback if needed: `alembic downgrade -1`

### Cache: Redis 7

**Use Cases:**
- API response caching (Google Books, Open Library)
- Session storage (optional)
- Rate limiting counters
- Trending books (weekly refresh)

**Data Structures:**
- **Strings** — Simple key-value cache
- **Hashes** — Book metadata
- **Sorted Sets** — Trending books (score = popularity)
- **Sets** — User's rated book IDs (fast lookups)

**TTL Strategy:**
| Data | TTL | Reason |
|------|-----|--------|
| Book details | 24h | Books rarely change |
| Search results | 30 min | Fresh but reusable |
| Trending books | 1 week | NYT updates weekly |
| User recommendations | 1h | Refresh often |
| Rate limit counters | Sliding window | Real-time |

---

## 🤖 AI/ML Specification

### Model Portfolio

| # | Model | Library | Purpose | Input | Output |
|---|-------|---------|---------|-------|--------|
| 1 | **TF-IDF Vectorizer** | scikit-learn | Content vectors | Book descriptions | Sparse vectors |
| 2 | **Cosine Similarity** | scikit-learn | Book similarity | Two vectors | Similarity score |
| 3 | **KNN (User-Based)** | scikit-learn | Find similar users | User-item matrix | Top-K neighbors |
| 4 | **KMeans** | scikit-learn | User segmentation | User features | Cluster labels |
| 5 | **Naive Bayes** | scikit-learn | Genre classification | Book text | Genre prediction |
| 6 | **Neural CF** | Keras | Deep personalization | (user, book) pairs | Rating prediction |
| 7 | **Sentiment Analyzer** | NLTK + TextBlob | Review analysis | Text | Sentiment score |
| 8 | **Isolation Forest** | scikit-learn | Fake review detection | Review features | Anomaly score |

### Model 1: Content-Based (TF-IDF)

**Purpose:** Recommend books similar to ones user liked.

**Pipeline:**
```
Book descriptions
      ↓
Text preprocessing (lowercase, remove stopwords, stem)
      ↓
TF-IDF Vectorizer (max_features=5000)
      ↓
Sparse matrix of book vectors
      ↓
For each user's liked book:
  Compute cosine similarity with all other books
      ↓
Aggregate scores → Top 10 recommendations
```

**Hyperparameters:**
- `max_features`: 5000
- `ngram_range`: (1, 2)  # unigrams + bigrams
- `min_df`: 2  # ignore very rare words
- `stop_words`: 'english'

### Model 2: Collaborative Filtering (KNN)

**Purpose:** "Users like you also liked..."

**Pipeline:**
```
User-Item Rating Matrix
      ↓
Compute user similarities (cosine)
      ↓
For target user:
  Find K=20 most similar users
      ↓
Aggregate their ratings (weighted by similarity)
      ↓
Recommend books current user hasn't seen
```

**Hyperparameters:**
- `n_neighbors`: 20
- `metric`: 'cosine'
- `algorithm`: 'brute' (for small dataset)

### Model 3: Neural Collaborative Filtering

**Purpose:** Learn complex patterns beyond simple similarity.

**Architecture:**
```
Input: (user_id, book_id)
      ↓
User Embedding (dim=50) + Book Embedding (dim=50)
      ↓
Concatenate → Dense(128, relu) → Dropout(0.3)
      ↓
Dense(64, relu) → Dropout(0.3)
      ↓
Dense(1, sigmoid) → Predicted rating (0-1)
```

**Training:**
- Loss: Mean Squared Error
- Optimizer: Adam (lr=0.001)
- Epochs: 50 with early stopping
- Batch size: 256
- Train/Val split: 80/20

### Hybrid Recommendation Strategy

```python
def get_recommendations(user_id: str) -> List[Book]:
    # Get scores from each model
    content_scores = content_based_model.recommend(user_id, top_n=50)
    collab_scores = knn_model.recommend(user_id, top_n=50)
    neural_scores = neural_model.recommend(user_id, top_n=50)
    
    # Weighted combination
    final_scores = {}
    for book_id in all_candidates:
        final_scores[book_id] = (
            0.30 * content_scores.get(book_id, 0) +
            0.30 * collab_scores.get(book_id, 0) +
            0.40 * neural_scores.get(book_id, 0)
        )
    
    # Diversity filter (max 2 per genre)
    diverse_recs = apply_diversity_filter(final_scores)
    
    # Return top 10
    return sorted(diverse_recs, key=lambda x: -x['score'])[:10]
```

### Cold Start Handling

**New user with no ratings:**
1. Onboarding: Rate 5-10 popular books
2. Use content-based rec on these initial ratings
3. Also include NYT bestsellers (broad appeal)
4. As user rates more, shift weight to collaborative + neural

### Model Serving

**Approach:** Pre-computed + On-demand hybrid
- **Batch:** Generate recommendations nightly for all active users → cache in DB
- **Real-time:** Trigger recompute when user rates a book (async job)

### Evaluation Metrics

| Model | Primary Metric | Target |
|-------|----------------|--------|
| Content-Based | Precision@10 | > 0.65 |
| Collaborative | Recall@10 | > 0.55 |
| Neural | RMSE | < 0.9 |
| Sentiment | Accuracy | > 85% |
| Genre Classifier | F1 Score | > 0.80 |

---

## 🌐 External API Integrations

### API 1: Google Books API (Primary)

**Base URL:** `https://www.googleapis.com/books/v1/`

**Endpoints Used:**
- `GET /volumes?q={query}` — Search books
- `GET /volumes/{id}` — Book details

**Authentication:** API Key (query parameter)

**Rate Limits:**
- Without key: 1,000 req/day
- With key: 100,000 req/day
- Per-second: 100 req/sec

**Response Structure:**
```json
{
  "items": [
    {
      "id": "abc123",
      "volumeInfo": {
        "title": "...",
        "authors": ["..."],
        "description": "...",
        "categories": ["..."],
        "imageLinks": {
          "thumbnail": "https://...",
          "smallThumbnail": "https://..."
        },
        "averageRating": 4.2,
        "ratingsCount": 1234
      }
    }
  ]
}
```

**Our Wrapper:**
```python
# external/google_books.py
class GoogleBooksClient:
    async def search(self, query: str, max_results: int = 20) -> List[Book]:
        # Implementation with httpx, retry, error handling
        ...
    
    async def get_details(self, book_id: str) -> Book:
        ...
```

### API 2: Open Library (Fallback)

**Base URL:** `https://openlibrary.org/`

**Endpoints Used:**
- `GET /search.json?q={query}` — Search
- `GET /works/{id}.json` — Details
- `GET /covers/b/isbn/{isbn}-L.jpg` — Cover images

**Authentication:** None required

**Rate Limits:** No hard limits, but be respectful (add User-Agent header)

**Use Case:** Fallback when Google Books fails or returns insufficient data

### API 3: NYT Books (Bestsellers)

**Base URL:** `https://api.nytimes.com/svc/books/v3/`

**Endpoints Used:**
- `GET /lists/current/{list-name}.json` — Current bestsellers
- `GET /lists/overview.json` — All lists

**Authentication:** API Key

**Rate Limits:** 500 req/day, 5 req/sec

**Use Case:** "Trending Now" homepage section

### API Resilience Strategy

```python
# services/book_service.py
async def get_book_details(book_id: str) -> Book:
    # Try cache first
    cached = await redis.get(f"book:{book_id}")
    if cached:
        return Book.parse_raw(cached)
    
    # Try primary API
    try:
        book = await google_books.get_details(book_id)
    except (APIError, TimeoutError):
        # Fallback to Open Library
        try:
            book = await open_library.get_details(book_id)
        except APIError:
            # Try DB (previously cached)
            book = await db.get_book_by_external_id(book_id)
            if not book:
                raise HTTPException(status_code=404, detail="Book not found")
    
    # Cache for 24 hours
    await redis.setex(f"book:{book_id}", 86400, book.json())
    return book
```

---

## 🔐 Authentication & Security

### Authentication: JWT (JSON Web Tokens)

**Flow:**
```
1. User submits email + password → POST /auth/login
2. Server verifies password (bcrypt)
3. Server generates JWT (signed with SECRET_KEY)
4. Client stores JWT (AsyncStorage/localStorage)
5. Client sends JWT in Authorization header
6. Server validates JWT on each request
```

**JWT Structure:**
```json
{
  "sub": "user_id_here",
  "email": "user@example.com",
  "iat": 1705318200,
  "exp": 1705404600,
  "type": "access"
}
```

**Token Types:**
- **Access Token:** 24 hours (short-lived)
- **Refresh Token:** 30 days (for renewal)

**Configuration:**
```python
JWT_SECRET_KEY = "..."  # 256-bit random (from env)
JWT_ALGORITHM = "HS256"
JWT_ACCESS_EXPIRE_MINUTES = 1440  # 24h
JWT_REFRESH_EXPIRE_DAYS = 30
```

### Password Security

**Hashing:** bcrypt with cost factor 12

**Requirements:**
- Min 8 characters
- At least 1 uppercase, 1 lowercase, 1 number
- No common passwords (validate against list)

**Implementation:**
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)
```

### Security Best Practices

| Concern | Mitigation |
|---------|------------|
| **SQL Injection** | SQLAlchemy ORM (parameterized queries) |
| **XSS** | React's default escaping + Content-Security-Policy |
| **CSRF** | JWT in Authorization header (not cookies) |
| **Password leaks** | bcrypt hashing, never log passwords |
| **API abuse** | Rate limiting (100 req/min per user) |
| **Secrets in Git** | `.env` in `.gitignore`, use env vars |
| **HTTPS only** | Nginx redirects HTTP → HTTPS |
| **CORS** | Whitelist frontend domain only |
| **Auth token theft** | Short access token expiry (24h) |
| **Timing attacks** | Constant-time password comparison |

### CORS Configuration

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",  # Expo dev
        "http://localhost:19006", # Expo web
        "https://kitabee.vercel.app",  # Production web
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## ⚡ Caching Strategy

### Multi-Level Cache

```
Level 1: In-Memory (LRU Cache on API endpoints)
   ↓ (miss)
Level 2: Redis (24h TTL for books, 1h for recs)
   ↓ (miss)
Level 3: PostgreSQL (permanent for cached API data)
   ↓ (miss)
Level 4: External API (fresh data)
```

### Cache Patterns

**Pattern 1: Cache-Aside (Read)**
```python
async def get_book(book_id: str) -> Book:
    # Try cache
    cached = await redis.get(f"book:{book_id}")
    if cached:
        return Book.parse_raw(cached)
    
    # Cache miss → fetch from source
    book = await fetch_from_api(book_id)
    
    # Write to cache
    await redis.setex(f"book:{book_id}", 86400, book.json())
    return book
```

**Pattern 2: Write-Through (Ratings)**
```python
async def rate_book(user_id: str, book_id: str, rating: int):
    # Write to DB
    await db.insert_rating(user_id, book_id, rating)
    
    # Invalidate user's recommendations cache
    await redis.delete(f"recs:user:{user_id}")
    
    # Trigger async ML retraining
    await queue.publish("retrain_user", user_id)
```

### Cache Invalidation

**Time-Based (TTL):**
- Books: 24h
- Search: 30min
- Recommendations: 1h
- Trending: 1 week

**Event-Based:**
- New rating → invalidate user recs
- Book update (rare) → invalidate book cache

---

## 📊 Performance Requirements

### Latency Targets (p95)

| Endpoint | Target | Reason |
|----------|--------|--------|
| `GET /books/search` | < 500ms | Interactive search |
| `GET /books/{id}` (cached) | < 100ms | Instant book details |
| `GET /books/{id}` (fresh) | < 2s | External API call |
| `GET /recommendations` | < 300ms | User-facing home |
| `POST /ratings` | < 200ms | Snappy interaction |
| `POST /auth/login` | < 400ms | Includes bcrypt |

### Throughput Targets

- **API:** 100 req/sec sustained
- **Concurrent users:** 500
- **Daily requests:** 1M

### Optimization Techniques

1. **Async I/O** — Non-blocking external API calls
2. **Connection pooling** — DB (10 connections), Redis (20)
3. **Query optimization** — Indexes on frequent lookups
4. **N+1 avoidance** — SQLAlchemy `selectinload`
5. **Response compression** — gzip via Nginx
6. **CDN for static** — Vercel handles frontend caching

---

## 🚨 Failure Modes & Resilience

### Failure Scenarios & Handling

| Failure | Detection | Response | User Experience |
|---------|-----------|----------|-----------------|
| **Google Books down** | HTTP timeout | Fallback to Open Library | Slight delay, still works |
| **All external APIs down** | All failed | Serve from DB cache | Older data, warning banner |
| **Database down** | Connection error | 503 Service Unavailable | "Try again in a moment" |
| **Redis down** | Connection error | Bypass cache (slow but works) | Slower but functional |
| **ML model fails** | Exception in service | Return popular books | Generic recs (transparent) |
| **Auth service down** | JWT verification fails | 401 Unauthorized | Login screen |
| **Rate limit hit (external)** | 429 response | Exponential backoff + cache | Fallback to cache |
| **Disk full** | Write error | Log to monitoring | Read-only mode |

### Circuit Breaker Pattern

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
async def call_google_books(query: str):
    # After 3 failures with exponential backoff, give up
    ...
```

### Graceful Degradation

**Priority order for recommendations:**
1. Personalized (ML models) — best
2. Similar users' favorites — good
3. Trending books (NYT) — okay
4. Popular books (static list) — fallback
5. Empty state with search CTA — last resort

---

## 🚀 Deployment Architecture

### Environments

| Environment | Purpose | URL Pattern |
|-------------|---------|-------------|
| **Local** | Development | `localhost:8000` |
| **Staging** | Pre-prod testing | `staging.kitabee.app` (optional) |
| **Production** | Live users | `kitabee.vercel.app` + `api.kitabee.app` |

### Backend Deployment: AWS EC2

**Instance:** t3.medium (2 vCPU, 4GB RAM)
**Region:** ap-south-1 (Mumbai)
**OS:** Ubuntu 22.04 LTS

**Stack on EC2:**
```
┌──────────────────────────────────────┐
│  Nginx (port 80, 443)                │
│  ├─ SSL termination                  │
│  └─ Reverse proxy → 127.0.0.1:8000   │
└──────────────────────────────────────┘
                ↓
┌──────────────────────────────────────┐
│  Docker Compose Stack                │
│                                      │
│  ┌────────────────────────────────┐  │
│  │ FastAPI (Uvicorn)              │  │
│  │ Port 8000                      │  │
│  └────────────────────────────────┘  │
│                                      │
│  ┌────────────────────────────────┐  │
│  │ PostgreSQL 16                  │  │
│  │ Port 5432                      │  │
│  └────────────────────────────────┘  │
│                                      │
│  ┌────────────────────────────────┐  │
│  │ Redis 7                        │  │
│  │ Port 6379                      │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
```

### Frontend Deployment

**Web (Vercel):**
```bash
# Build for web
cd mobile
npx expo export -p web

# Deploy
vercel deploy --prod
```

**Mobile (Expo Go):**
```bash
# Publish update
eas update --branch production --message "v0.1.0"

# Share QR code (from Expo dashboard)
```

### Docker Configuration

**Backend Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Non-root user
RUN useradd -m -u 1000 appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**docker-compose.yml (production):**
```yaml
services:
  api:
    build: ./backend
    ports:
      - "127.0.0.1:8000:8000"
    environment:
      - DATABASE_URL=postgresql://kitabee:pass@postgres:5432/kitabee_db
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    restart: unless-stopped
    
  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=kitabee
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=kitabee_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped
    
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - api
    restart: unless-stopped

volumes:
  postgres_data:
```

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflows

**Workflow 1: Backend Tests (on every push)**
```yaml
# .github/workflows/backend-test.yml
name: Backend Tests

on:
  push:
    paths:
      - 'backend/**'
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: test
        ports:
          - 5432:5432
      redis:
        image: redis:7
        ports:
          - 6379:6379
    
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements-dev.txt
      - name: Run tests
        run: |
          cd backend
          pytest --cov=src --cov-report=xml
```

**Workflow 2: Deploy Backend (on main merge)**
```yaml
# .github/workflows/deploy-backend.yml
name: Deploy Backend

on:
  push:
    branches: [main]
    paths:
      - 'backend/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: SSH to EC2 and deploy
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.EC2_HOST }}
          username: ubuntu
          key: ${{ secrets.EC2_SSH_KEY }}
          script: |
            cd /home/ubuntu/kitabee
            git pull
            docker compose down
            docker compose up -d --build
```

---

## 📈 Monitoring & Observability

### Logging

**Library:** Loguru (Python)

**Levels:**
- `DEBUG` — Development only
- `INFO` — Normal operations
- `WARNING` — Recoverable issues
- `ERROR` — Failed operations
- `CRITICAL` — System-level failures

**Format:**
```
2025-01-15 10:30:45 | INFO | src.api.routes.books | Search: query='sapiens' | user_id=abc123
```

### Metrics (Free Tier)

**MVP Approach:** Simple health endpoint + logs

**Post-MVP:** Prometheus + Grafana

### Health Check Endpoint

```python
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "checks": {
            "database": await check_db(),
            "redis": await check_redis(),
            "external_apis": await check_external()
        }
    }
```

---

## 💻 Development Environment

### Required Tools

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.11 | Backend |
| Node.js | 20+ | Frontend |
| Docker Desktop | Latest | Databases |
| Git | Latest | Version control |
| VS Code | Latest | IDE |
| Postman/Thunder | Latest | API testing |

### VS Code Extensions

- Python, Pylance
- ESLint, Prettier
- Docker
- GitLens
- Thunder Client
- Material Icon Theme
- Error Lens

### Development Workflow

```bash
# Backend
cd backend
.\venv\Scripts\activate
uvicorn src.main:app --reload

# Frontend
cd mobile
npx expo start

# Databases
cd docker
docker compose up -d
```

---

## 🧪 Testing Strategy

### Test Pyramid

```
        /\
       /  \  E2E (5%)
      /────\
     /      \  Integration (25%)
    /────────\
   /          \  Unit (70%)
  /────────────\
```

### Backend Testing

**Unit Tests (pytest):**
```python
# tests/test_auth.py
def test_password_hashing():
    plain = "MySecure123!"
    hashed = hash_password(plain)
    assert verify_password(plain, hashed) is True
    assert verify_password("wrong", hashed) is False
```

**Integration Tests:**
```python
# tests/test_api_books.py
def test_search_books(client, mock_google_books):
    response = client.get("/api/v1/books/search?q=sapiens")
    assert response.status_code == 200
    assert len(response.json()["data"]) > 0
```

**Coverage Target:** 70%+

### Frontend Testing

**Component Tests (Jest + RN Testing Library):**
```typescript
// __tests__/BookCard.test.tsx
test('renders book title', () => {
  const { getByText } = render(<BookCard title="Sapiens" />);
  expect(getByText('Sapiens')).toBeTruthy();
});
```

---

## 📏 Code Standards

### Python

**Formatting:** Black (line-length: 100)
**Import sorting:** isort
**Linting:** flake8
**Type hints:** Required for all functions

**Naming:**
- `snake_case` for functions/variables
- `PascalCase` for classes
- `UPPER_SNAKE` for constants
- `_prefix` for private

### TypeScript

**Formatting:** Prettier
**Linting:** ESLint (with react-native config)
**Strict mode:** Enabled

**Naming:**
- `camelCase` for functions/variables
- `PascalCase` for components/types
- `UPPER_SNAKE` for constants

### Git Commits

**Format (Conventional Commits):**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat` — New feature
- `fix` — Bug fix
- `docs` — Documentation
- `style` — Formatting
- `refactor` — Code restructuring
- `test` — Adding tests
- `chore` — Maintenance

**Example:**
```
feat(auth): implement JWT-based authentication

- Add JWT token generation on login
- Add auth middleware for protected routes
- Add refresh token endpoint

Closes #12
```

---

## 📦 Dependency Management

### Backend (Python)

**File:** `requirements.txt` (production), `requirements-dev.txt` (dev)

**Update Strategy:**
- Pin exact versions (`==`) for production
- Weekly `pip list --outdated` review
- Security patches: immediate
- Major upgrades: end of week batches

### Frontend (Node.js)

**File:** `package.json`

**Update Strategy:**
- Use `^` for minor version flexibility
- `npm audit` weekly
- Expo SDK: only upgrade on Expo team's release cycle

### Security Scanning

**GitHub Dependabot:** Enabled (auto-PRs for vulnerabilities)

---

## 📎 Appendix

### Reference Documents

- [PRD.md](./PRD.md) — Product requirements
- [API_DESIGN.md](./API_DESIGN.md) — Detailed API spec (coming)
- [DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md) — Full DB docs (coming)
- [DEPLOYMENT.md](./DEPLOYMENT.md) — Deployment guide (coming)

### External Documentation

- [FastAPI Docs](https://fastapi.tiangolo.com)
- [Expo Docs](https://docs.expo.dev)
- [React Native Docs](https://reactnative.dev)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Redis Docs](https://redis.io/docs/)

### Glossary

- **ASGI:** Asynchronous Server Gateway Interface
- **CORS:** Cross-Origin Resource Sharing
- **JWT:** JSON Web Token
- **ORM:** Object-Relational Mapping
- **TTL:** Time To Live
- **CDN:** Content Delivery Network
- **CI/CD:** Continuous Integration/Deployment

### Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Today] | [Your Name] | Initial Tech Spec |

---

**End of Tech Spec** 🔧

*"Design like an architect. Build like an engineer. Ship like a pro."*