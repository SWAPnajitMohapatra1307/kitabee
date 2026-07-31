# 🗄️ Kitabee — Data Schema Document

> **Document Version:** 1.0  
> **Last Updated:** [Today's Date]  
> **Author:** [Your Name]  
> **Status:** 🟢 Approved for Implementation  
> **Related Docs:** [PRD.md](./PRD.md) | [TECHSPEC.md](./TECHSPEC.md) | [APPFLOW.md](./APPFLOW.md)

---

## 📚 Table of Contents

1. [Overview](#-overview)
2. [Design Principles](#-design-principles)
3. [Entity Relationship Diagram](#-entity-relationship-diagram)
4. [Database Schema (PostgreSQL)](#-database-schema-postgresql)
   - [4.1 Users Table](#41-users-table)
   - [4.2 Books Table](#42-books-table)
   - [4.3 Ratings Table](#43-ratings-table)
   - [4.4 Library Table](#44-library-table)
   - [4.5 Recommendations Table](#45-recommendations-table)
   - [4.6 User Preferences Table](#46-user-preferences-table)
   - [4.7 Search History Table](#47-search-history-table)
5. [Enumerations](#-enumerations)
6. [Indexes & Performance](#-indexes--performance)
7. [Constraints & Validations](#-constraints--validations)
8. [API Schemas (Pydantic)](#-api-schemas-pydantic)
9. [Frontend Types (TypeScript)](#-frontend-types-typescript)
10. [External API Response Schemas](#-external-api-response-schemas)
11. [Redis Cache Schemas](#-redis-cache-schemas)
12. [ML Feature Schemas](#-ml-feature-schemas)
13. [Sample Data](#-sample-data)
14. [Migration Strategy](#-migration-strategy)
15. [Schema Evolution](#-schema-evolution)
16. [Data Privacy & Security](#-data-privacy--security)
17. [Appendix](#-appendix)

---

## 🎯 Overview

### Purpose
This document is the **single source of truth** for every data structure in Kitabee. If it's not documented here, it doesn't exist.

### Scope
- ✅ PostgreSQL database schema (tables, columns, types)
- ✅ Pydantic models (backend validation)
- ✅ TypeScript interfaces (frontend types)
- ✅ Redis cache key patterns
- ✅ External API response shapes
- ✅ ML model input/output structures
- ✅ Sample data for testing

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| **Table names** | `snake_case`, plural | `users`, `ratings` |
| **Column names** | `snake_case` | `user_id`, `created_at` |
| **Primary keys** | `id` (UUID) | `id UUID PRIMARY KEY` |
| **Foreign keys** | `<entity>_id` | `user_id`, `book_id` |
| **Timestamps** | `<action>_at` | `created_at`, `updated_at` |
| **Booleans** | `is_<state>` or `has_<thing>` | `is_active`, `has_completed` |
| **Enums** | `snake_case` values | `'want_to_read'` |
| **Indexes** | `idx_<table>_<columns>` | `idx_ratings_user_book` |
| **Constraints** | `<table>_<column>_<type>` | `users_email_unique` |

---

## 🎨 Design Principles

### 1. UUIDs Over Auto-Increment
- ✅ **Prevents enumeration attacks** (can't guess `/users/1`, `/users/2`)
- ✅ **Client-side generation** (offline-first ready)
- ✅ **Distributed systems safe** (no coordination needed)
- ⚠️ Slightly larger storage (16 bytes vs 4-8 bytes) — acceptable

### 2. Timestamps Everywhere
Every table has:
- `created_at` — When the row was created
- `updated_at` — Last modification time (auto-updated via trigger)

**Why:** Debugging, analytics, audit trails, temporal queries.

### 3. Soft Deletes (Where Appropriate)
User accounts use `deleted_at` timestamp instead of hard DELETE for:
- ✅ Data recovery (accidental deletions)
- ✅ Compliance (regulatory requirements)
- ⚠️ Ratings/library are hard-deleted (privacy on request)

### 4. JSONB for Flexible Fields
Use `JSONB` (PostgreSQL) for:
- User preferences (evolving structure)
- Book metadata extras (varies by source)
- ML feature vectors (dynamic schema)

**Advantages:**
- Schema flexibility without migrations
- Native indexing support (GIN indexes)
- Query with `->` and `->>` operators

### 5. Explicit Over Implicit
- Every column has a comment
- Every relationship has a foreign key
- Every constraint has a name
- Every index has a purpose documented

### 6. Denormalization for Performance
Some fields duplicated for query speed:
- `books.average_rating` (calculated from ratings, cached)
- `books.ratings_count` (denormalized count)
- Updated via triggers or async jobs

**Trade-off:** Slightly more storage + write complexity for massive read performance gain.

---

## 🔗 Entity Relationship Diagram

### High-Level ER Diagram

```
┌─────────────────┐
│     USERS       │
│                 │
│ id (PK)         │◄────┐
│ email           │     │
│ password_hash   │     │
│ name            │     │
│ preferences     │     │
│ created_at      │     │
└─────────────────┘     │
        │               │
        │ 1:N           │
        │               │
        ▼               │
┌─────────────────┐     │
│    RATINGS      │     │
│                 │     │
│ id (PK)         │     │
│ user_id (FK)────┼─────┘
│ book_id (FK)────┼─────┐
│ rating          │     │
│ review_text     │     │
│ created_at      │     │
└─────────────────┘     │
                        │
┌─────────────────┐     │
│     BOOKS       │◄────┤
│                 │     │
│ id (PK)         │     │
│ external_id     │     │
│ title           │     │
│ authors[]       │     │
│ description     │     │
│ genres[]        │     │
│ cover_url       │     │
│ isbn_13         │     │
│ avg_rating      │     │
│ created_at      │     │
└─────────────────┘     │
        │               │
        │ 1:N           │
        │               │
        ▼               │
┌─────────────────┐     │
│    LIBRARY      │     │
│                 │     │
│ id (PK)         │     │
│ user_id (FK)────┼─────┘
│ book_id (FK)    │
│ status          │
│ added_at        │
└─────────────────┘

┌─────────────────┐
│RECOMMENDATIONS  │  (Cached ML output)
│                 │
│ id (PK)         │
│ user_id (FK)    │
│ book_id (FK)    │
│ score           │
│ model_type      │
│ explanation     │
│ generated_at    │
└─────────────────┘

┌─────────────────┐
│USER_PREFERENCES │  (Extended settings)
│                 │
│ id (PK)         │
│ user_id (FK)    │
│ favorite_genres │
│ reading_pace    │
│ notification_settings │
└─────────────────┘

┌─────────────────┐
│SEARCH_HISTORY   │  (User's searches)
│                 │
│ id (PK)         │
│ user_id (FK)    │
│ query           │
│ results_count   │
│ searched_at     │
└─────────────────┘
```

### Relationship Summary

| From | To | Type | Cascade |
|------|-----|------|---------|
| Users → Ratings | 1:N | ON DELETE CASCADE |
| Users → Library | 1:N | ON DELETE CASCADE |
| Users → Recommendations | 1:N | ON DELETE CASCADE |
| Users → SearchHistory | 1:N | ON DELETE CASCADE |
| Books → Ratings | 1:N | ON DELETE CASCADE |
| Books → Library | 1:N | ON DELETE CASCADE |
| Books → Recommendations | 1:N | ON DELETE CASCADE |

---

## 🗄️ Database Schema (PostgreSQL)

### 4.1 Users Table

**Purpose:** Store user accounts and authentication data.

**SQL Definition:**

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(100) NOT NULL,
    avatar_url TEXT,
    bio TEXT,
    date_of_birth DATE,
    onboarding_completed BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE, -- Soft delete
    
    CONSTRAINT users_email_unique UNIQUE (email),
    CONSTRAINT users_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT users_name_length CHECK (LENGTH(name) BETWEEN 2 AND 100)
);

COMMENT ON TABLE users IS 'User accounts for Kitabee';
COMMENT ON COLUMN users.id IS 'Unique user identifier (UUID v4)';
COMMENT ON COLUMN users.email IS 'User email, used for login';
COMMENT ON COLUMN users.password_hash IS 'Bcrypt-hashed password (cost factor 12)';
COMMENT ON COLUMN users.onboarding_completed IS 'True after user rates 5+ initial books';
COMMENT ON COLUMN users.deleted_at IS 'Soft delete timestamp (NULL = active)';

-- Indexes
CREATE UNIQUE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_last_login ON users(last_login_at);
```

**Column Details:**

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | ❌ | `gen_random_uuid()` | Primary key |
| `email` | VARCHAR(255) | ❌ | - | Login email, unique |
| `password_hash` | VARCHAR(255) | ❌ | - | Bcrypt hash |
| `name` | VARCHAR(100) | ❌ | - | Display name (2-100 chars) |
| `avatar_url` | TEXT | ✅ | NULL | Profile picture URL |
| `bio` | TEXT | ✅ | NULL | Optional user bio |
| `date_of_birth` | DATE | ✅ | NULL | For age-appropriate recs |
| `onboarding_completed` | BOOLEAN | ❌ | FALSE | Completed initial setup? |
| `is_active` | BOOLEAN | ❌ | TRUE | Account status |
| `email_verified` | BOOLEAN | ❌ | FALSE | Email verification status |
| `last_login_at` | TIMESTAMP | ✅ | NULL | Last successful login |
| `created_at` | TIMESTAMP | ❌ | NOW() | Account creation time |
| `updated_at` | TIMESTAMP | ❌ | NOW() | Last modification |
| `deleted_at` | TIMESTAMP | ✅ | NULL | Soft delete marker |

**Business Rules:**
- Email must be valid format
- Password stored as bcrypt hash (cost=12)
- Name is 2-100 characters
- Soft deletes preserve data for 30 days, then hard delete

---

### 4.2 Books Table

**Purpose:** Cache book metadata from external APIs (Google Books, Open Library).

**SQL Definition:**

```sql
CREATE TABLE books (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id VARCHAR(100) NOT NULL,
    external_source VARCHAR(50) NOT NULL DEFAULT 'google_books',
    title VARCHAR(500) NOT NULL,
    subtitle VARCHAR(500),
    authors TEXT[] NOT NULL,
    description TEXT,
    genres TEXT[] NOT NULL DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    isbn_10 VARCHAR(10),
    isbn_13 VARCHAR(13),
    published_year INTEGER,
    publisher VARCHAR(200),
    page_count INTEGER,
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    cover_url TEXT,
    cover_url_large TEXT,
    average_rating DECIMAL(3,2) DEFAULT 0.00,
    ratings_count INTEGER DEFAULT 0,
    kitabee_rating DECIMAL(3,2), -- Our internal aggregated rating
    kitabee_ratings_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}', -- Flexible extras
    cached_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT books_external_unique UNIQUE (external_source, external_id),
    CONSTRAINT books_rating_range CHECK (average_rating BETWEEN 0 AND 5),
    CONSTRAINT books_page_count_positive CHECK (page_count > 0 OR page_count IS NULL),
    CONSTRAINT books_year_valid CHECK (published_year BETWEEN 1000 AND EXTRACT(YEAR FROM CURRENT_DATE) + 1)
);

COMMENT ON TABLE books IS 'Book metadata cached from external APIs';
COMMENT ON COLUMN books.external_id IS 'ID from source API (e.g., Google Books volume ID)';
COMMENT ON COLUMN books.external_source IS 'Which API this came from';
COMMENT ON COLUMN books.metadata IS 'Additional fields specific to source API';
COMMENT ON COLUMN books.kitabee_rating IS 'Aggregated rating from Kitabee users only';

-- Indexes
CREATE INDEX idx_books_external ON books(external_source, external_id);
CREATE INDEX idx_books_isbn_13 ON books(isbn_13) WHERE isbn_13 IS NOT NULL;
CREATE INDEX idx_books_title_gin ON books USING GIN(to_tsvector('english', title));
CREATE INDEX idx_books_authors_gin ON books USING GIN(authors);
CREATE INDEX idx_books_genres_gin ON books USING GIN(genres);
CREATE INDEX idx_books_avg_rating ON books(average_rating DESC);
CREATE INDEX idx_books_cached_at ON books(cached_at);
```

**Column Details:**

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | ❌ | `gen_random_uuid()` | Primary key |
| `external_id` | VARCHAR(100) | ❌ | - | ID from source API |
| `external_source` | VARCHAR(50) | ❌ | `'google_books'` | API source |
| `title` | VARCHAR(500) | ❌ | - | Book title |
| `subtitle` | VARCHAR(500) | ✅ | NULL | Optional subtitle |
| `authors` | TEXT[] | ❌ | - | Array of author names |
| `description` | TEXT | ✅ | NULL | Book description |
| `genres` | TEXT[] | ❌ | `{}` | Genre tags |
| `tags` | TEXT[] | ✅ | `{}` | Custom tags |
| `isbn_10` | VARCHAR(10) | ✅ | NULL | ISBN-10 identifier |
| `isbn_13` | VARCHAR(13) | ✅ | NULL | ISBN-13 identifier |
| `published_year` | INTEGER | ✅ | NULL | Publication year |
| `publisher` | VARCHAR(200) | ✅ | NULL | Publisher name |
| `page_count` | INTEGER | ✅ | NULL | Number of pages |
| `language` | VARCHAR(10) | ❌ | `'en'` | ISO language code |
| `cover_url` | TEXT | ✅ | NULL | Small cover image |
| `cover_url_large` | TEXT | ✅ | NULL | High-res cover |
| `average_rating` | DECIMAL(3,2) | ✅ | 0.00 | External avg rating |
| `ratings_count` | INTEGER | ✅ | 0 | External ratings count |
| `kitabee_rating` | DECIMAL(3,2) | ✅ | NULL | Our users' avg rating |
| `kitabee_ratings_count` | INTEGER | ✅ | 0 | Count of Kitabee ratings |
| `metadata` | JSONB | ✅ | `{}` | Extra API-specific data |
| `cached_at` | TIMESTAMP | ❌ | NOW() | When cached from API |
| `created_at` | TIMESTAMP | ❌ | NOW() | First seen |
| `updated_at` | TIMESTAMP | ❌ | NOW() | Last updated |

**Metadata JSONB Example:**
```json
{
  "google_books": {
    "preview_link": "https://books.google.com/...",
    "info_link": "https://books.google.com/...",
    "maturity_rating": "NOT_MATURE"
  },
  "content_warnings": ["violence", "explicit_language"],
  "awards": ["Pulitzer Prize 2020"]
}
```

---

### 4.3 Ratings Table

**Purpose:** Store user ratings and reviews (core ML training data).

**SQL Definition:**

```sql
CREATE TABLE ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    book_id UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    rating SMALLINT NOT NULL,
    review_text TEXT,
    review_title VARCHAR(200),
    is_spoiler BOOLEAN NOT NULL DEFAULT FALSE,
    helpful_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT ratings_user_book_unique UNIQUE (user_id, book_id),
    CONSTRAINT ratings_value_range CHECK (rating BETWEEN 1 AND 5),
    CONSTRAINT ratings_review_length CHECK (LENGTH(review_text) <= 5000)
);

COMMENT ON TABLE ratings IS 'User ratings and reviews of books';
COMMENT ON COLUMN ratings.rating IS 'Star rating (1-5)';
COMMENT ON COLUMN ratings.review_text IS 'Optional written review';
COMMENT ON COLUMN ratings.is_spoiler IS 'Whether review contains spoilers';

-- Indexes
CREATE INDEX idx_ratings_user_id ON ratings(user_id);
CREATE INDEX idx_ratings_book_id ON ratings(book_id);
CREATE INDEX idx_ratings_user_book ON ratings(user_id, book_id);
CREATE INDEX idx_ratings_rating ON ratings(rating);
CREATE INDEX idx_ratings_created_at ON ratings(created_at DESC);
```

**Column Details:**

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | ❌ | `gen_random_uuid()` | Primary key |
| `user_id` | UUID | ❌ | - | FK → users.id |
| `book_id` | UUID | ❌ | - | FK → books.id |
| `rating` | SMALLINT | ❌ | - | 1-5 stars |
| `review_text` | TEXT | ✅ | NULL | Written review (max 5000 chars) |
| `review_title` | VARCHAR(200) | ✅ | NULL | Optional review headline |
| `is_spoiler` | BOOLEAN | ❌ | FALSE | Contains plot spoilers |
| `helpful_count` | INTEGER | ❌ | 0 | Post-MVP: helpful votes |
| `created_at` | TIMESTAMP | ❌ | NOW() | When rated |
| `updated_at` | TIMESTAMP | ❌ | NOW() | Last edit |

**Business Rules:**
- One user can rate one book only ONCE (unique constraint)
- Rating must be 1-5 (integer)
- Rating updates trigger recommendation cache invalidation
- Rating creation triggers ML model retrain (async)

---

### 4.4 Library Table

**Purpose:** Track user's personal book collection (want to read, reading, read).

**SQL Definition:**

```sql
-- Create enum type first
CREATE TYPE library_status_enum AS ENUM (
    'want_to_read',
    'currently_reading',
    'read',
    'dnf' -- Did Not Finish
);

CREATE TABLE library (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    book_id UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    status library_status_enum NOT NULL DEFAULT 'want_to_read',
    current_page INTEGER DEFAULT 0,
    total_pages INTEGER,
    started_reading_at TIMESTAMP WITH TIME ZONE,
    finished_reading_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    is_favorite BOOLEAN NOT NULL DEFAULT FALSE,
    added_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT library_user_book_unique UNIQUE (user_id, book_id),
    CONSTRAINT library_page_valid CHECK (current_page >= 0 AND (total_pages IS NULL OR current_page <= total_pages)),
    CONSTRAINT library_dates_valid CHECK (
        finished_reading_at IS NULL OR 
        started_reading_at IS NULL OR 
        finished_reading_at >= started_reading_at
    )
);

COMMENT ON TABLE library IS 'User book collections and reading status';
COMMENT ON COLUMN library.status IS 'Current status of book in library';
COMMENT ON COLUMN library.current_page IS 'Reading progress tracker';

-- Indexes
CREATE INDEX idx_library_user_id ON library(user_id);
CREATE INDEX idx_library_book_id ON library(book_id);
CREATE INDEX idx_library_user_status ON library(user_id, status);
CREATE INDEX idx_library_added_at ON library(added_at DESC);
```

**Column Details:**

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | ❌ | `gen_random_uuid()` | Primary key |
| `user_id` | UUID | ❌ | - | FK → users.id |
| `book_id` | UUID | ❌ | - | FK → books.id |
| `status` | ENUM | ❌ | `'want_to_read'` | Reading status |
| `current_page` | INTEGER | ✅ | 0 | Progress tracker |
| `total_pages` | INTEGER | ✅ | NULL | Cached from book |
| `started_reading_at` | TIMESTAMP | ✅ | NULL | When began reading |
| `finished_reading_at` | TIMESTAMP | ✅ | NULL | When completed |
| `notes` | TEXT | ✅ | NULL | Personal notes |
| `is_favorite` | BOOLEAN | ❌ | FALSE | Marked as favorite |
| `added_at` | TIMESTAMP | ❌ | NOW() | When added to library |
| `updated_at` | TIMESTAMP | ❌ | NOW() | Last status change |

**State Transitions:**
```
want_to_read → currently_reading → read
                    ↓
                   dnf
```

---

### 4.5 Recommendations Table

**Purpose:** Cache ML-generated recommendations for fast retrieval.

**SQL Definition:**

```sql
CREATE TYPE recommendation_model_enum AS ENUM (
    'content_based',
    'collaborative_knn',
    'neural_cf',
    'hybrid',
    'trending',
    'popular'
);

CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    book_id UUID NOT NULL REFERENCES books(id) ON DELETE CASCADE,
    score DECIMAL(6,5) NOT NULL, -- 0.00000 to 1.00000
    rank INTEGER NOT NULL,
    model_type recommendation_model_enum NOT NULL,
    explanation TEXT,
    metadata JSONB DEFAULT '{}',
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '1 hour'),
    
    CONSTRAINT recommendations_score_range CHECK (score BETWEEN 0 AND 1),
    CONSTRAINT recommendations_rank_positive CHECK (rank > 0)
);

COMMENT ON TABLE recommendations IS 'Cached ML recommendations per user';
COMMENT ON COLUMN recommendations.score IS 'Confidence score (0-1)';
COMMENT ON COLUMN recommendations.rank IS 'Position in recommended list';
COMMENT ON COLUMN recommendations.explanation IS 'Human-readable "why" explanation';
COMMENT ON COLUMN recommendations.expires_at IS 'When this cache expires';

-- Indexes
CREATE INDEX idx_recommendations_user_rank ON recommendations(user_id, rank);
CREATE INDEX idx_recommendations_user_score ON recommendations(user_id, score DESC);
CREATE INDEX idx_recommendations_expires ON recommendations(expires_at);
CREATE INDEX idx_recommendations_model ON recommendations(model_type);
```

**Column Details:**

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | UUID | ❌ | `gen_random_uuid()` | Primary key |
| `user_id` | UUID | ❌ | - | FK → users.id |
| `book_id` | UUID | ❌ | - | FK → books.id |
| `score` | DECIMAL(6,5) | ❌ | - | Confidence 0.00000-1.00000 |
| `rank` | INTEGER | ❌ | - | 1st, 2nd, 3rd... |
| `model_type` | ENUM | ❌ | - | Which model generated this |
| `explanation` | TEXT | ✅ | NULL | Why this book was recommended |
| `metadata` | JSONB | ✅ | `{}` | Model-specific data |
| `generated_at` | TIMESTAMP | ❌ | NOW() | When calculated |
| `expires_at` | TIMESTAMP | ❌ | NOW() + 1h | Cache expiration |

**Metadata JSONB Example:**
```json
{
  "based_on_books": ["book_id_1", "book_id_2"],
  "similar_users_count": 42,
  "genre_match_score": 0.87,
  "content_similarity": 0.72,
  "diversity_boost_applied": true
}
```

---

### 4.6 User Preferences Table

**Purpose:** Store extended user preferences and settings.

**SQL Definition:**

```sql
CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    favorite_genres TEXT[] NOT NULL DEFAULT '{}',
    preferred_languages TEXT[] NOT NULL DEFAULT '{en}',
    excluded_genres TEXT[] DEFAULT '{}',
    content_warnings_hide TEXT[] DEFAULT '{}',
    reading_pace VARCHAR(20) DEFAULT 'medium', -- 'slow', 'medium', 'fast'
    preferred_book_length VARCHAR(20) DEFAULT 'any', -- 'short', 'medium', 'long', 'any'
    theme VARCHAR(20) NOT NULL DEFAULT 'system', -- 'light', 'dark', 'system'
    notification_settings JSONB NOT NULL DEFAULT '{"email": false, "push": false}',
    privacy_settings JSONB NOT NULL DEFAULT '{"public_library": false, "public_ratings": false}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT user_preferences_user_unique UNIQUE (user_id),
    CONSTRAINT user_preferences_theme_valid CHECK (theme IN ('light', 'dark', 'system')),
    CONSTRAINT user_preferences_pace_valid CHECK (reading_pace IN ('slow', 'medium', 'fast'))
);

COMMENT ON TABLE user_preferences IS 'Extended user preferences and settings';

-- Indexes
CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX idx_user_preferences_genres_gin ON user_preferences USING GIN(favorite_genres);
```

**Notification Settings JSONB:**
```json
{
  "email": true,
  "push": false,
  "categories": {
    "new_recommendations": true,
    "reading_reminders": false,
    "weekly_digest": true,
    "friend_activity": false
  }
}
```

**Privacy Settings JSONB:**
```json
{
  "public_library": false,
  "public_ratings": false,
  "show_reading_pace": true,
  "allow_analytics": true
}
```

---

### 4.7 Search History Table

**Purpose:** Track user searches for personalization and UX improvements.

**SQL Definition:**

```sql
CREATE TABLE search_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    query VARCHAR(500) NOT NULL,
    normalized_query VARCHAR(500) NOT NULL, -- Lowercase, trimmed
    results_count INTEGER NOT NULL DEFAULT 0,
    clicked_book_id UUID REFERENCES books(id) ON DELETE SET NULL,
    session_id VARCHAR(100),
    device_type VARCHAR(20), -- 'mobile', 'tablet', 'web'
    searched_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT search_history_query_not_empty CHECK (LENGTH(TRIM(query)) > 0)
);

COMMENT ON TABLE search_history IS 'User search queries for analytics and personalization';
COMMENT ON COLUMN search_history.normalized_query IS 'Normalized for deduplication';
COMMENT ON COLUMN search_history.clicked_book_id IS 'Which book user clicked from results';

-- Indexes
CREATE INDEX idx_search_history_user_id ON search_history(user_id);
CREATE INDEX idx_search_history_searched_at ON search_history(searched_at DESC);
CREATE INDEX idx_search_history_normalized ON search_history(normalized_query);
```

---

## 📋 Enumerations

### Library Status Enum

```sql
CREATE TYPE library_status_enum AS ENUM (
    'want_to_read',
    'currently_reading',
    'read',
    'dnf'
);
```

| Value | Description |
|-------|-------------|
| `want_to_read` | User wants to read (default) |
| `currently_reading` | Actively reading |
| `read` | Finished |
| `dnf` | Did Not Finish |

### Recommendation Model Enum

```sql
CREATE TYPE recommendation_model_enum AS ENUM (
    'content_based',
    'collaborative_knn',
    'neural_cf',
    'hybrid',
    'trending',
    'popular'
);
```

| Value | Description |
|-------|-------------|
| `content_based` | TF-IDF similarity-based |
| `collaborative_knn` | KNN user-based CF |
| `neural_cf` | Keras neural recommender |
| `hybrid` | Weighted combination |
| `trending` | NYT bestsellers |
| `popular` | Popularity-based fallback |

### External Source Enum (Book Source)

Used as VARCHAR (not strict enum for extensibility):
- `google_books` — Google Books API
- `open_library` — Open Library
- `nyt_books` — NYT API
- `manual` — Manually added

---

## 🚀 Indexes & Performance

### Index Strategy

| Table | Index | Purpose | Type |
|-------|-------|---------|------|
| `users` | `idx_users_email` | Login lookup | B-tree UNIQUE |
| `users` | `idx_users_created_at` | Analytics | B-tree |
| `books` | `idx_books_external` | Cache lookup | B-tree UNIQUE |
| `books` | `idx_books_isbn_13` | ISBN search | B-tree |
| `books` | `idx_books_title_gin` | Full-text search | GIN |
| `books` | `idx_books_authors_gin` | Array search | GIN |
| `books` | `idx_books_genres_gin` | Genre filtering | GIN |
| `ratings` | `idx_ratings_user_book` | User's rating lookup | B-tree |
| `ratings` | `idx_ratings_book_id` | Book's ratings | B-tree |
| `library` | `idx_library_user_status` | Filter by status | Composite |
| `recommendations` | `idx_recommendations_user_score` | Fetch top recs | B-tree DESC |

### Query Performance Targets

| Query | Target | Index Used |
|-------|--------|-----------|
| User login by email | < 5ms | `idx_users_email` |
| Book by external_id | < 5ms | `idx_books_external` |
| User's ratings | < 20ms | `idx_ratings_user_id` |
| Top 10 recommendations | < 30ms | `idx_recommendations_user_score` |
| Library filtered by status | < 50ms | `idx_library_user_status` |
| Full-text book search | < 100ms | `idx_books_title_gin` |

### Denormalization

Some fields are duplicated for performance:

**In `books`:**
- `average_rating` — Cached, updated via trigger
- `ratings_count` — Cached count

**Trigger:**
```sql
CREATE OR REPLACE FUNCTION update_book_ratings_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE books
    SET 
        kitabee_rating = (
            SELECT AVG(rating)::DECIMAL(3,2) 
            FROM ratings 
            WHERE book_id = NEW.book_id
        ),
        kitabee_ratings_count = (
            SELECT COUNT(*) 
            FROM ratings 
            WHERE book_id = NEW.book_id
        ),
        updated_at = CURRENT_TIMESTAMP
    WHERE id = NEW.book_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_book_ratings
AFTER INSERT OR UPDATE OR DELETE ON ratings
FOR EACH ROW EXECUTE FUNCTION update_book_ratings_stats();
```

---

## 🔒 Constraints & Validations

### Referential Integrity

All foreign keys use `ON DELETE CASCADE` to prevent orphaned data:
- Delete user → Delete their ratings, library, recommendations
- Delete book → Delete all associated ratings, library entries

### Check Constraints

| Table | Constraint | Rule |
|-------|-----------|------|
| `users` | `users_email_format` | Valid email regex |
| `users` | `users_name_length` | 2-100 chars |
| `books` | `books_rating_range` | 0 ≤ rating ≤ 5 |
| `books` | `books_year_valid` | 1000 ≤ year ≤ current+1 |
| `ratings` | `ratings_value_range` | 1 ≤ rating ≤ 5 |
| `ratings` | `ratings_review_length` | ≤ 5000 chars |
| `library` | `library_page_valid` | current ≤ total |
| `library` | `library_dates_valid` | finished ≥ started |
| `recommendations` | `recommendations_score_range` | 0 ≤ score ≤ 1 |

### Unique Constraints

| Table | Constraint | Purpose |
|-------|-----------|---------|
| `users` | `users_email_unique` | One account per email |
| `books` | `books_external_unique` | No duplicate books |
| `ratings` | `ratings_user_book_unique` | One rating per user per book |
| `library` | `library_user_book_unique` | Book in library once |
| `user_preferences` | `user_preferences_user_unique` | One prefs row per user |

---

## 🐍 API Schemas (Pydantic)

### User Schemas

```python
# schemas/user.py
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional
from uuid import UUID


class UserBase(BaseModel):
    """Shared user fields."""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)


class UserCreate(UserBase):
    """Request schema for user registration."""
    password: str = Field(..., min_length=8, max_length=100)
    
    @validator('password')
    def password_complexity(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain a number')
        return v


class UserLogin(BaseModel):
    """Request schema for login."""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Request schema for profile update."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    date_of_birth: Optional[str] = None  # ISO date


class UserResponse(UserBase):
    """Response schema (no sensitive fields)."""
    id: UUID
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    onboarding_completed: bool
    email_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True  # Allow ORM model conversion


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: UserResponse
```

### Book Schemas

```python
# schemas/book.py
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal


class BookBase(BaseModel):
    """Shared book fields."""
    title: str = Field(..., max_length=500)
    authors: List[str] = Field(..., min_items=1)
    description: Optional[str] = None
    genres: List[str] = []
    isbn_13: Optional[str] = Field(None, max_length=13)
    published_year: Optional[int] = Field(None, ge=1000, le=2100)


class BookResponse(BookBase):
    """Public book response."""
    id: UUID
    external_id: str
    external_source: str
    subtitle: Optional[str] = None
    publisher: Optional[str] = None
    page_count: Optional[int] = None
    language: str = "en"
    cover_url: Optional[str] = None
    cover_url_large: Optional[str] = None
    average_rating: Optional[Decimal] = Field(None, ge=0, le=5)
    ratings_count: int = 0
    kitabee_rating: Optional[Decimal] = None
    kitabee_ratings_count: int = 0
    metadata: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


class BookSearchQuery(BaseModel):
    """Search query params."""
    q: str = Field(..., min_length=2, max_length=200)
    limit: int = Field(20, ge=1, le=40)
    offset: int = Field(0, ge=0)
    genre: Optional[str] = None
    language: str = "en"


class BookSearchResponse(BaseModel):
    """Paginated search results."""
    query: str
    total_count: int
    limit: int
    offset: int
    results: List[BookResponse]
```

### Rating Schemas

```python
# schemas/rating.py
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional
from uuid import UUID


class RatingCreate(BaseModel):
    """Request to create/update rating."""
    book_id: UUID
    rating: int = Field(..., ge=1, le=5)
    review_text: Optional[str] = Field(None, max_length=5000)
    review_title: Optional[str] = Field(None, max_length=200)
    is_spoiler: bool = False


class RatingResponse(BaseModel):
    """Rating response."""
    id: UUID
    user_id: UUID
    book_id: UUID
    rating: int
    review_text: Optional[str] = None
    review_title: Optional[str] = None
    is_spoiler: bool
    helpful_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RatingWithBook(RatingResponse):
    """Rating with embedded book info."""
    book: 'BookResponse'  # Forward reference
```

### Library Schemas

```python
# schemas/library.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from uuid import UUID
from enum import Enum


class LibraryStatus(str, Enum):
    WANT_TO_READ = "want_to_read"
    CURRENTLY_READING = "currently_reading"
    READ = "read"
    DNF = "dnf"


class LibraryEntryCreate(BaseModel):
    book_id: UUID
    status: LibraryStatus = LibraryStatus.WANT_TO_READ
    notes: Optional[str] = None


class LibraryEntryUpdate(BaseModel):
    status: Optional[LibraryStatus] = None
    current_page: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None
    is_favorite: Optional[bool] = None


class LibraryEntryResponse(BaseModel):
    id: UUID
    user_id: UUID
    book_id: UUID
    status: LibraryStatus
    current_page: int
    total_pages: Optional[int] = None
    started_reading_at: Optional[datetime] = None
    finished_reading_at: Optional[datetime] = None
    notes: Optional[str] = None
    is_favorite: bool
    added_at: datetime
    updated_at: datetime
    book: Optional['BookResponse'] = None
    
    class Config:
        from_attributes = True
```

### Recommendation Schemas

```python
# schemas/recommendation.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal
from enum import Enum


class ModelType(str, Enum):
    CONTENT_BASED = "content_based"
    COLLABORATIVE_KNN = "collaborative_knn"
    NEURAL_CF = "neural_cf"
    HYBRID = "hybrid"
    TRENDING = "trending"
    POPULAR = "popular"


class RecommendationResponse(BaseModel):
    id: UUID
    user_id: UUID
    book_id: UUID
    score: Decimal = Field(..., ge=0, le=1)
    rank: int
    model_type: ModelType
    explanation: Optional[str] = None
    metadata: Dict[str, Any] = {}
    generated_at: datetime
    book: Optional['BookResponse'] = None


class RecommendationListResponse(BaseModel):
    user_id: UUID
    generated_at: datetime
    total_count: int
    recommendations: List[RecommendationResponse]
```

### Standard Response Wrapper

```python
# schemas/common.py
from pydantic import BaseModel
from typing import Optional, Any, Generic, TypeVar
from datetime import datetime

T = TypeVar('T')


class SuccessResponse(BaseModel, Generic[T]):
    """Standard success response."""
    success: bool = True
    data: T
    meta: dict = {
        "timestamp": datetime.utcnow().isoformat(),
        "version": "v1"
    }


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    error: ErrorDetail
    meta: dict = {
        "timestamp": datetime.utcnow().isoformat()
    }


class PaginationMeta(BaseModel):
    total: int
    limit: int
    offset: int
    has_more: bool
```

---

## 📘 Frontend Types (TypeScript)

### User Types

```typescript
// types/user.ts

export interface User {
  id: string;
  email: string;
  name: string;
  avatarUrl?: string;
  bio?: string;
  dateOfBirth?: string;
  onboardingCompleted: boolean;
  emailVerified: boolean;
  createdAt: string;
}

export interface UserCredentials {
  email: string;
  password: string;
}

export interface UserRegistration extends UserCredentials {
  name: string;
}

export interface UserUpdate {
  name?: string;
  bio?: string;
  avatarUrl?: string;
  dateOfBirth?: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
  tokenType: 'bearer';
  expiresIn: number;
  user: User;
}
```

### Book Types

```typescript
// types/book.ts

export interface Book {
  id: string;
  externalId: string;
  externalSource: string;
  title: string;
  subtitle?: string;
  authors: string[];
  description?: string;
  genres: string[];
  tags?: string[];
  isbn10?: string;
  isbn13?: string;
  publishedYear?: number;
  publisher?: string;
  pageCount?: number;
  language: string;
  coverUrl?: string;
  coverUrlLarge?: string;
  averageRating: number;
  ratingsCount: number;
  kitabeeRating?: number;
  kitabeeRatingsCount: number;
  metadata: Record<string, any>;
}

export interface BookSearchParams {
  q: string;
  limit?: number;
  offset?: number;
  genre?: string;
  language?: string;
}

export interface BookSearchResults {
  query: string;
  totalCount: number;
  limit: number;
  offset: number;
  results: Book[];
}
```

### Rating Types

```typescript
// types/rating.ts

export interface Rating {
  id: string;
  userId: string;
  bookId: string;
  rating: number; // 1-5
  reviewText?: string;
  reviewTitle?: string;
  isSpoiler: boolean;
  helpfulCount: number;
  createdAt: string;
  updatedAt: string;
}

export interface RatingWithBook extends Rating {
  book: Book;
}

export interface CreateRatingInput {
  bookId: string;
  rating: number;
  reviewText?: string;
  reviewTitle?: string;
  isSpoiler?: boolean;
}
```

### Library Types

```typescript
// types/library.ts

export type LibraryStatus = 'want_to_read' | 'currently_reading' | 'read' | 'dnf';

export interface LibraryEntry {
  id: string;
  userId: string;
  bookId: string;
  status: LibraryStatus;
  currentPage: number;
  totalPages?: number;
  startedReadingAt?: string;
  finishedReadingAt?: string;
  notes?: string;
  isFavorite: boolean;
  addedAt: string;
  updatedAt: string;
  book?: Book;
}

export interface AddToLibraryInput {
  bookId: string;
  status?: LibraryStatus;
  notes?: string;
}

export interface UpdateLibraryInput {
  status?: LibraryStatus;
  currentPage?: number;
  notes?: string;
  isFavorite?: boolean;
}
```

### Recommendation Types

```typescript
// types/recommendation.ts

export type ModelType = 
  | 'content_based' 
  | 'collaborative_knn' 
  | 'neural_cf' 
  | 'hybrid' 
  | 'trending' 
  | 'popular';

export interface Recommendation {
  id: string;
  userId: string;
  bookId: string;
  score: number; // 0-1
  rank: number;
  modelType: ModelType;
  explanation?: string;
  metadata: Record<string, any>;
  generatedAt: string;
  book?: Book;
}

export interface RecommendationList {
  userId: string;
  generatedAt: string;
  totalCount: number;
  recommendations: Recommendation[];
}
```

### API Response Types

```typescript
// types/api.ts

export interface SuccessResponse<T> {
  success: true;
  data: T;
  meta: {
    timestamp: string;
    version: string;
  };
}

export interface ErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: Record<string, any>;
  };
  meta: {
    timestamp: string;
  };
}

export type ApiResponse<T> = SuccessResponse<T> | ErrorResponse;

export interface PaginationMeta {
  total: number;
  limit: number;
  offset: number;
  hasMore: boolean;
}
```

---

## 🌐 External API Response Schemas

### Google Books API

**Endpoint:** `GET https://www.googleapis.com/books/v1/volumes?q={query}`

**Response Schema:**
```typescript
interface GoogleBooksSearchResponse {
  kind: 'books#volumes';
  totalItems: number;
  items?: GoogleBook[];
}

interface GoogleBook {
  kind: 'books#volume';
  id: string;
  etag: string;
  selfLink: string;
  volumeInfo: {
    title: string;
    subtitle?: string;
    authors?: string[];
    publisher?: string;
    publishedDate?: string;
    description?: string;
    industryIdentifiers?: Array<{
      type: 'ISBN_10' | 'ISBN_13' | 'OTHER';
      identifier: string;
    }>;
    pageCount?: number;
    categories?: string[];
    averageRating?: number;
    ratingsCount?: number;
    imageLinks?: {
      smallThumbnail?: string;
      thumbnail?: string;
      small?: string;
      medium?: string;
      large?: string;
      extraLarge?: string;
    };
    language?: string;
    previewLink?: string;
    infoLink?: string;
    canonicalVolumeLink?: string;
  };
  saleInfo?: {
    country: string;
    saleability: string;
  };
  accessInfo?: {
    country: string;
    viewability: string;
  };
}
```

### Open Library API

**Endpoint:** `GET https://openlibrary.org/search.json?q={query}`

**Response Schema:**
```typescript
interface OpenLibrarySearchResponse {
  numFound: number;
  start: number;
  numFoundExact: boolean;
  docs: OpenLibraryDoc[];
}

interface OpenLibraryDoc {
  key: string; // e.g., "/works/OL45804W"
  title: string;
  author_name?: string[];
  author_key?: string[];
  first_publish_year?: number;
  isbn?: string[];
  cover_i?: number; // Use for image URL
  edition_count?: number;
  language?: string[];
  subject?: string[];
  publisher?: string[];
}
```

**Cover URL Pattern:**
```
https://covers.openlibrary.org/b/id/{cover_i}-L.jpg  (Large)
https://covers.openlibrary.org/b/id/{cover_i}-M.jpg  (Medium)
https://covers.openlibrary.org/b/id/{cover_i}-S.jpg  (Small)
```

### NYT Books API

**Endpoint:** `GET https://api.nytimes.com/svc/books/v3/lists/current/hardcover-fiction.json?api-key=...`

**Response Schema:**
```typescript
interface NYTBooksResponse {
  status: 'OK';
  copyright: string;
  num_results: number;
  results: {
    list_name: string;
    bestsellers_date: string;
    published_date: string;
    books: NYTBook[];
  };
}

interface NYTBook {
  rank: number;
  weeks_on_list: number;
  primary_isbn10: string;
  primary_isbn13: string;
  publisher: string;
  description: string;
  title: string;
  author: string;
  contributor: string;
  book_image: string;
  amazon_product_url: string;
}
```

---

## 💾 Redis Cache Schemas

### Cache Key Patterns

**Format:** `<namespace>:<entity>:<identifier>[:<sub-key>]`

| Key Pattern | Value Type | TTL | Purpose |
|-------------|-----------|-----|---------|
| `book:{book_id}` | JSON (Book) | 24h | Book details cache |
| `book:external:{source}:{ext_id}` | JSON (Book) | 24h | External book lookup |
| `search:{normalized_query}` | JSON (BookList) | 30m | Search results |
| `search:{normalized_query}:{page}` | JSON (BookList) | 30m | Paginated search |
| `recs:user:{user_id}` | JSON (RecList) | 1h | User recommendations |
| `recs:user:{user_id}:{model}` | JSON (RecList) | 1h | Model-specific recs |
| `trending:{list_name}` | JSON (BookList) | 7d | NYT bestsellers |
| `user:session:{token_hash}` | JSON (Session) | 24h | Session data |
| `rate_limit:{ip}:{endpoint}` | Integer | 1m | Rate limit counter |
| `user:library:{user_id}` | JSON (List) | 5m | User's library cache |

### Redis Data Examples

**Book Cache:**
```
Key: book:550e8400-e29b-41d4-a716-446655440000
Type: String (JSON)
TTL: 86400 (24 hours)
Value: {
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Sapiens",
  "authors": ["Yuval Noah Harari"],
  ...
}
```

**Search Cache:**
```
Key: search:sapiens
Type: String (JSON)
TTL: 1800 (30 minutes)
Value: {
  "query": "sapiens",
  "totalCount": 42,
  "results": [...]
}
```

**Rate Limit:**
```
Key: rate_limit:192.168.1.1:/api/v1/search
Type: Integer
TTL: 60
Value: 15  # Number of requests in current minute
```

### Cache Invalidation Events

| Event | Keys Invalidated |
|-------|------------------|
| New rating | `recs:user:{user_id}*`, `user:library:{user_id}` |
| Book update | `book:{book_id}`, `book:external:*` (if match) |
| User update | `user:session:{token}` |
| Trending refresh | `trending:*` |

---

## 🤖 ML Feature Schemas

### Content-Based Features (TF-IDF Input)

```python
# ml/schemas.py
from pydantic import BaseModel
from typing import List, Dict


class BookFeatureVector(BaseModel):
    """Book representation for content-based ML."""
    book_id: str
    text_content: str  # Combined: title + authors + description + genres
    genres: List[str]
    published_year: int
    language: str
    

class TFIDFVector(BaseModel):
    """Sparse TF-IDF vector."""
    book_id: str
    vector: Dict[int, float]  # {feature_index: tfidf_score}
    magnitude: float  # For cosine similarity
```

### Collaborative Filtering Features (KNN Input)

```python
class UserItemInteraction(BaseModel):
    """One user-book interaction."""
    user_id: str
    book_id: str
    rating: float  # Normalized to 0-1
    timestamp: str


class UserRatingVector(BaseModel):
    """User's rating history as sparse vector."""
    user_id: str
    ratings: Dict[str, float]  # {book_id: rating}
    mean_rating: float
    rating_count: int
```

### Neural Recommender Features

```python
class NeuralCFInput(BaseModel):
    """Input to neural collaborative filter."""
    user_id: str
    book_id: str
    user_embedding: List[float]  # 50-dim vector
    book_embedding: List[float]  # 50-dim vector


class NeuralCFOutput(BaseModel):
    """Predicted rating."""
    user_id: str
    book_id: str
    predicted_rating: float  # 0-1 (sigmoid output)
    confidence: float
```

### User Clustering Features

```python
class UserClusterFeatures(BaseModel):
    """Features for KMeans user clustering."""
    user_id: str
    avg_rating: float
    rating_count: int
    genre_distribution: Dict[str, float]  # {"fiction": 0.4, ...}
    reading_pace: float  # books per month
    diversity_score: float  # 0-1
    

class UserCluster(BaseModel):
    """Cluster assignment."""
    user_id: str
    cluster_id: int  # 0-9 (K=10 clusters)
    cluster_label: str  # e.g., "Contemplative Explorer"
    distance_to_center: float
```

### Sentiment Analysis Schema

```python
class SentimentInput(BaseModel):
    """Text to analyze."""
    text: str
    text_type: str  # 'review', 'description'


class SentimentOutput(BaseModel):
    """Sentiment analysis result."""
    polarity: float  # -1 to 1
    subjectivity: float  # 0 to 1
    sentiment_label: str  # 'positive', 'neutral', 'negative'
    confidence: float
    top_emotions: List[str]  # ['joyful', 'thoughtful']
```

---

## 📝 Sample Data

### Sample User

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "priya@example.com",
  "password_hash": "$2b$12$KIXxPfnK...",
  "name": "Priya Sharma",
  "avatar_url": "https://api.dicebear.com/7.x/avataaars/svg?seed=priya",
  "bio": "Avid reader, tea enthusiast",
  "onboarding_completed": true,
  "is_active": true,
  "email_verified": false,
  "last_login_at": "2025-01-15T10:30:00Z",
  "created_at": "2025-01-10T14:22:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

### Sample Book

```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "external_id": "FmyBAwAAQBAJ",
  "external_source": "google_books",
  "title": "Sapiens",
  "subtitle": "A Brief History of Humankind",
  "authors": ["Yuval Noah Harari"],
  "description": "From a renowned historian comes a groundbreaking narrative of humanity's creation and evolution...",
  "genres": ["Non-fiction", "History", "Anthropology", "Science"],
  "tags": ["philosophy", "evolution"],
  "isbn_10": "0062316095",
  "isbn_13": "9780062316097",
  "published_year": 2014,
  "publisher": "Harper",
  "page_count": 464,
  "language": "en",
  "cover_url": "https://books.google.com/books/content?id=FmyBAwAAQBAJ&printsec=frontcover&img=1&zoom=1",
  "cover_url_large": "https://books.google.com/books/content?id=FmyBAwAAQBAJ&printsec=frontcover&img=1&zoom=2",
  "average_rating": 4.5,
  "ratings_count": 15234,
  "kitabee_rating": 4.6,
  "kitabee_ratings_count": 42,
  "metadata": {
    "google_books": {
      "preview_link": "https://books.google.com/books?id=FmyBAwAAQBAJ",
      "info_link": "https://books.google.com/books?id=FmyBAwAAQBAJ"
    }
  },
  "cached_at": "2025-01-15T10:00:00Z",
  "created_at": "2025-01-15T10:00:00Z",
  "updated_at": "2025-01-15T10:00:00Z"
}
```

### Sample Rating

```json
{
  "id": "770e8400-e29b-41d4-a716-446655440002",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "book_id": "660e8400-e29b-41d4-a716-446655440001",
  "rating": 5,
  "review_text": "Absolutely mind-blowing! Changed how I think about humanity and history.",
  "review_title": "A must-read for everyone",
  "is_spoiler": false,
  "helpful_count": 12,
  "created_at": "2025-01-14T18:45:00Z",
  "updated_at": "2025-01-14T18:45:00Z"
}
```

### Sample Library Entry

```json
{
  "id": "880e8400-e29b-41d4-a716-446655440003",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "book_id": "660e8400-e29b-41d4-a716-446655440001",
  "status": "read",
  "current_page": 464,
  "total_pages": 464,
  "started_reading_at": "2024-12-20T09:00:00Z",
  "finished_reading_at": "2025-01-05T22:30:00Z",
  "notes": "Great historical perspective on humanity",
  "is_favorite": true,
  "added_at": "2024-12-15T14:00:00Z",
  "updated_at": "2025-01-05T22:30:00Z"
}
```

### Sample Recommendation

```json
{
  "id": "990e8400-e29b-41d4-a716-446655440004",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "book_id": "aa0e8400-e29b-41d4-a716-446655440005",
  "score": 0.92543,
  "rank": 1,
  "model_type": "hybrid",
  "explanation": "Based on your love for Sapiens and 87% of similar readers enjoyed this",
  "metadata": {
    "based_on_books": ["660e8400-e29b-41d4-a716-446655440001"],
    "similar_users_count": 156,
    "content_score": 0.89,
    "collaborative_score": 0.94,
    "neural_score": 0.93
  },
  "generated_at": "2025-01-15T10:00:00Z",
  "expires_at": "2025-01-15T11:00:00Z"
}
```

---

## 🚚 Migration Strategy

### Tool: Alembic

**Location:** `backend/alembic/versions/`

### Migration Workflow

```bash
# 1. Modify SQLAlchemy models
# Edit: backend/src/database/models/user.py

# 2. Generate migration
cd backend
alembic revision --autogenerate -m "add email_verified field to users"

# 3. Review generated file (IMPORTANT!)
# Edit: alembic/versions/xxx_add_email_verified.py

# 4. Apply migration
alembic upgrade head

# 5. Verify
alembic current
```

### Migration File Naming

Format: `{timestamp}_{description}.py`

Example: `20250115_1030_add_email_verified_to_users.py`

### Rollback Strategy

```bash
# Rollback last migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# View history
alembic history
```

### Safe Migration Practices

**✅ DO:**
- Add nullable columns first, backfill data, then set NOT NULL
- Add indexes CONCURRENTLY on large tables
- Test migrations on staging before production
- Keep migrations backwards-compatible when possible

**❌ DON'T:**
- Drop columns without a deprecation period
- Rename columns in a single migration (create new, migrate data, drop old)
- Run heavy DML in migrations (use background jobs)

---

## 🔄 Schema Evolution

### Version Compatibility

| Version | Status | Changes |
|---------|--------|---------|
| **v1.0** | 🟢 Current | Initial schema |
| **v1.1** | 📅 Planned | Add reading_challenges table |
| **v2.0** | 🔮 Future | Add social features (follows, feed) |

### Backward Compatibility Rules

1. **Additive changes = safe** (new columns, tables, indexes)
2. **Deprecation = 30 days minimum** before removal
3. **Breaking changes = major version bump** (v1 → v2)

### Deprecated Field Marker

When deprecating:
```python
# schemas/user.py
class UserResponse(BaseModel):
    # ...
    old_field: Optional[str] = Field(
        None,
        deprecated=True,
        description="Deprecated: Use new_field instead. Will be removed in v2.0"
    )
    new_field: Optional[str] = None
```

---

## 🔒 Data Privacy & Security

### Sensitive Data Classification

| Field | Classification | Handling |
|-------|---------------|----------|
| `password_hash` | 🔴 Critical | Never in logs, API responses |
| `email` | 🟡 Sensitive | Encrypted at rest, HTTPS only |
| `date_of_birth` | 🟡 Sensitive | Not exposed publicly |
| `ratings` | 🟢 Semi-public | Aggregated for others |
| `library` | 🟢 Semi-public | Optional public sharing |
| `search_history` | 🟡 Sensitive | Anonymized after 90 days |

### PII (Personally Identifiable Information)

Stored PII:
- Email
- Name
- Date of birth (optional)
- Avatar URL

**Retention:**
- Active accounts: Indefinitely (with consent)
- Deleted accounts: 30 days soft delete, then hard delete
- Search history: 90 days rolling

### Data Export (GDPR Compliance)

User can request full data export via:
- Endpoint: `GET /api/v1/users/me/export`
- Format: JSON zip file
- Contents: All user data (profile, ratings, library, preferences)

### Data Deletion

User can request account deletion via:
- Endpoint: `DELETE /api/v1/users/me`
- Effect: Soft delete for 30 days, then hard delete
- Cascade: All ratings, library, recommendations deleted

### Encryption

- **At rest:** PostgreSQL disk encryption (AWS RDS default)
- **In transit:** TLS 1.3 (HTTPS only)
- **Passwords:** bcrypt with cost factor 12
- **JWT tokens:** HS256 signed with 256-bit secret

---

## 📎 Appendix

### Related Documents

- [PRD.md](./PRD.md) — Product requirements
- [TECHSPEC.md](./TECHSPEC.md) — Technical specification
- [APPFLOW.md](./APPFLOW.md) — User flows
- [API_DESIGN.md](./API_DESIGN.md) — API endpoints (coming)

### Type Generation Tools

**Backend → OpenAPI:**
```bash
# FastAPI auto-generates at /openapi.json
```

**OpenAPI → TypeScript:**
```bash
npx openapi-typescript http://localhost:8000/openapi.json -o types/api-generated.ts
```

### Database Tools

**GUI Clients:**
- [pgAdmin](https://www.pgadmin.org/) (Official)
- [DBeaver](https://dbeaver.io/) (Universal)
- [TablePlus](https://tableplus.com/) (Modern)

**CLI:**
```bash
# Connect to Kitabee DB
docker exec -it kitabee_postgres psql -U kitabee_user -d kitabee_db

# Common queries
\dt              -- List tables
\d users         -- Describe table
\di              -- List indexes
```

### Glossary

- **CASCADE:** Auto-delete related rows when parent deleted
- **DDL:** Data Definition Language (CREATE, ALTER, DROP)
- **DML:** Data Manipulation Language (INSERT, UPDATE, DELETE)
- **ER:** Entity Relationship
- **GIN Index:** Generalized Inverted Index (for arrays, JSON)
- **JSONB:** Binary JSON (indexable, faster than JSON in Postgres)
- **PII:** Personally Identifiable Information
- **UUID:** Universally Unique Identifier
- **TTL:** Time To Live (cache expiration)

### Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Today] | [Your Name] | Initial schema documentation |

---

**End of Schema Document** 🗄️

*"The schema is the contract. Break it, break the app."*