# Kitabee API — Examples

Practical curl examples for every endpoint. All responses follow the standard envelope.

Base URL (local): `http://localhost:8000`

---

## Health

### `GET /health`

```bash
curl http://localhost:8000/health
Response

JSON

{
  "success": true,
  "data": {
    "status": "ok"
  },
  "meta": {
    "timestamp": "2025-07-19T10:00:00.000000+00:00",
    "version": "v1"
  }
}
GET /health/cache
Bash

curl http://localhost:8000/health/cache
Response — Redis connected

JSON

{
  "success": true,
  "data": {
    "connected": true,
    "info": {
      "redis_version": "7.0.0",
      "connected_clients": 1,
      "used_memory_human": "1.00M",
      "keyspace_hits": 42,
      "keyspace_misses": 7,
      "uptime_in_seconds": 3600
    }
  },
  "meta": {
    "timestamp": "2025-07-19T10:00:00.000000+00:00",
    "version": "v1"
  }
}
Response — Redis down

JSON

{
  "success": true,
  "data": {
    "connected": false,
    "info": null
  },
  "meta": {
    "timestamp": "2025-07-19T10:00:00.000000+00:00",
    "version": "v1"
  }
}
Books
GET /api/v1/books/search
Search books by title, author, or ISBN.

Minimal request

Bash

curl "http://localhost:8000/api/v1/books/search?q=dune"
With limit

Bash

curl "http://localhost:8000/api/v1/books/search?q=frank+herbert&limit=5"
Response

JSON

{
  "success": true,
  "data": {
    "query": "dune",
    "total_count": 3,
    "limit": 20,
    "offset": 0,
    "results": [
      {
        "google_books_id": "ydQR_YorfqMC",
        "title": "Dune",
        "subtitle": null,
        "authors": ["Frank Herbert"],
        "description": "Set in the far future amidst a feudal interstellar society...",
        "categories": ["Fiction"],
        "thumbnail_url": "http://books.google.com/books/content?id=ydQR_YorfqMC&zoom=1",
        "small_thumbnail_url": "http://books.google.com/books/content?id=ydQR_YorfqMC&zoom=5",
        "average_rating": 4.5,
        "ratings_count": 1200,
        "published_date": "1965",
        "publisher": "Chilton Books",
        "page_count": 412,
        "language": "en",
        "isbn_10": "0441172717",
        "isbn_13": "9780441172719",
        "preview_link": "http://books.google.com/books?id=ydQR_YorfqMC&dq=dune",
        "info_link": "http://books.google.com/books?id=ydQR_YorfqMC"
      }
    ]
  },
  "meta": {
    "timestamp": "2025-07-19T10:00:00.000000+00:00",
    "version": "v1"
  }
}
Error — query too short

Bash

curl "http://localhost:8000/api/v1/books/search?q=a"
JSON

{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed.",
    "details": [
      {
        "type": "string_too_short",
        "loc": ["query", "q"],
        "msg": "String should have at least 2 characters",
        "input": "a"
      }
    ]
  },
  "meta": {
    "timestamp": "2025-07-19T10:00:00.000000+00:00",
    "version": "v1"
  }
}
Error — upstream unavailable

JSON

{
  "success": false,
  "error": {
    "code": "UPSTREAM_UNAVAILABLE",
    "message": "Book search is temporarily unavailable. Please try again."
  },
  "meta": {
    "timestamp": "2025-07-19T10:00:00.000000+00:00",
    "version": "v1"
  }
}
GET /api/v1/books/{book_id}
Fetch full book details by Kitabee UUID. UUID is assigned when a book
is first seen in search results and persisted to the database.

Bash

curl "http://localhost:8000/api/v1/books/123e4567-e89b-12d3-a456-426614174000"
Response

JSON

{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "external_id": "ydQR_YorfqMC",
    "external_source": "google_books",
    "google_books_id": "ydQR_YorfqMC",
    "title": "Dune",
    "subtitle": null,
    "authors": ["Frank Herbert"],
    "description": "Set in the far future amidst a feudal interstellar society...",
    "categories": ["Fiction"],
    "thumbnail_url": "http://books.google.com/books/content?id=ydQR_YorfqMC&zoom=1",
    "small_thumbnail_url": "http://books.google.com/books/content?id=ydQR_YorfqMC&zoom=5",
    "average_rating": 4.5,
    "ratings_count": 1200,
    "published_date": "1965",
    "publisher": "Chilton Books",
    "page_count": 412,
    "language": "en",
    "isbn_10": "0441172717",
    "isbn_13": "9780441172719",
    "preview_link": "http://books.google.com/books?id=ydQR_YorfqMC&dq=dune",
    "info_link": "http://books.google.com/books?id=ydQR_YorfqMC",
    "kitabee_rating": null,
    "kitabee_ratings_count": 0,
    "metadata_json": {
      "google_books": {
        "preview_link": "http://books.google.com/books?id=ydQR_YorfqMC&dq=dune",
        "info_link": "http://books.google.com/books?id=ydQR_YorfqMC"
      }
    }
  },
  "meta": {
    "timestamp": "2025-07-19T10:00:00.000000+00:00",
    "version": "v1"
  }
}
Error — not found

Bash

curl "http://localhost:8000/api/v1/books/00000000-0000-0000-0000-000000000000"
JSON

{
  "success": false,
  "error": {
    "code": "BOOK_NOT_FOUND",
    "message": "No book found with id 00000000-0000-0000-0000-000000000000."
  },
  "meta": {
    "timestamp": "2025-07-19T10:00:00.000000+00:00",
    "version": "v1"
  }
}
Error — invalid UUID format

Bash

curl "http://localhost:8000/api/v1/books/not-a-uuid"
JSON

{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed.",
    "details": [
      {
        "type": "uuid_parsing",
        "loc": ["path", "book_id"],
        "msg": "Input should be a valid UUID",
        "input": "not-a-uuid"
      }
    ]
  },
  "meta": {
    "timestamp": "2025-07-19T10:00:00.000000+00:00",
    "version": "v1"
  }
}
GET /api/v1/books/{book_id}/similar
Find books similar to a given Kitabee UUID. Similarity based on author + genre.
Source book is excluded from results.

Default limit (10)

Bash

curl "http://localhost:8000/api/v1/books/123e4567-e89b-12d3-a456-426614174000/similar"
Custom limit

Bash

curl "http://localhost:8000/api/v1/books/123e4567-e89b-12d3-a456-426614174000/similar?limit=5"
Response — same shape as /search

JSON

{
  "success": true,
  "data": {
    "query": "Frank Herbert Fiction",
    "total_count": 5,
    "limit": 5,
    "offset": 0,
    "results": [...]
  },
  "meta": {
    "timestamp": "2025-07-19T10:00:00.000000+00:00",
    "version": "v1"
  }
}
Error — source book not found

JSON

{
  "success": false,
  "error": {
    "code": "BOOK_NOT_FOUND",
    "message": "No book found with id 00000000-0000-0000-0000-000000000000."
  },
  "meta": {
    "timestamp": "2025-07-19T10:00:00.000000+00:00",
    "version": "v1"
  }
}
Query Parameter Reference
Endpoint	Param	Type	Default	Min	Max
/search	q	string	required	2 chars	200 chars
/search	limit	int	20	1	40
/search	offset	int	0	0	—
/{id}/similar	limit	int	10	1	40
Error Code Reference
Code	HTTP Status	Meaning
VALIDATION_ERROR	422	Invalid query params or path params
BOOK_NOT_FOUND	404	UUID not in database
UPSTREAM_UNAVAILABLE	503	Google Books API unreachable
NOT_FOUND	404	Route does not exist
INTERNAL_ERROR	500	Unhandled server error
