
# 🗄️ Kitabee — Data Schema Document

> **Document Version:** 2.1
> **Last Updated:** 2026-08-10
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
18. [content_id Convention (v2.1)](#-content_id-convention-v21) 🆕

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

### What Changed in v2.1 (Day 24.5)
Backend content identity unified across all three external APIs (Google Books, Comic Vine, Internet Archive) using a **prefixed content_id convention**:

- `gb:{google_books_id}` → Google Books volumes
- `cv:{comic_vine_id}` → Comic Vine issues and volumes
- `ia:{archive_identifier}` → Internet Archive items

**DB schema unchanged.** The `external_id` + `external_source` columns still handle multi-source storage. The prefix is constructed at the service boundary (never stored in DB) and used as the public API-facing identifier. See [Section 18](#-content_id-convention-v21) for full detail.

### Scope
- ✅ PostgreSQL database schema (books + comics + collections + reading)
- ✅ Pydantic models (backend validation)
- ✅ TypeScript interfaces (frontend types)
- ✅ Redis cache key patterns
- ✅ External API response shapes (Google Books, Comic Vine, Internet Archive)
- ✅ ML model input/output structures
- ✅ Sample data for testing
- ✅ **content_id prefix convention** 🆕 v2.1

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
| **Content IDs (API)** 🆕 | `{prefix}:{external_id}` | `gb:ByLKDQAAQBAJ`, `cv:12345`, `ia:pg1342` |

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

### 9. Prefixed Content Identity (New in v2.1) 🆕
API-facing content IDs use prefixes (`gb:`, `cv:`, `ia:`) to route requests to the correct external source at the service boundary. DB storage remains normalized around `external_id` + `external_source`. See [Section 18](#-content_id-convention-v21).

---

## 🔗 Entity Relationship Diagram

*[Unchanged from v2.0 — full ER diagram preserved]*

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

*[Sections 4.1 – 4.14 unchanged from v2.0 — all 14 tables preserved as-is]*

---

## 📋 Enumerations

*[Unchanged from v2.0]*

---

## 🚀 Indexes & Performance

*[Unchanged from v2.0]*

---

## 🐍 API Schemas (Pydantic)

### New in v2.1: ContentItemResponse 🆕

```python
# schemas/book.py — added in Day 24.5
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from decimal import Decimal


class ContentItemResponse(BaseModel):
    """Unified response shape for content from all 3 sources.

    Returned by:
    - GET /api/v1/books/{content_id}
    - GET /api/v1/books/search
    - GET /api/v1/collections (items)
    """
    content_id: str = Field(..., description="Prefixed ID: gb:xxx | cv:xxx | ia:xxx")
    external_id: str
    external_source: Literal["google_books", "comic_vine", "internet_archive"]
    title: str
    author: Optional[str] = None
    authors: List[str] = []
    description: Optional[str] = None
    cover_url: Optional[str] = None
    cover_url_large: Optional[str] = None
    content_type: Literal["book", "comic"]
    is_free: bool
    free_url: Optional[str] = None
    genres: List[str] = []
    language: str = "en"
    publisher: Optional[str] = None
    published_date: Optional[str] = None
    page_count: Optional[int] = None
    isbn_10: Optional[str] = None
    isbn_13: Optional[str] = None
    average_rating: Optional[Decimal] = None
    rating_count: int = 0
    series_id: Optional[str] = None
    series_order: Optional[str] = None
    source: str


class ContentItemListResponse(BaseModel):
    """Wrapped list of ContentItems for search endpoints."""
    total_count: int
    limit: int
    offset: int
    results: List[ContentItemResponse]
```

**Field notes:**
- `is_free` is `True` only for `ia:` items. Always `False` for `gb:` and `cv:`.
- `free_url` is `None` for `gb:` and `cv:`. Comic Vine info pages are not readable content.
- `content_type` is `"comic"` for `cv:` items, `"book"` for `gb:` and `ia:` items.

*[Rest of section unchanged — Comic Schemas, Collection Schemas, Series Schemas, Reading Progress Schemas preserved as-is]*

---

## 📘 Frontend Types (TypeScript)

### New in v2.1: ContentItem 🆕

```typescript
// types/content.ts — added Day 24.5

export type ContentSource = 'google_books' | 'comic_vine' | 'internet_archive';
export type ContentTypeStr = 'book' | 'comic';

export interface ContentItem {
  contentId: string;           // e.g., "gb:ByLKDQAAQBAJ"
  externalId: string;
  externalSource: ContentSource;
  title: string;
  author?: string;
  authors: string[];
  description?: string;
  coverUrl?: string;
  coverUrlLarge?: string;
  contentType: ContentTypeStr;
  isFree: boolean;
  freeUrl?: string;
  genres: string[];
  language: string;
  publisher?: string;
  publishedDate?: string;
  pageCount?: number;
  isbn10?: string;
  isbn13?: string;
  averageRating?: number;
  ratingCount: number;
  seriesId?: string;
  seriesOrder?: string;
  source: string;
}

export interface ContentItemList {
  totalCount: number;
  limit: number;
  offset: number;
  results: ContentItem[];
}
```

*[Rest of section unchanged — Comic Types, Collection Types, Series Types, Reading Progress Types preserved as-is]*

---

## 🌐 External API Response Schemas

*[Unchanged from v2.0]*

---

## 💾 Redis Cache Schemas

### Updated Cache Keys (v2.1)

| Key Pattern | Value Type | TTL | Purpose |
|-------------|-----------|-----|---------|
| `gb:search:{query}:{page}` | JSON (list) | 30m | Google Books search cache |
| `gb:volume:{google_books_id}` | JSON (Volume) | 24h | Google Books detail cache |
| `cv:search:{query}:{page}` | JSON (list) | 30m | Comic Vine search cache |
| `cv:issue:{comic_vine_id}` | JSON (Issue) | 24h | Comic Vine detail cache |
| `ia:search:{query}:{page}:{limit}` | JSON (list) | 24h | Internet Archive search cache |
| `ia:item:{identifier}` | JSON (Metadata) | 24h | Internet Archive detail cache |
| `collections:home:{user_id}` | JSON (HomeCollections) | 6h | User's home screen |
| `series:{name}:{content_type}` | JSON (OrderedSeries) | 7d | Series order data |
| `reading_progress:{user_id}` | JSON (List) | 5m | Continue reading list |

**Cache invalidation note (v2.1):** After changing search query parameters or normalization logic, flush affected cache prefix with `redis-cli FLUSHALL` or targeted `KEYS ia:search:*` + `DEL`.

---

## 🤖 ML Feature Schemas

*[Unchanged from v2.0]*

---

## 📝 Sample Data

### Sample ContentItem — Google Books 🆕

```json
{
  "content_id": "gb:ByLKDQAAQBAJ",
  "external_id": "ByLKDQAAQBAJ",
  "external_source": "google_books",
  "title": "Dune",
  "author": "Frank Herbert",
  "authors": ["Frank Herbert"],
  "description": "Set on the desert planet Arrakis...",
  "cover_url": "http://books.google.com/books/content?id=ByLKDQAAQBAJ&...",
  "content_type": "book",
  "is_free": false,
  "free_url": null,
  "genres": ["Fiction", "Science Fiction"],
  "language": "en",
  "publisher": "Ace",
  "published_date": "2010-06-01",
  "page_count": 688,
  "isbn_10": null,
  "isbn_13": "9780441013593",
  "average_rating": 4.5,
  "rating_count": 1234,
  "source": "google_books"
}
```

### Sample ContentItem — Comic Vine 🆕

```json
{
  "content_id": "cv:137677",
  "external_id": "137677",
  "external_source": "comic_vine",
  "title": "Dune",
  "author": null,
  "authors": [],
  "description": null,
  "cover_url": "https://comicvine.gamespot.com/a/uploads/scale_medium/...",
  "content_type": "comic",
  "is_free": false,
  "free_url": null,
  "genres": [],
  "language": "en",
  "publisher": null,
  "published_date": null,
  "series_order": "1",
  "source": "comic_vine"
}
```

### Sample ContentItem — Internet Archive 🆕

```json
{
  "content_id": "ia:duneherb00herb",
  "external_id": "duneherb00herb",
  "external_source": "internet_archive",
  "title": "Dune",
  "author": "Herbert, Frank",
  "authors": ["Herbert, Frank"],
  "description": "Dune -- Maud'Dib -- Appendix I: Ecology of Dune...",
  "cover_url": "https://archive.org/services/img/duneherb00herb",
  "content_type": "book",
  "is_free": true,
  "free_url": null,
  "genres": ["Dune (Imaginary place)", "Science fiction"],
  "language": "eng",
  "publisher": null,
  "published_date": "1984-01-01T00:00:00Z",
  "source": "internet_archive"
}
```

*[Rest of section unchanged — Sample Comic, Sample Collection, Sample Series Metadata, Sample Reading Progress preserved as-is]*

---

## 🚚 Migration Strategy

*[Unchanged from v2.0. No new migrations required in v2.1 — DB schema unchanged.]*

---

## 🔄 Schema Evolution

### Version Compatibility

| Version | Status | Changes |
|---------|--------|---------|
| **v1.0** | ✅ Deployed | Initial schema (7 tables) |
| **v2.0** | ✅ Deployed | Added comics, collections, reading progress, series metadata (14 tables total) |
| **v2.1** | 🟢 Current | Added content_id prefix convention (gb:/cv:/ia:) at API boundary. **DB schema unchanged.** ContentItemResponse unified response shape. IA search scoped to title+creator fields. Comic Vine `free_url` nulled. |
| **v2.2** | 📅 Planned | Social features (follows, activity feed) |
| **v3.0** | 🔮 Future | Multi-language support, audio books |

---

## 🔒 Data Privacy & Security

*[Unchanged from v2.0]*

---

## 📎 Appendix

### Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Original] | [Your Name] | Initial schema (7 tables) |
| 2.0 | [Original] | [Your Name] | Added comics, comic_ratings, comic_library_items, collections, user_collections, reading_progress, series_metadata tables. Added series/free-reading fields to books. Added content_type support to recommendations, preferences, search_history. New enums: content_type, content_preference, collection_type. |
| 2.1 | 2026-08-10 | [Your Name] | Added Section 18 (content_id convention). Added ContentItemResponse Pydantic schema. Added ContentItem TypeScript type. Updated Redis cache key patterns for all 3 external sources. Added sample ContentItem data. DB schema unchanged. |

---

## 🔗 content_id Convention (v2.1) 🆕

### Purpose

Unify content identity across three heterogeneous external sources (Google Books, Comic Vine, Internet Archive) into a single string identifier usable by the frontend, ratings, library, and detail endpoints — **without adding a new column to the database**.

### Format

```
{prefix}:{raw_external_id}
```

| Prefix | Source | DB `external_source` | Example |
|--------|--------|----------------------|---------|
| `gb` | Google Books | `google_books` | `gb:ByLKDQAAQBAJ` |
| `cv` | Comic Vine | `comic_vine` | `cv:137677` |
| `ia` | Internet Archive | `internet_archive` | `ia:duneherb00herb` |

### Design Rules

1. **Constructed at service boundary, never stored.** The `books.external_id` column stores only the raw ID. The prefix is added at the response normalization layer (`services/content_normalizer.py`) and stripped at the request routing layer (`services/content_router.py`).

2. **DB schema unchanged.** Multi-source lookups continue to use the composite `(external_source, external_id)` unique constraint.

3. **Prefix drives dispatch.** The `ContentRouter.get_by_id(content_id)` method parses the prefix and forwards the request to the correct external client:
   - `gb:` → `GoogleBooksClient.get_volume()`
   - `cv:` → `ComicVineClient.get_issue()`
   - `ia:` → `InternetArchiveClient.get_item()`

4. **Ratings and library resolve to UUID.** When a user rates content or adds it to their library, the service layer:
   1. Parses `content_id` into `(prefix, external_id)`
   2. Looks up the book UUID via `(external_source, external_id)`
   3. Creates a stub row if not yet in DB (upsert on first interaction)
   4. Passes UUID to downstream persistence

5. **is_free flag is prefix-derived.** Always `True` for `ia:`, always `False` for `gb:` and `cv:`. Comic Vine info pages are not readable content.

6. **free_url is null for non-IA sources.** Only Internet Archive items have real readable URLs. Comic Vine `detail_url` was previously misleading and is now excluded from the response.

### Code Locations

| File | Purpose |
|------|---------|
| `backend/src/services/content_normalizer.py` | `make_content_id()`, `parse_content_id()`, `normalize_*()` per source |
| `backend/src/services/content_router.py` | `ContentRouter.get_by_id()`, `ContentRouter.search()` |
| `backend/src/api/routes/books.py` | Uses `ContentRouter` for detail + search |
| `backend/src/api/routes/collections.py` | Enriches collection items via all 3 clients concurrently |
| `backend/src/api/routes/ratings.py` | Accepts `content_id` string, resolves to UUID |
| `backend/src/api/routes/library.py` | Same as ratings |
| `backend/src/services/rating_service.py` | `resolve_content_id()` method |
| `backend/src/services/library_service.py` | `resolve_content_id()` method |

### API Endpoint Contract

```
GET /api/v1/books/{content_id}
    → 200 OK: ContentItemResponse
    → 404: content_id not found in source
    → 400: invalid content_id format (no prefix or unknown prefix)

GET /api/v1/books/search?q={query}&sources={list}
    → 200 OK: ContentItemListResponse (results from all requested sources, concurrent)

POST /api/v1/ratings
    Body: { content_id: "gb:xxx", rating: 5, review: "..." }
    → 201 Created

POST /api/v1/library
    Body: { content_id: "ia:xxx", status: "want_to_read" }
    → 201 Created
```

### Testing Approach

- All 3 external API clients are mocked in tests — no real HTTP.
- Test IDs use canonical form: `gb:test123`, `cv:456`, `ia:pg1342`.
- `test_content_normalizer.py` verifies all `normalize_*()` functions.
- `test_content_router.py` verifies dispatch by prefix + error paths.
- Route tests use string `content_id` in request paths and bodies.

### Migration Notes

- **No DB migration required.** The prefix layer is purely a service-layer convention.
- **Frontend must update.** Old frontend code that used raw UUIDs or `seed-*` IDs must be updated to use prefixed content IDs from API responses.
- **Redis cache flush required after query logic changes.** IA search relevance was fixed in Day 24.5 by scoping the query to `title:` + `creator:` fields and sorting by `downloads desc`. Existing cached search results must be purged.

---

**End of Schema Document** 🗄️

*"The schema is the contract. Break it, break the app."*
```

---