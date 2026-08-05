---
# 🗄️ Kitabee — Data Schema Document

> **Document Version:** 2.0
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
   - [4.1 Users Table](#41-users-table) ✅ Built
   - [4.2 Books Table](#42-books-table) ✅ Built
   - [4.3 Ratings Table](#43-ratings-table) ✅ Built
   - [4.4 Library Table](#44-library-table) ✅ Built
   - [4.5 Recommendations Table](#45-recommendations-table) ✅ Built
   - [4.6 User Preferences Table](#46-user-preferences-table) ✅ Built
   - [4.7 Search History Table](#47-search-history-table) ✅ Built
   - [4.8 Comics Table](#48-comics-table) 🆕 Week 3
   - [4.9 Comic Ratings Table](#49-comic-ratings-table) 🆕 Week 3
   - [4.10 Comic Library Table](#410-comic-library-table) 🆕 Week 3
   - [4.11 Collections Table](#411-collections-table) 🆕 Week 3
   - [4.12 User Collections Table](#412-user-collections-table) 🆕 Week 3
   - [4.13 Reading Progress Table](#413-reading-progress-table) 🆕 Week 3
   - [4.14 Series Metadata Table](#414-series-metadata-table) 🆕 Week 3
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
This document is the **single source of truth** for every data structure in Kitabee. If it is not documented here, it does not exist.

### What Changed in v2.0
Kitabee now supports books + comics, Netflix-style themed collections, series reading order guides, and free reading via Internet Archive. This required 7 new tables:

- **comics** — Comic metadata (parallel to books)
- **comic_ratings** — Ratings on comics
- **comic_library_items** — Comics in user library
- **collections** — Themed rows curated by ML
- **user_collections** — Per-user collection ranking
- **reading_progress** — Track reading position for free content
- **series_metadata** — Cached series reading order data

### Scope
- ✅ PostgreSQL database schema (books + comics + collections + reading)
- ✅ Pydantic models (backend validation)
- ✅ TypeScript interfaces (frontend types)
- ✅ Redis cache key patterns
- ✅ External API response shapes (Google Books, Comic Vine, Internet Archive)
- ✅ ML model input/output structures
- ✅ Sample data for testing

### Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| **Table names** | `snake_case`, plural | `users`, `ratings`, `comics` |
| **Column names** | `snake_case` | `user_id`, `created_at` |
| **Primary keys** | `id` (UUID) | `id UUID PRIMARY KEY` |
| **Foreign keys** | `<entity>_id` | `user_id`, `book_id`, `comic_id` |
| **Timestamps** | `<action>_at` | `created_at`, `updated_at` |
| **Booleans** | `is_<state>` or `has_<thing>` | `is_active`, `has_completed` |
| **Enums** | `snake_case` values | `'want_to_read'`, `'main'` |
| **Indexes** | `idx_<table>_<columns>` | `idx_ratings_user_book` |
| **Constraints** | `<table>_<column>_<type>` | `users_email_unique` |

---

## 🎨 Design Principles

### 1. UUIDs Over Auto-Increment
- ✅ Prevents enumeration attacks
- ✅ Client-side generation possible
- ✅ Distributed systems safe

### 2. Timestamps Everywhere
Every table has `created_at` and `updated_at`.

### 3. Soft Deletes (Where Appropriate)
User accounts use `deleted_at`. Ratings/library are hard-deleted for privacy.

### 4. JSONB for Flexible Fields
Used for preferences, metadata, ML feature vectors, collection items list.

### 5. Explicit Over Implicit
Every column has a comment. Every relationship has a foreign key.

### 6. Denormalization for Performance
Some fields duplicated for query speed (`books.average_rating`, `books.ratings_count`).

### 7. Content-Type Symmetry (New in v2.0)
Books and comics are separate tables but share nearly identical schema. This makes ML and services content-type-agnostic while keeping SQL clean.

### 8. Cached ML Outputs
Collections, series metadata, and recommendations are all cached in DB (not just Redis) so they survive restarts and can be inspected.

---

## 🔗 Entity Relationship Diagram

### High-Level ER Diagram

```
┌─────────────────┐
│     USERS       │
│                 │
│ id (PK)         │◄──────────────┬──────────────┬──────────────┐
│ email           │               │              │              │
│ password_hash   │               │              │              │
│ name            │               │              │              │
│ preferences     │               │              │              │
│ created_at      │               │              │              │
└─────────────────┘               │              │              │
        │                         │              │              │
        │ 1:N                     │              │              │
        ▼                         │              │              │
┌─────────────────┐               │              │              │
│    RATINGS      │               │              │              │
│                 │               │              │              │
│ user_id (FK)────┘               │              │              │
│ book_id (FK)────┐               │              │              │
└─────────────────┘               │              │              │
                                  │              │              │
┌─────────────────┐               │              │              │
│     BOOKS       │◄──────────────┤              │              │
│                 │               │              │              │
│ id (PK)         │               │              │              │
│ external_id     │               │              │              │
│ title           │               │              │              │
│ series_name     │               │              │              │
│ series_order    │               │              │              │
└─────────────────┘               │              │              │
        │                         │              │              │
        │ 1:N                     │              │              │
        ▼                         │              │              │
┌─────────────────┐               │              │              │
│    LIBRARY      │               │              │              │
│ user_id (FK)────┘               │              │              │
└─────────────────┘               │              │              │
                                  │              │              │
                                  │              │              │
┌─────────────────┐               │              │              │
│     COMICS      │◄──────────────┼──────────────┤              │
│  🆕 v2.0        │               │              │              │
│ id (PK)         │               │              │              │
│ external_id     │ (Comic Vine)  │              │              │
│ title           │               │              │              │
│ series_name     │               │              │              │
│ issue_number    │               │              │              │
│ is_free_online  │               │              │              │
└─────────────────┘               │              │              │
        │                         │              │              │
        │ 1:N                     │              │              │
        ▼                         │              │              │
┌─────────────────┐               │              │              │
│ COMIC_RATINGS   │               │              │              │
│  🆕 v2.0        │               │              │              │
│ user_id (FK)────┤               │              │              │
│ comic_id (FK)   │               │              │              │
└─────────────────┘               │              │              │
                                  │              │              │
┌────────────────────┐            │              │              │
│ COMIC_LIBRARY_ITEMS│            │              │              │
│  🆕 v2.0           │            │              │              │
│ user_id (FK)───────┘            │              │              │
│ comic_id (FK)                   │              │              │
└────────────────────┘            │              │              │
                                  │              │              │
┌─────────────────┐               │              │              │
│  COLLECTIONS    │               │              │              │
│  🆕 v2.0        │               │              │              │
│ id (PK)         │               │              │              │
│ name            │               │              │              │
│ title           │               │              │              │
│ collection_type │               │              │              │
│ items_json      │               │              │              │
│ generated_at    │               │              │              │
└─────────────────┘               │              │              │
        │                         │              │              │
        │ N:M                     │              │              │
        ▼                         │              │              │
┌──────────────────┐              │              │              │
│ USER_COLLECTIONS │              │              │              │
│  🆕 v2.0         │              │              │              │
│ user_id (FK)─────┘              │              │              │
│ collection_id    │              │              │              │
│ rank             │              │              │              │
└──────────────────┘              │              │              │
                                  │              │              │
┌──────────────────┐              │              │              │
│ READING_PROGRESS │              │              │              │
│  🆕 v2.0         │              │              │              │
│ user_id (FK)─────┘              │              │              │
│ content_id       │              │              │              │
│ content_type     │              │              │              │
│ progress_percent │              │              │              │
└──────────────────┘              │              │              │
                                  │              │              │
┌──────────────────┐              │              │              │
│ SERIES_METADATA  │              │              │              │
│  🆕 v2.0         │              │              │              │
│ series_name      │              │              │              │
│ content_type     │              │              │              │
│ ordered_items    │              │              │              │
│ tips             │              │              │              │
└──────────────────┘              │              │              │

┌─────────────────┐               │              │              │
│RECOMMENDATIONS  │               │              │              │
│ user_id (FK)────┘               │              │              │
│ book_id (FK)                    │              │              │
│ model_type                      │              │              │
└─────────────────┘               │              │              │

┌─────────────────┐               │              │              │
│USER_PREFERENCES │               │              │              │
│ user_id (FK)────────────────────┘              │              │
│ content_type_preference (NEW)   │              │              │
└─────────────────┘               │              │              │

┌─────────────────┐               │              │              │
│SEARCH_HISTORY   │               │              │              │
│ user_id (FK)────────────────────────────────────┘              │
│ content_type_filter (NEW)       │              │              │
└─────────────────┘               │              │              │
```

### Relationship Summary

| From | To | Type | Cascade |
|------|-----|------|---------|
| Users → Ratings | 1:N | ON DELETE CASCADE |
| Users → Library | 1:N | ON DELETE CASCADE |
| Users → ComicRatings | 1:N | ON DELETE CASCADE |
| Users → ComicLibrary | 1:N | ON DELETE CASCADE |
| Users → UserCollections | 1:N | ON DELETE CASCADE |
| Users → ReadingProgress | 1:N | ON DELETE CASCADE |
| Users → Recommendations | 1:N | ON DELETE CASCADE |
| Users → SearchHistory | 1:N | ON DELETE CASCADE |
| Books → Ratings | 1:N | ON DELETE CASCADE |
| Books → Library | 1:N | ON DELETE CASCADE |
| Books → Recommendations | 1:N | ON DELETE CASCADE |
| Comics → ComicRatings | 1:N | ON DELETE CASCADE |
| Comics → ComicLibrary | 1:N | ON DELETE CASCADE |
| Collections → UserCollections | 1:N | ON DELETE CASCADE |

---

## 🗄️ Database Schema (PostgreSQL)

### 4.1 Users Table ✅ Built (Days 1-14)

**Purpose:** Store user accounts and authentication data.

*[Unchanged from v1.0 — already built and in production]*

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
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    email_verified BOOLEAN NOT NULL DEFAULT FALSE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT users_email_unique UNIQUE (email),
    CONSTRAINT users_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    CONSTRAINT users_name_length CHECK (LENGTH(name) BETWEEN 2 AND 100)
);

CREATE UNIQUE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_created_at ON users(created_at);
CREATE INDEX idx_users_last_login ON users(last_login_at);
```

---

### 4.2 Books Table ✅ Built (Updated v2.0)

**Purpose:** Cache book metadata from external APIs. Now includes series and free-reading fields.

**Changes in v2.0:**
- Added `series_name`, `series_order`, `series_entry_type` (for series intelligence)
- Added `is_free_online`, `internet_archive_id`, `free_epub_url` (for free reading)

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
    kitabee_rating DECIMAL(3,2),
    kitabee_ratings_count INTEGER DEFAULT 0,

    -- Series intelligence fields (v2.0)
    series_name VARCHAR(300),
    series_order INTEGER,
    series_entry_type VARCHAR(20),  -- 'main' | 'prequel' | 'spinoff' | 'companion'

    -- Free reading fields (v2.0)
    is_free_online BOOLEAN NOT NULL DEFAULT FALSE,
    internet_archive_id VARCHAR(200),
    free_epub_url TEXT,
    free_pdf_url TEXT,

    -- ML mood tag (v2.0, populated by mood_detector)
    mood_tags TEXT[] DEFAULT '{}',

    metadata JSONB DEFAULT '{}',
    cached_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT books_external_unique UNIQUE (external_source, external_id),
    CONSTRAINT books_rating_range CHECK (average_rating BETWEEN 0 AND 5),
    CONSTRAINT books_page_count_positive CHECK (page_count > 0 OR page_count IS NULL),
    CONSTRAINT books_year_valid CHECK (published_year BETWEEN 1000 AND EXTRACT(YEAR FROM CURRENT_DATE) + 1),
    CONSTRAINT books_series_entry_type CHECK (series_entry_type IN ('main', 'prequel', 'spinoff', 'companion') OR series_entry_type IS NULL)
);

-- Existing indexes
CREATE INDEX idx_books_external ON books(external_source, external_id);
CREATE INDEX idx_books_isbn_13 ON books(isbn_13) WHERE isbn_13 IS NOT NULL;
CREATE INDEX idx_books_title_gin ON books USING GIN(to_tsvector('english', title));
CREATE INDEX idx_books_authors_gin ON books USING GIN(authors);
CREATE INDEX idx_books_genres_gin ON books USING GIN(genres);
CREATE INDEX idx_books_avg_rating ON books(average_rating DESC);
CREATE INDEX idx_books_cached_at ON books(cached_at);

-- New indexes v2.0
CREATE INDEX idx_books_series ON books(series_name, series_order) WHERE series_name IS NOT NULL;
CREATE INDEX idx_books_free_online ON books(is_free_online) WHERE is_free_online = TRUE;
CREATE INDEX idx_books_mood_tags_gin ON books USING GIN(mood_tags);
```

---

### 4.3 Ratings Table ✅ Built

*[Unchanged from v1.0]*

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

CREATE INDEX idx_ratings_user_id ON ratings(user_id);
CREATE INDEX idx_ratings_book_id ON ratings(book_id);
CREATE INDEX idx_ratings_user_book ON ratings(user_id, book_id);
CREATE INDEX idx_ratings_rating ON ratings(rating);
CREATE INDEX idx_ratings_created_at ON ratings(created_at DESC);
```

---

### 4.4 Library Table ✅ Built

*[Unchanged from v1.0. Note: this is `library_items` in the actual codebase.]*

```sql
CREATE TYPE library_status_enum AS ENUM (
    'want_to_read',
    'currently_reading',
    'read',
    'dnf'
);

CREATE TABLE library_items (
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

CREATE INDEX idx_library_user_id ON library_items(user_id);
CREATE INDEX idx_library_book_id ON library_items(book_id);
CREATE INDEX idx_library_user_status ON library_items(user_id, status);
CREATE INDEX idx_library_added_at ON library_items(added_at DESC);
```

---

### 4.5 Recommendations Table ✅ Built (Updated v2.0)

**Purpose:** Cache ML-generated recommendations.

**Changes in v2.0:**
- Added `content_id` polymorphic reference and `content_type` (recommendations work for books AND comics)

```sql
CREATE TYPE recommendation_model_enum AS ENUM (
    'content_based',
    'collaborative_knn',
    'neural_cf',
    'hybrid',
    'trending',
    'popular'
);

CREATE TYPE content_type_enum AS ENUM ('book', 'comic');

CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    book_id UUID REFERENCES books(id) ON DELETE CASCADE,
    comic_id UUID REFERENCES comics(id) ON DELETE CASCADE,
    content_type content_type_enum NOT NULL DEFAULT 'book',
    score DECIMAL(6,5) NOT NULL,
    rank INTEGER NOT NULL,
    model_type recommendation_model_enum NOT NULL,
    explanation TEXT,
    metadata JSONB DEFAULT '{}',
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '1 hour'),

    CONSTRAINT recommendations_score_range CHECK (score BETWEEN 0 AND 1),
    CONSTRAINT recommendations_rank_positive CHECK (rank > 0),
    CONSTRAINT recommendations_content_ref CHECK (
        (content_type = 'book' AND book_id IS NOT NULL AND comic_id IS NULL) OR
        (content_type = 'comic' AND comic_id IS NOT NULL AND book_id IS NULL)
    )
);

CREATE INDEX idx_recommendations_user_rank ON recommendations(user_id, rank);
CREATE INDEX idx_recommendations_user_score ON recommendations(user_id, score DESC);
CREATE INDEX idx_recommendations_expires ON recommendations(expires_at);
CREATE INDEX idx_recommendations_model ON recommendations(model_type);
CREATE INDEX idx_recommendations_content_type ON recommendations(content_type);
```

---

### 4.6 User Preferences Table ✅ Built (Updated v2.0)

**Purpose:** Store extended user preferences.

**Changes in v2.0:**
- Added `content_type_preference` (books/comics/both)

```sql
CREATE TYPE content_preference_enum AS ENUM ('books', 'comics', 'both');

CREATE TABLE user_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    favorite_genres TEXT[] NOT NULL DEFAULT '{}',
    preferred_languages TEXT[] NOT NULL DEFAULT '{en}',
    excluded_genres TEXT[] DEFAULT '{}',
    content_warnings_hide TEXT[] DEFAULT '{}',
    reading_pace VARCHAR(20) DEFAULT 'medium',
    preferred_book_length VARCHAR(20) DEFAULT 'any',
    content_type_preference content_preference_enum NOT NULL DEFAULT 'both',  -- NEW v2.0
    theme VARCHAR(20) NOT NULL DEFAULT 'system',
    notification_settings JSONB NOT NULL DEFAULT '{"email": false, "push": false}',
    privacy_settings JSONB NOT NULL DEFAULT '{"public_library": false, "public_ratings": false}',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT user_preferences_user_unique UNIQUE (user_id),
    CONSTRAINT user_preferences_theme_valid CHECK (theme IN ('light', 'dark', 'system')),
    CONSTRAINT user_preferences_pace_valid CHECK (reading_pace IN ('slow', 'medium', 'fast'))
);

CREATE INDEX idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX idx_user_preferences_genres_gin ON user_preferences USING GIN(favorite_genres);
CREATE INDEX idx_user_preferences_content_type ON user_preferences(content_type_preference);
```

---

### 4.7 Search History Table ✅ Built (Updated v2.0)

**Changes in v2.0:**
- Added `content_type_filter` (which tab was active when searched)

```sql
CREATE TABLE search_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    query VARCHAR(500) NOT NULL,
    normalized_query VARCHAR(500) NOT NULL,
    content_type_filter VARCHAR(20) DEFAULT 'all',  -- NEW v2.0: 'all' | 'books' | 'comics'
    results_count INTEGER NOT NULL DEFAULT 0,
    clicked_book_id UUID REFERENCES books(id) ON DELETE SET NULL,
    clicked_comic_id UUID REFERENCES comics(id) ON DELETE SET NULL,  -- NEW v2.0
    session_id VARCHAR(100),
    device_type VARCHAR(20),
    searched_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT search_history_query_not_empty CHECK (LENGTH(TRIM(query)) > 0)
);

CREATE INDEX idx_search_history_user_id ON search_history(user_id);
CREATE INDEX idx_search_history_searched_at ON search_history(searched_at DESC);
CREATE INDEX idx_search_history_normalized ON search_history(normalized_query);
```

---

### 4.8 Comics Table 🆕 (Week 3)

**Purpose:** Cache comic metadata from Comic Vine and Internet Archive.

**SQL Definition:**

```sql
CREATE TABLE comics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    external_id VARCHAR(100) NOT NULL,
    external_source VARCHAR(50) NOT NULL DEFAULT 'comic_vine',
    title VARCHAR(500) NOT NULL,
    creators TEXT[] NOT NULL DEFAULT '{}',  -- writers + artists combined
    publisher VARCHAR(200),
    description TEXT,
    genres TEXT[] NOT NULL DEFAULT '{}',
    characters TEXT[] DEFAULT '{}',  -- Batman, Superman, Wolverine etc.
    tags TEXT[] DEFAULT '{}',
    published_year INTEGER,
    page_count INTEGER,
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    cover_url TEXT,
    cover_url_large TEXT,

    -- Series info (comics almost always in series)
    series_name VARCHAR(300),
    issue_number INTEGER,
    volume_number INTEGER,
    series_entry_type VARCHAR(20),  -- 'main' | 'annual' | 'oneshot' | 'special'

    -- Ratings (aggregated from comic_ratings table)
    average_rating DECIMAL(3,2) DEFAULT 0.00,
    ratings_count INTEGER DEFAULT 0,
    kitabee_rating DECIMAL(3,2),
    kitabee_ratings_count INTEGER DEFAULT 0,

    -- Free reading fields
    is_free_online BOOLEAN NOT NULL DEFAULT FALSE,
    internet_archive_id VARCHAR(200),
    free_image_urls TEXT[],  -- Array of page image URLs
    free_pdf_url TEXT,

    -- ML mood tag
    mood_tags TEXT[] DEFAULT '{}',

    metadata JSONB DEFAULT '{}',
    cached_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT comics_external_unique UNIQUE (external_source, external_id),
    CONSTRAINT comics_rating_range CHECK (average_rating BETWEEN 0 AND 5),
    CONSTRAINT comics_page_count_positive CHECK (page_count > 0 OR page_count IS NULL),
    CONSTRAINT comics_year_valid CHECK (published_year BETWEEN 1900 AND EXTRACT(YEAR FROM CURRENT_DATE) + 1),
    CONSTRAINT comics_entry_type CHECK (series_entry_type IN ('main', 'annual', 'oneshot', 'special') OR series_entry_type IS NULL)
);

COMMENT ON TABLE comics IS 'Comic metadata cached from Comic Vine + Internet Archive';
COMMENT ON COLUMN comics.creators IS 'Combined writers and artists';
COMMENT ON COLUMN comics.characters IS 'Featured characters (Batman, Wolverine, etc.)';
COMMENT ON COLUMN comics.is_free_online IS 'True if readable free via Internet Archive';
COMMENT ON COLUMN comics.free_image_urls IS 'Array of page image URLs for in-app reader';

-- Indexes
CREATE INDEX idx_comics_external ON comics(external_source, external_id);
CREATE INDEX idx_comics_title_gin ON comics USING GIN(to_tsvector('english', title));
CREATE INDEX idx_comics_creators_gin ON comics USING GIN(creators);
CREATE INDEX idx_comics_characters_gin ON comics USING GIN(characters);
CREATE INDEX idx_comics_genres_gin ON comics USING GIN(genres);
CREATE INDEX idx_comics_series ON comics(series_name, issue_number) WHERE series_name IS NOT NULL;
CREATE INDEX idx_comics_free_online ON comics(is_free_online) WHERE is_free_online = TRUE;
CREATE INDEX idx_comics_publisher ON comics(publisher);
CREATE INDEX idx_comics_avg_rating ON comics(average_rating DESC);
CREATE INDEX idx_comics_mood_tags_gin ON comics USING GIN(mood_tags);
```

---

### 4.9 Comic Ratings Table 🆕 (Week 3)

**Purpose:** User ratings and reviews for comics.

```sql
CREATE TABLE comic_ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    comic_id UUID NOT NULL REFERENCES comics(id) ON DELETE CASCADE,
    rating SMALLINT NOT NULL,
    review_text TEXT,
    review_title VARCHAR(200),
    is_spoiler BOOLEAN NOT NULL DEFAULT FALSE,
    helpful_count INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT comic_ratings_user_comic_unique UNIQUE (user_id, comic_id),
    CONSTRAINT comic_ratings_value_range CHECK (rating BETWEEN 1 AND 5),
    CONSTRAINT comic_ratings_review_length CHECK (LENGTH(review_text) <= 5000)
);

CREATE INDEX idx_comic_ratings_user_id ON comic_ratings(user_id);
CREATE INDEX idx_comic_ratings_comic_id ON comic_ratings(comic_id);
CREATE INDEX idx_comic_ratings_user_comic ON comic_ratings(user_id, comic_id);
CREATE INDEX idx_comic_ratings_rating ON comic_ratings(rating);
CREATE INDEX idx_comic_ratings_created_at ON comic_ratings(created_at DESC);
```

---

### 4.10 Comic Library Table 🆕 (Week 3)

**Purpose:** User's comic collection (parallel to library_items for books).

```sql
CREATE TABLE comic_library_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    comic_id UUID NOT NULL REFERENCES comics(id) ON DELETE CASCADE,
    status library_status_enum NOT NULL DEFAULT 'want_to_read',
    current_page INTEGER DEFAULT 0,
    total_pages INTEGER,
    started_reading_at TIMESTAMP WITH TIME ZONE,
    finished_reading_at TIMESTAMP WITH TIME ZONE,
    notes TEXT,
    is_favorite BOOLEAN NOT NULL DEFAULT FALSE,
    added_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT comic_library_user_comic_unique UNIQUE (user_id, comic_id),
    CONSTRAINT comic_library_page_valid CHECK (current_page >= 0 AND (total_pages IS NULL OR current_page <= total_pages))
);

CREATE INDEX idx_comic_library_user_id ON comic_library_items(user_id);
CREATE INDEX idx_comic_library_comic_id ON comic_library_items(comic_id);
CREATE INDEX idx_comic_library_user_status ON comic_library_items(user_id, status);
CREATE INDEX idx_comic_library_added_at ON comic_library_items(added_at DESC);
```

---

### 4.11 Collections Table 🆕 (Week 3)

**Purpose:** Netflix-style themed collections generated by ML. Each row on the home screen corresponds to one collection.

```sql
CREATE TYPE collection_type_enum AS ENUM (
    'personalized',    -- "Because you loved X..."
    'mood',            -- "Dark But You Cannot Put It Down"
    'utility',         -- "Complete Series — Read in Order"
    'trending',        -- "Everyone Is Reading This"
    'free_reading',    -- "Free to Read Right Now"
    'series',          -- Auto-generated series row
    'author',          -- "From the Mind of X"
    'genre'            -- "Best of Sci-Fi This Year"
);

CREATE TABLE collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(200) NOT NULL,  -- internal name: "epic_fantasy_cluster_3"
    title VARCHAR(300) NOT NULL,  -- display title: "Epic Worlds Built From Scratch"
    description TEXT,
    collection_type collection_type_enum NOT NULL,
    content_type VARCHAR(20) NOT NULL DEFAULT 'mixed',  -- 'books' | 'comics' | 'mixed'
    mood VARCHAR(50),  -- 'dark', 'funny', 'epic', etc. (nullable)

    -- Items in this collection (denormalized for fast reads)
    items_json JSONB NOT NULL DEFAULT '[]',
    -- Example items_json:
    -- [
    --   {"content_type": "book", "id": "uuid1", "position": 1},
    --   {"content_type": "comic", "id": "uuid2", "position": 2},
    --   ...
    -- ]

    item_count INTEGER NOT NULL DEFAULT 0,

    -- Metadata for personalization
    based_on_book_id UUID REFERENCES books(id) ON DELETE SET NULL,
    based_on_comic_id UUID REFERENCES comics(id) ON DELETE SET NULL,
    based_on_author VARCHAR(200),
    based_on_genre VARCHAR(100),

    -- Freshness tracking
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '6 hours'),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT collections_content_type_valid CHECK (content_type IN ('books', 'comics', 'mixed')),
    CONSTRAINT collections_item_count_positive CHECK (item_count >= 0)
);

COMMENT ON TABLE collections IS 'ML-curated themed rows for Netflix-style home screen';
COMMENT ON COLUMN collections.name IS 'Internal identifier (e.g., epic_fantasy_cluster_3)';
COMMENT ON COLUMN collections.title IS 'Catchy display title shown to user';
COMMENT ON COLUMN collections.items_json IS 'Ordered list of content items with type + id';

CREATE INDEX idx_collections_type ON collections(collection_type);
CREATE INDEX idx_collections_content_type ON collections(content_type);
CREATE INDEX idx_collections_mood ON collections(mood) WHERE mood IS NOT NULL;
CREATE INDEX idx_collections_expires_at ON collections(expires_at);
CREATE INDEX idx_collections_generated_at ON collections(generated_at DESC);
```

---

### 4.12 User Collections Table 🆕 (Week 3)

**Purpose:** Per-user ranking of collections (which rows to show at what position on this user's home screen).

```sql
CREATE TABLE user_collections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    collection_id UUID NOT NULL REFERENCES collections(id) ON DELETE CASCADE,
    rank INTEGER NOT NULL,  -- Row position on home screen (1 = top)
    personalization_score DECIMAL(6,5),  -- 0-1 confidence this user will like this row
    shown_at TIMESTAMP WITH TIME ZONE,  -- Last time actually rendered
    clicked_count INTEGER NOT NULL DEFAULT 0,  -- Engagement tracking
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT user_collections_user_collection_unique UNIQUE (user_id, collection_id),
    CONSTRAINT user_collections_rank_positive CHECK (rank > 0),
    CONSTRAINT user_collections_score_range CHECK (personalization_score BETWEEN 0 AND 1 OR personalization_score IS NULL)
);

CREATE INDEX idx_user_collections_user_rank ON user_collections(user_id, rank);
CREATE INDEX idx_user_collections_collection ON user_collections(collection_id);
```

---

### 4.13 Reading Progress Table 🆕 (Week 3)

**Purpose:** Track user's reading position for free content (EPUB books + comics). Feeds "Continue Reading" row.

```sql
CREATE TABLE reading_progress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    book_id UUID REFERENCES books(id) ON DELETE CASCADE,
    comic_id UUID REFERENCES comics(id) ON DELETE CASCADE,
    content_type content_type_enum NOT NULL,

    -- Progress tracking
    current_position VARCHAR(500),  -- EPUB CFI or page number
    current_page INTEGER,
    total_pages INTEGER,
    progress_percent DECIMAL(5,2) NOT NULL DEFAULT 0.00,  -- 0.00 to 100.00

    -- Session tracking
    last_read_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_reading_time_seconds INTEGER NOT NULL DEFAULT 0,
    session_count INTEGER NOT NULL DEFAULT 0,

    -- Completion
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT reading_progress_content_ref CHECK (
        (content_type = 'book' AND book_id IS NOT NULL AND comic_id IS NULL) OR
        (content_type = 'comic' AND comic_id IS NOT NULL AND book_id IS NULL)
    ),
    CONSTRAINT reading_progress_percent_range CHECK (progress_percent BETWEEN 0 AND 100),
    CONSTRAINT reading_progress_user_book_unique UNIQUE (user_id, book_id),
    CONSTRAINT reading_progress_user_comic_unique UNIQUE (user_id, comic_id)
);

COMMENT ON TABLE reading_progress IS 'Tracks user reading position for free content (EPUB + comics)';
COMMENT ON COLUMN reading_progress.current_position IS 'EPUB CFI location or page number string';
COMMENT ON COLUMN reading_progress.progress_percent IS 'Percentage read (0-100)';

CREATE INDEX idx_reading_progress_user_id ON reading_progress(user_id);
CREATE INDEX idx_reading_progress_user_last_read ON reading_progress(user_id, last_read_at DESC);
CREATE INDEX idx_reading_progress_book_id ON reading_progress(book_id) WHERE book_id IS NOT NULL;
CREATE INDEX idx_reading_progress_comic_id ON reading_progress(comic_id) WHERE comic_id IS NOT NULL;
CREATE INDEX idx_reading_progress_incomplete ON reading_progress(user_id, is_completed) WHERE is_completed = FALSE;
```

---

### 4.14 Series Metadata Table 🆕 (Week 3)

**Purpose:** Cache computed series reading order data. Avoids recomputing series structure every time user visits a book/comic.

```sql
CREATE TABLE series_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    series_name VARCHAR(300) NOT NULL,
    content_type content_type_enum NOT NULL,

    -- Ordered items (denormalized for fast reads)
    ordered_items_json JSONB NOT NULL DEFAULT '[]',
    -- Example:
    -- [
    --   {"id": "uuid1", "title": "Dune", "order": 1, "label": "Start Here"},
    --   {"id": "uuid2", "title": "Dune Messiah", "order": 2, "label": null},
    --   ...
    -- ]

    -- Related series (prequels, spinoffs)
    companion_series_json JSONB DEFAULT '[]',
    -- Example:
    -- [
    --   {
    --     "name": "Prequel Series by Brian Herbert",
    --     "entries": [...],
    --     "tip": "Read after Book 1 or after all 6 originals."
    --   }
    -- ]

    -- Contextual tip for readers
    tip TEXT,

    -- Metadata
    total_items INTEGER NOT NULL DEFAULT 0,
    is_complete BOOLEAN NOT NULL DEFAULT FALSE,  -- Is the series finished?

    -- Cache management
    generated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (CURRENT_TIMESTAMP + INTERVAL '7 days'),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT series_metadata_name_type_unique UNIQUE (series_name, content_type),
    CONSTRAINT series_metadata_total_positive CHECK (total_items >= 0)
);

COMMENT ON TABLE series_metadata IS 'Cached reading order data for series (Series Intelligence output)';
COMMENT ON COLUMN series_metadata.ordered_items_json IS 'Full series in reading order with labels';
COMMENT ON COLUMN series_metadata.companion_series_json IS 'Prequel/spinoff series data';

CREATE INDEX idx_series_metadata_name ON series_metadata(series_name);
CREATE INDEX idx_series_metadata_content_type ON series_metadata(content_type);
CREATE INDEX idx_series_metadata_expires ON series_metadata(expires_at);
```

---

## 📋 Enumerations

### All Enums Summary

| Enum | Values | Used In |
|------|--------|---------|
| `library_status_enum` | `want_to_read`, `currently_reading`, `read`, `dnf` | library_items, comic_library_items |
| `recommendation_model_enum` | `content_based`, `collaborative_knn`, `neural_cf`, `hybrid`, `trending`, `popular` | recommendations |
| `content_type_enum` 🆕 | `book`, `comic` | recommendations, reading_progress, series_metadata |
| `content_preference_enum` 🆕 | `books`, `comics`, `both` | user_preferences |
| `collection_type_enum` 🆕 | `personalized`, `mood`, `utility`, `trending`, `free_reading`, `series`, `author`, `genre` | collections |

---

## 🚀 Indexes & Performance

### New Query Performance Targets (v2.0)

| Query | Target | Index Used |
|-------|--------|-----------|
| User's home collections | < 50ms | `idx_user_collections_user_rank` |
| Collection items lookup | < 20ms | JSONB read on `collections.items_json` |
| Series for book/comic | < 10ms | `idx_series_metadata_name` |
| Continue reading list | < 30ms | `idx_reading_progress_user_last_read` |
| Free books search | < 100ms | `idx_books_free_online` |
| Free comics search | < 100ms | `idx_comics_free_online` |
| Comic series by name | < 50ms | `idx_comics_series` |
| Comics by character | < 100ms | `idx_comics_characters_gin` |

### Trigger for Comic Rating Stats

```sql
CREATE OR REPLACE FUNCTION update_comic_ratings_stats()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE comics
    SET
        kitabee_rating = (
            SELECT AVG(rating)::DECIMAL(3,2)
            FROM comic_ratings
            WHERE comic_id = COALESCE(NEW.comic_id, OLD.comic_id)
        ),
        kitabee_ratings_count = (
            SELECT COUNT(*)
            FROM comic_ratings
            WHERE comic_id = COALESCE(NEW.comic_id, OLD.comic_id)
        ),
        updated_at = CURRENT_TIMESTAMP
    WHERE id = COALESCE(NEW.comic_id, OLD.comic_id);
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_comic_ratings
AFTER INSERT OR UPDATE OR DELETE ON comic_ratings
FOR EACH ROW EXECUTE FUNCTION update_comic_ratings_stats();
```

### Trigger for Collection Item Count

```sql
CREATE OR REPLACE FUNCTION update_collection_item_count()
RETURNS TRIGGER AS $$
BEGIN
    NEW.item_count = jsonb_array_length(NEW.items_json);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_collection_count
BEFORE INSERT OR UPDATE ON collections
FOR EACH ROW EXECUTE FUNCTION update_collection_item_count();
```

---

## 🐍 API Schemas (Pydantic)

### Comic Schemas 🆕

```python
# schemas/comic.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal


class ComicBase(BaseModel):
    title: str = Field(..., max_length=500)
    creators: List[str] = []
    publisher: Optional[str] = None
    description: Optional[str] = None
    genres: List[str] = []
    characters: List[str] = []


class ComicResponse(ComicBase):
    id: UUID
    external_id: str
    external_source: str
    tags: List[str] = []
    published_year: Optional[int] = None
    page_count: Optional[int] = None
    language: str = "en"
    cover_url: Optional[str] = None
    cover_url_large: Optional[str] = None
    series_name: Optional[str] = None
    issue_number: Optional[int] = None
    volume_number: Optional[int] = None
    series_entry_type: Optional[str] = None
    average_rating: Optional[Decimal] = None
    ratings_count: int = 0
    kitabee_rating: Optional[Decimal] = None
    kitabee_ratings_count: int = 0
    is_free_online: bool = False
    internet_archive_id: Optional[str] = None
    mood_tags: List[str] = []
    metadata: Dict[str, Any] = {}

    class Config:
        from_attributes = True


class ComicSearchQuery(BaseModel):
    q: str = Field(..., min_length=2, max_length=200)
    limit: int = Field(20, ge=1, le=40)
    offset: int = Field(0, ge=0)
    publisher: Optional[str] = None
    character: Optional[str] = None
    free_only: bool = False


class ComicSearchResponse(BaseModel):
    query: str
    total_count: int
    limit: int
    offset: int
    results: List[ComicResponse]
```

### Collection Schemas 🆕

```python
# schemas/collection.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from uuid import UUID


class CollectionItem(BaseModel):
    """Single item in a collection row."""
    content_type: Literal["book", "comic"]
    id: UUID
    position: int
    title: str
    cover_url: Optional[str] = None
    is_free_online: bool = False
    kitabee_rating: Optional[float] = None


class CollectionResponse(BaseModel):
    id: UUID
    name: str
    title: str  # Catchy display title
    description: Optional[str] = None
    collection_type: str
    content_type: str  # 'books' | 'comics' | 'mixed'
    mood: Optional[str] = None
    items: List[CollectionItem]
    item_count: int
    based_on_book_id: Optional[UUID] = None
    based_on_author: Optional[str] = None
    generated_at: datetime

    class Config:
        from_attributes = True


class HomeCollectionsResponse(BaseModel):
    """Response for GET /api/v1/collections (home screen)."""
    user_id: UUID
    generated_at: datetime
    total_collections: int
    collections: List[CollectionResponse]
    continue_reading: Optional[List[CollectionItem]] = None
```

### Series Schemas 🆕

```python
# schemas/series.py
from pydantic import BaseModel
from typing import Optional, List, Literal
from uuid import UUID


class SeriesEntry(BaseModel):
    id: UUID
    title: str
    order: int
    label: Optional[str] = None  # "Start Here" | "Prequel" | "Spinoff" | None
    cover_url: Optional[str] = None


class CompanionSeries(BaseModel):
    name: str
    entries: List[SeriesEntry]
    tip: Optional[str] = None


class OrderedSeriesResponse(BaseModel):
    series_name: str
    content_type: Literal["book", "comic"]
    total_items: int
    is_complete: bool
    main_series: List[SeriesEntry]
    companion_series: List[CompanionSeries] = []
    tip: Optional[str] = None
    generated_at: str
```

### Reading Progress Schemas 🆕

```python
# schemas/reading_progress.py
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Literal
from uuid import UUID
from decimal import Decimal


class ReadingProgressUpdate(BaseModel):
    current_position: Optional[str] = None
    current_page: Optional[int] = Field(None, ge=0)
    total_pages: Optional[int] = Field(None, ge=1)
    progress_percent: Decimal = Field(..., ge=0, le=100)
    session_time_seconds: int = Field(0, ge=0)


class ReadingProgressResponse(BaseModel):
    id: UUID
    user_id: UUID
    book_id: Optional[UUID] = None
    comic_id: Optional[UUID] = None
    content_type: Literal["book", "comic"]
    current_position: Optional[str] = None
    current_page: Optional[int] = None
    total_pages: Optional[int] = None
    progress_percent: Decimal
    last_read_at: datetime
    total_reading_time_seconds: int
    session_count: int
    is_completed: bool
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
```

---

## 📘 Frontend Types (TypeScript)

### Comic Types 🆕

```typescript
// types/comic.ts

export interface Comic {
  id: string;
  externalId: string;
  externalSource: string;
  title: string;
  creators: string[];
  publisher?: string;
  description?: string;
  genres: string[];
  characters: string[];
  tags?: string[];
  publishedYear?: number;
  pageCount?: number;
  language: string;
  coverUrl?: string;
  coverUrlLarge?: string;
  seriesName?: string;
  issueNumber?: number;
  volumeNumber?: number;
  seriesEntryType?: 'main' | 'annual' | 'oneshot' | 'special';
  averageRating: number;
  ratingsCount: number;
  kitabeeRating?: number;
  kitabeeRatingsCount: number;
  isFreeOnline: boolean;
  internetArchiveId?: string;
  moodTags: string[];
  metadata: Record<string, any>;
}
```

### Collection Types 🆕

```typescript
// types/collection.ts

export type CollectionType =
  | 'personalized'
  | 'mood'
  | 'utility'
  | 'trending'
  | 'free_reading'
  | 'series'
  | 'author'
  | 'genre';

export type ContentType = 'book' | 'comic';

export interface CollectionItem {
  contentType: ContentType;
  id: string;
  position: number;
  title: string;
  coverUrl?: string;
  isFreeOnline: boolean;
  kitabeeRating?: number;
}

export interface Collection {
  id: string;
  name: string;
  title: string;
  description?: string;
  collectionType: CollectionType;
  contentType: 'books' | 'comics' | 'mixed';
  mood?: string;
  items: CollectionItem[];
  itemCount: number;
  basedOnBookId?: string;
  basedOnAuthor?: string;
  generatedAt: string;
}

export interface HomeCollections {
  userId: string;
  generatedAt: string;
  totalCollections: number;
  collections: Collection[];
  continueReading?: CollectionItem[];
}
```

### Series Types 🆕

```typescript
// types/series.ts

export interface SeriesEntry {
  id: string;
  title: string;
  order: number;
  label?: 'Start Here' | 'Prequel' | 'Spinoff' | null;
  coverUrl?: string;
}

export interface CompanionSeries {
  name: string;
  entries: SeriesEntry[];
  tip?: string;
}

export interface OrderedSeries {
  seriesName: string;
  contentType: ContentType;
  totalItems: number;
  isComplete: boolean;
  mainSeries: SeriesEntry[];
  companionSeries: CompanionSeries[];
  tip?: string;
  generatedAt: string;
}
```

### Reading Progress Types 🆕

```typescript
// types/reading.ts

export interface ReadingProgress {
  id: string;
  userId: string;
  bookId?: string;
  comicId?: string;
  contentType: ContentType;
  currentPosition?: string;
  currentPage?: number;
  totalPages?: number;
  progressPercent: number;
  lastReadAt: string;
  totalReadingTimeSeconds: number;
  sessionCount: number;
  isCompleted: boolean;
  completedAt?: string;
}
```

---

## 🌐 External API Response Schemas

### Google Books API
*[Unchanged from v1.0]*

### Comic Vine API 🆕

**Endpoint:** `GET https://comicvine.gamespot.com/api/volumes/?api_key={key}&filter=name:{query}&format=json`

```typescript
interface ComicVineResponse {
  error: 'OK' | string;
  limit: number;
  offset: number;
  number_of_page_results: number;
  number_of_total_results: number;
  status_code: number;
  results: ComicVineVolume[];
}

interface ComicVineVolume {
  id: number;
  name: string;
  description?: string;  // HTML
  publisher?: {
    id: number;
    name: string;
  };
  start_year?: string;
  count_of_issues?: number;
  image?: {
    icon_url: string;
    medium_url: string;
    original_url: string;
  };
  characters?: Array<{ id: number; name: string }>;
  api_detail_url: string;
}
```

### Internet Archive API 🆕

**Search Endpoint:** `GET https://archive.org/advancedsearch.php?q={query}+AND+mediatype:texts&fl[]=identifier&fl[]=title&fl[]=creator&fl[]=description&fl[]=year&output=json`

```typescript
interface InternetArchiveSearchResponse {
  responseHeader: {
    status: number;
    QTime: number;
    params: Record<string, any>;
  };
  response: {
    numFound: number;
    start: number;
    docs: InternetArchiveDoc[];
  };
}

interface InternetArchiveDoc {
  identifier: string;
  title?: string;
  creator?: string | string[];
  description?: string | string[];
  year?: string;
  language?: string | string[];
  mediatype: string;
  collection?: string[];
  subject?: string[];
}
```

**Metadata Endpoint:** `GET https://archive.org/metadata/{identifier}`

Returns file listing including EPUB, PDF, image files for reading.

---

## 💾 Redis Cache Schemas

### New Cache Keys in v2.0

| Key Pattern | Value Type | TTL | Purpose |
|-------------|-----------|-----|---------|
| `comic:{comic_id}` | JSON (Comic) | 24h | Comic details cache |
| `comic:external:{source}:{ext_id}` | JSON (Comic) | 24h | External comic lookup |
| `search:comics:{query}` | JSON (ComicList) | 30m | Comic search results |
| `search:all:{query}` | JSON (Mixed) | 30m | Unified search |
| `collections:home:{user_id}` | JSON (HomeCollections) | 6h | User's home screen |
| `collection:{collection_id}` | JSON (Collection) | 6h | Individual collection |
| `series:{name}:{content_type}` | JSON (OrderedSeries) | 7d | Series order data |
| `ia:reading_links:{identifier}` | JSON (Links) | 24h | Internet Archive URLs |
| `reading_progress:{user_id}` | JSON (List) | 5m | Continue reading list |

### Cache Invalidation Events (Updated)

| Event | Keys Invalidated |
|-------|------------------|
| New book rating | `recs:user:{user_id}*`, `collections:home:{user_id}` |
| New comic rating | `recs:user:{user_id}*`, `collections:home:{user_id}` |
| Book/comic added to library | `collections:home:{user_id}` |
| Reading progress update | `reading_progress:{user_id}`, `collections:home:{user_id}` |
| Preferences update | `collections:home:{user_id}` |

---

## 🤖 ML Feature Schemas

### Collection Engine Schemas 🆕

```python
class ContentVector(BaseModel):
    """Vectorized representation of book or comic."""
    content_id: str
    content_type: Literal["book", "comic"]
    text_content: str  # title + description + genres + tags
    vector: Dict[int, float]  # TF-IDF sparse vector


class ClusterAssignment(BaseModel):
    """KMeans cluster output."""
    content_id: str
    cluster_id: int
    distance_to_center: float


class MoodDetection(BaseModel):
    """Mood detection output for a piece of content."""
    content_id: str
    primary_mood: str  # 'dark', 'funny', 'epic', etc.
    mood_scores: Dict[str, float]  # {mood: confidence}
    confidence: float


class GeneratedCollection(BaseModel):
    """Output of collection engine."""
    name: str
    title: str  # Catchy title
    description: Optional[str] = None
    collection_type: str
    content_type: str
    mood: Optional[str] = None
    items: List[str]  # content_ids in order
    based_on: Optional[Dict[str, Any]] = None
```

### Series Intelligence Schemas 🆕

```python
class SeriesInfo(BaseModel):
    """Detected series membership."""
    series_name: str
    entry_type: Literal["main", "prequel", "spinoff", "companion"]
    volume_number: Optional[int] = None
    confidence: float


class OrderedSeriesOutput(BaseModel):
    """Series builder output."""
    series_name: str
    content_type: str
    main_series: List[Dict[str, Any]]
    companion_series: List[Dict[str, Any]]
    tip: Optional[str] = None
```

---

## 📝 Sample Data

### Sample Comic 🆕

```json
{
  "id": "cc0e8400-e29b-41d4-a716-446655440006",
  "external_id": "4050-42165",
  "external_source": "comic_vine",
  "title": "Batman: Year One",
  "creators": ["Frank Miller", "David Mazzucchelli"],
  "publisher": "DC Comics",
  "description": "Bruce Wayne returns to Gotham City after a 12-year absence to begin his crusade against crime...",
  "genres": ["Superhero", "Crime", "Drama"],
  "characters": ["Batman", "Bruce Wayne", "James Gordon", "Selina Kyle"],
  "published_year": 1987,
  "page_count": 104,
  "language": "en",
  "cover_url": "https://comicvine.gamespot.com/a/uploads/original/...",
  "series_name": "Batman",
  "issue_number": 1,
  "volume_number": 1,
  "series_entry_type": "main",
  "kitabee_rating": 4.8,
  "kitabee_ratings_count": 156,
  "is_free_online": false,
  "mood_tags": ["dark", "gritty", "noir"],
  "cached_at": "2025-01-20T10:00:00Z"
}
```

### Sample Collection 🆕

```json
{
  "id": "dd0e8400-e29b-41d4-a716-446655440007",
  "name": "epic_fantasy_cluster_3",
  "title": "Epic Worlds Built From Scratch",
  "description": "Immersive fantasy worlds you can lose yourself in for weeks",
  "collection_type": "mood",
  "content_type": "books",
  "mood": "epic",
  "items_json": [
    {"content_type": "book", "id": "uuid-dune", "position": 1, "title": "Dune", "cover_url": "..."},
    {"content_type": "book", "id": "uuid-wot", "position": 2, "title": "The Eye of the World", "cover_url": "..."},
    {"content_type": "book", "id": "uuid-notw", "position": 3, "title": "The Name of the Wind", "cover_url": "..."}
  ],
  "item_count": 12,
  "generated_at": "2025-01-20T08:00:00Z",
  "expires_at": "2025-01-20T14:00:00Z"
}
```

### Sample Series Metadata 🆕

```json
{
  "id": "ee0e8400-e29b-41d4-a716-446655440008",
  "series_name": "Dune",
  "content_type": "book",
  "ordered_items_json": [
    {"id": "uuid1", "title": "Dune", "order": 1, "label": "Start Here"},
    {"id": "uuid2", "title": "Dune Messiah", "order": 2, "label": null},
    {"id": "uuid3", "title": "Children of Dune", "order": 3, "label": null},
    {"id": "uuid4", "title": "God Emperor of Dune", "order": 4, "label": null},
    {"id": "uuid5", "title": "Heretics of Dune", "order": 5, "label": null},
    {"id": "uuid6", "title": "Chapterhouse: Dune", "order": 6, "label": null}
  ],
  "companion_series_json": [
    {
      "name": "Prequel Series by Brian Herbert",
      "entries": [
        {"id": "uuid7", "title": "House Atreides", "order": 1, "label": null},
        {"id": "uuid8", "title": "House Harkonnen", "order": 2, "label": null},
        {"id": "uuid9", "title": "House Corrino", "order": 3, "label": null}
      ],
      "tip": "Read after Book 1 or after all 6 originals."
    }
  ],
  "tip": "Books 1-3 are the core trilogy. Books 4-6 are for dedicated fans.",
  "total_items": 6,
  "is_complete": true,
  "generated_at": "2025-01-20T10:00:00Z"
}
```

### Sample Reading Progress 🆕

```json
{
  "id": "ff0e8400-e29b-41d4-a716-446655440009",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "book_id": "uuid-pride-prejudice",
  "content_type": "book",
  "current_position": "epubcfi(/6/14[chapter_5]!/4/2/2)",
  "current_page": 87,
  "total_pages": 432,
  "progress_percent": 20.14,
  "last_read_at": "2025-01-20T22:15:00Z",
  "total_reading_time_seconds": 4820,
  "session_count": 4,
  "is_completed": false
}
```

---

## 🚚 Migration Strategy

### v2.0 Migration Plan

The v2.0 additions require these migrations (in order):

```bash
# 1. Add new enum types
alembic revision -m "add content_type and collection_type enums"

# 2. Update books table (new columns)
alembic revision -m "add series and free reading fields to books"

# 3. Update user_preferences (content_type_preference)
alembic revision -m "add content_type_preference to user_preferences"

# 4. Update search_history (comic support)
alembic revision -m "add comic support to search_history"

# 5. Update recommendations (polymorphic content)
alembic revision -m "add comic support to recommendations"

# 6. Create comics table
alembic revision -m "create comics table"

# 7. Create comic_ratings table
alembic revision -m "create comic_ratings table"

# 8. Create comic_library_items table
alembic revision -m "create comic_library_items table"

# 9. Create collections table
alembic revision -m "create collections table"

# 10. Create user_collections table
alembic revision -m "create user_collections table"

# 11. Create reading_progress table
alembic revision -m "create reading_progress table"

# 12. Create series_metadata table
alembic revision -m "create series_metadata table"

# 13. Add triggers for comic ratings and collection item count
alembic revision -m "add triggers for comic stats and collection counts"
```

### Safe Migration Practices
*[Unchanged from v1.0]*

---

## 🔄 Schema Evolution

### Version Compatibility

| Version | Status | Changes |
|---------|--------|---------|
| **v1.0** | ✅ Deployed | Initial schema (7 tables) |
| **v2.0** | 🟢 Current | Added comics, collections, reading progress, series metadata (14 tables total) |
| **v2.1** | 📅 Planned | Social features (follows, activity feed) |
| **v3.0** | 🔮 Future | Multi-language support, audio books |

---

## 🔒 Data Privacy & Security

### Updated Sensitive Data Classification (v2.0)

| Field | Classification | Handling |
|-------|---------------|----------|
| `password_hash` | 🔴 Critical | Never in logs or API responses |
| `email` | 🟡 Sensitive | Encrypted at rest, HTTPS only |
| `date_of_birth` | 🟡 Sensitive | Not exposed publicly |
| `ratings` (books + comics) | 🟢 Semi-public | Aggregated for others |
| `library` (books + comics) | 🟢 Semi-public | Optional public sharing |
| `reading_progress` 🆕 | 🟡 Sensitive | Never exposed to other users |
| `search_history` | 🟡 Sensitive | Anonymized after 90 days |

### Reading Progress Privacy 🆕
- `reading_progress` is fully private
- Never appears in public library views
- Only user themselves can see their progress
- Deleted immediately on account deletion

---

## 📎 Appendix

### Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Original] | [Your Name] | Initial schema (7 tables) |
| 2.0 | [Today] | [Your Name] | Added comics, comic_ratings, comic_library_items, collections, user_collections, reading_progress, series_metadata tables. Added series/free-reading fields to books. Added content_type support to recommendations, preferences, search_history. New enums: content_type, content_preference, collection_type. |

---

**End of Schema Document** 🗄️

*"The schema is the contract. Break it, break the app."*

---

