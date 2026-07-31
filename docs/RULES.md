Markdown

# Kitabee — Engineering Rules & Standards

> **Document Version:** 3.0  
> **Last Updated:** [Today's Date]  
> **Author:** [Your Name]  
> **Status:** MANDATORY for all code contributions  
> **Related Docs:** [PRD.md](./PRD.md) | [TECHSPEC.md](./TECHSPEC.md) | [SCHEMA.md](./SCHEMA.md)

---

## Table of Contents

1. [Core Philosophy](#core-philosophy)
2. [The Prime Rules](#the-prime-rules)
3. [Comment Discipline](#comment-discipline)
4. [Code Structure](#code-structure)
5. [Naming Conventions](#naming-conventions)
6. [Git and Version Control](#git-and-version-control)
7. [Commit Message Standards](#commit-message-standards)
8. [Branch Strategy](#branch-strategy)
9. [Python Backend Rules](#python-backend-rules)
10. [TypeScript Frontend Rules](#typescript-frontend-rules)
11. [File and Folder Organization](#file-and-folder-organization)
12. [API Design Rules](#api-design-rules)
13. [Database Rules](#database-rules)
14. [Security Rules](#security-rules)
15. [Testing Standards](#testing-standards)
16. [Documentation Standards](#documentation-standards)
17. [Performance Rules](#performance-rules)
18. [Error Handling](#error-handling)
19. [Dependency Management](#dependency-management)
20. [Environment and Secrets](#environment-and-secrets)
21. [Forbidden Practices](#forbidden-practices)
22. [Pre-Commit Checklist](#pre-commit-checklist)
23. [Debugging Standards](#debugging-standards)
24. [Enforcement Tools](#enforcement-tools)
25. [Design Token Rules](#design-token-rules)
26. [React Native Mobile Rules](#react-native-mobile-rules)
27. [Claude Code Interaction Rules](#claude-code-interaction-rules)

---

## Core Philosophy

### The Kitabee Code Standard

Write code that:

1. Solves the problem correctly
2. Is easy to read six months from now
3. Is easy to debug when it breaks
4. Contains zero visual noise
5. Follows consistent patterns
6. Speaks for itself without decoration

### The Guiding Principle

> Good code needs no decoration. Great code reads like prose.

Every line of code must serve a purpose. Every comment must add value. Every function must do one thing well.

### What We Value

- Correctness over cleverness
- Clarity over compactness
- Consistency over creativity
- Simplicity over sophistication
- Debuggability over decoration

---

## The Prime Rules

These are absolute. Breaking any of these means the code does not ship.

### Rule 1: No Emojis in Code

Never use emojis in:
- Source code files (.py, .ts, .tsx, .js)
- Function names
- Variable names
- Comments
- Log statements
- Error messages
- Commit messages (except in commit body if genuinely useful)

Emojis are acceptable only in:
- Markdown documentation files (README.md, docs/*.md)
- User-facing UI text (via translation strings, not hardcoded)

**Wrong:**
```python
def get_user():
    logger.info("Fetching user 🚀")
    return user
Right:

Python

def get_user():
    logger.info("Fetching user")
    return user
Rule 2: No Decorative Comment Blocks
Never use comment blocks like these:

Wrong:

Python

# ============================================
# USER SERVICE
# ============================================
# This module handles user operations
# ============================================

# ################
# # LOGIN LOGIC  #
# ################

#################################################
##             Authentication Module           ##
#################################################
Right:

Python

"""User service for authentication and profile management."""


class UserService:
    """Handles user CRUD operations."""
    
    def login(self, email: str, password: str) -> Optional[Token]:
        """Authenticate user and return token."""
        ...
Rule 3: Comments Explain Why, Not What
Wrong:

Python

# Increment counter by 1
counter += 1

# Get user by ID
user = get_user_by_id(user_id)

# Loop through books
for book in books:
    print(book)
Right:

Python

counter += 1

user = get_user_by_id(user_id)

for book in books:
    print(book)


# WHY comments are useful:

# Use exponential backoff to respect API rate limits (max 100 req/min)
retry_delay = 2 ** attempt

# HACK: Working around httpx bug #1234; remove when upgrading to 0.28+
timeout = 30 if is_slow_network else 10

# NOTE: Google Books API returns max 40 results per page
# See: https://developers.google.com/books/docs/v1/using
max_results = min(requested_limit, 40)
Rule 4: Section Markers Are Minimal
If you must mark sections, use minimal markers only:

Acceptable:

Python

"""Book service module."""

from typing import Optional
from sqlalchemy.orm import Session

from src.database.models import Book
from src.schemas.book import BookCreate, BookResponse


# Constants

MAX_SEARCH_RESULTS = 40
DEFAULT_PAGE_SIZE = 20


# Public API

class BookService:
    """Handles book operations."""
    
    def search(self, query: str) -> list[Book]:
        return self._perform_search(query)
    
    def get_by_id(self, book_id: str) -> Optional[Book]:
        return self._fetch_from_db(book_id)


# Private helpers

def _perform_search(query: str) -> list[Book]:
    ...

def _fetch_from_db(book_id: str) -> Optional[Book]:
    ...
Notice: Just # Constants, # Public API, # Private helpers. No decorations. No ASCII art. No emojis.

Rule 5: Never Commit Secrets
Never commit:

.env files
API keys
Passwords
Private keys
Database credentials
OAuth tokens
Always use environment variables loaded from .env files (which are gitignored).

Rule 6: Every Function Has a Docstring
All public functions and classes must have docstrings. Use Google style.

Wrong:

Python

def calculate_score(user_ratings, book_features):
    weights = [0.3, 0.4, 0.3]
    return sum(w * f for w, f in zip(weights, book_features))
Right:

Python

def calculate_score(
    user_ratings: list[Rating],
    book_features: BookFeatures
) -> float:
    """Calculate recommendation score for user-book pair.
    
    Combines content-based and collaborative filtering
    with fixed weights.
    
    Args:
        user_ratings: User's historical ratings
        book_features: Feature vector of the book
        
    Returns:
        Score between 0.0 and 1.0
    """
    weights = [0.3, 0.4, 0.3]
    return sum(w * f for w, f in zip(weights, book_features))
Rule 7: Small Functions, Small Files
Functions: Maximum 50 lines
Files: Maximum 500 lines
Classes: Maximum 300 lines
If exceeding, refactor into smaller units.

Rule 8: Consistent Error Handling
Never catch bare exceptions. Always be specific.

Wrong:

Python

try:
    result = do_something()
except:
    pass
Right:

Python

try:
    result = do_something()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
Rule 9: Type Hints Are Mandatory
All new Python code must have type hints. All TypeScript must avoid any.

Rule 10: Tests Are Not Optional
New logic requires new tests. No exceptions.

Comment Discipline
When to Comment
Comments should answer WHY, not WHAT:

Good comments explain:

Non-obvious business logic
Why a workaround exists
External API quirks
Performance decisions
Security considerations
Bad comments repeat the code:

"Set x to 5" for x = 5
"Loop through items" for for item in items
"Return the result" for return result
Comment Types (Acceptable)
1. Docstrings (mandatory for public code)

Python

def process_payment(amount: Decimal) -> PaymentResult:
    """Process a payment transaction.
    
    Args:
        amount: Payment amount in USD
        
    Returns:
        Result with transaction ID and status
        
    Raises:
        InsufficientFundsError: If account balance insufficient
    """
    ...
2. WHY comments (encouraged)

Python

# Use cosine similarity because vectors are sparse
# and magnitude matters less than direction
similarity = cosine_similarity(vec1, vec2)
3. TODO comments (with owner and ticket)

Python

# TODO(username): Implement retry logic
# See issue #123
result = api_call()
4. NOTE comments (for gotchas)

Python

# NOTE: This must run before database initialization
# See src/database/session.py line 42
setup_connection_pool()
5. Section markers (minimal, functional)

Python

# Constants

MAX_RETRIES = 3


# Helpers

def validate_input(data: dict) -> bool:
    ...


# Public API

def process(data: dict) -> Result:
    if not validate_input(data):
        raise ValueError("Invalid data")
    return _execute(data)
Comment Types (Forbidden)
1. Emoji-decorated comments

Python

# NOT ALLOWED:
# 🚀 Launch the app 🚀
# ✨ This is where the magic happens ✨
2. ASCII art banners

Python

# NOT ALLOWED:
# ============================================
# ================ SECTION ==================
# ============================================
# ############################################
# #                                          #
# #           IMPORTANT SECTION              #
# #                                          #
# ############################################
3. Redundant comments

Python

# NOT ALLOWED:
counter = 0  # Initialize counter to zero
users = []  # Empty list of users
def get_name():  # Function to get name
    return name  # Return the name
4. Commented-out code

Python

# NOT ALLOWED:
def process():
    # old_way()
    # v2_attempt()
    # x = calculate()
    # if x > 5:
    #     return x
    return new_way()
Git remembers old code. Delete it.

5. Signature comments

Python

# NOT ALLOWED:
# Author: John Doe
# Created: 2025-01-15
# Modified: 2025-01-20
# Version: 1.2.3
def process():
    ...
Git tracks all of this.

Code Structure
File Organization Pattern
Every source file should follow this order:

Python

"""Module docstring explaining purpose."""

# 1. Standard library imports
import os
from datetime import datetime
from typing import Optional

# 2. Third-party imports
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

# 3. Local imports
from src.config import settings
from src.database.models import User


# 4. Module-level constants

MAX_RETRIES = 3
DEFAULT_TIMEOUT = 30


# 5. Module-level classes/functions

class UserService:
    """Handles user operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user(self, user_id: str) -> Optional[User]:
        return self.db.query(User).get(user_id)


# 6. Private helpers (at bottom)

def _validate_email(email: str) -> bool:
    return "@" in email
Function Structure
Every function should follow this pattern:

Python

def function_name(param1: Type, param2: Type) -> ReturnType:
    """One-line summary.
    
    Longer description if needed.
    
    Args:
        param1: Description
        param2: Description
        
    Returns:
        Description
        
    Raises:
        SomeError: When this happens
    """
    # 1. Input validation
    if not param1:
        raise ValueError("param1 required")
    
    # 2. Setup
    result = []
    
    # 3. Core logic
    for item in param2:
        processed = process_item(item)
        result.append(processed)
    
    # 4. Return
    return result
Class Structure
Python

class MyService:
    """Service description."""
    
    # 1. Class constants
    MAX_ITEMS = 100
    
    # 2. Constructor
    def __init__(self, db: Session):
        self.db = db
    
    # 3. Public methods (alphabetical or by feature)
    def create(self, data: dict) -> Model:
        ...
    
    def delete(self, id: str) -> None:
        ...
    
    def get(self, id: str) -> Optional[Model]:
        ...
    
    def update(self, id: str, data: dict) -> Model:
        ...
    
    # 4. Private methods (prefixed with _)
    def _validate(self, data: dict) -> None:
        ...
    
    def _transform(self, data: dict) -> dict:
        ...
Naming Conventions
Python
Python

# Variables and functions: snake_case
user_email = "test@example.com"
def fetch_user_data(user_id: str) -> User:
    pass


# Classes: PascalCase
class BookService:
    pass


# Constants: UPPER_SNAKE_CASE
MAX_SEARCH_RESULTS = 40
DEFAULT_TIMEOUT_SECONDS = 30


# Private (single underscore)
def _internal_helper():
    pass


# Boolean variables: is_/has_/should_ prefix
is_active = True
has_completed_onboarding = False
should_show_modal = True


# Collections: plural noun
books = []
user_ids = set()
book_ratings = {}
TypeScript
TypeScript

// Variables and functions: camelCase
const userEmail = "test@example.com";
function fetchUserData(userId: string): Promise<User> { }


// Types and Interfaces: PascalCase
interface Book { }
type UserRole = 'admin' | 'user';


// Components: PascalCase
const BookCard: React.FC = () => { };


// Constants: UPPER_SNAKE_CASE
const MAX_SEARCH_RESULTS = 40;


// Boolean: is/has/should prefix
const isAuthenticated = true;
const hasCompletedOnboarding = false;


// Event handlers: handle prefix
const handleBookPress = () => { };
const handleSearch = (query: string) => { };


// Async: descriptive verb
const fetchBooks = async () => { };
const loadUserData = async () => { };
Function Naming Patterns
Prefix	Purpose	Example
get*	Retrieve data	getUserById, get_books
fetch*	Async retrieve	fetchBooks, fetch_recommendations
create*	Make new	createUser, create_rating
update*	Modify existing	updateProfile, update_book_rating
delete*	Remove	deleteAccount, delete_rating
is*	Boolean check	isValid, is_authenticated
has*	Boolean check	hasPermission, has_completed
handle*	Event handler	handleClick, handle_submit
validate*	Check validity	validateEmail, validate_input
format*	Transform for display	formatDate, format_currency
parse*	Convert from string	parseJSON, parse_iso_date
Git and Version Control
Repository Structure
text

kitabee/
    backend/
    mobile/
    docker/
    docs/
    .github/workflows/
    .gitignore
    README.md
    LICENSE
.gitignore Rules
Always ignore:

text

# Secrets
.env
.env.local
*.key
*.pem

# Dependencies
node_modules/
venv/
__pycache__/
*.pyc

# Build outputs
dist/
build/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# ML artifacts
*.pt
*.h5
*.pkl
models_artifacts/

# Data
data/raw/
data/processed/

# Testing
.pytest_cache/
.coverage
htmlcov/

# Expo
.expo/
web-build/
File Size Limits
Committed files: less than 100 MB
Use Git LFS for files greater than 100 MB
Never commit trained ML models to Git (use S3)
Never commit large datasets
Commit Message Standards
Format: Conventional Commits
text

<type>(<scope>): <subject>

<body>

<footer>
Types
Type	Use When
feat	New feature
fix	Bug fix
docs	Documentation only
style	Formatting, no code change
refactor	Code restructure, no behavior change
perf	Performance improvement
test	Add or update tests
chore	Maintenance tasks
ci	CI/CD changes
build	Build system changes
Scope
Use module or area affected:

auth, books, ratings, library, recommendations
db, cache, api, ml
mobile, web, docker
Subject Rules
Use imperative mood: "add" not "added" or "adds"
Lowercase first letter
No period at end
50 characters or less
Complete this sentence: "If applied, this commit will ___"
Examples
Good:

text

feat(auth): implement JWT-based authentication

- Add JWT token generation on login
- Add auth middleware for protected routes
- Add refresh token endpoint with 30-day expiry
- Add password hashing with bcrypt

Closes #12
text

fix(search): prevent race condition in cache invalidation

The cache was being invalidated before the DB write completed,
causing stale data to be re-cached. Now we use a transaction
to ensure atomicity.

Fixes #45
text

docs(schema): add ML feature vector documentation
Bad:

text

stuff
fixed bug
WIP
update
final version
asdf
Commit Frequency
Commit multiple times per day
Commit each logical change separately
Commit before switching tasks
Never commit half-broken code to main
Never commit changes greater than 1000 lines (split them)
Branch Strategy
Main Branches
text

main       Production-ready code (protected)
develop    Integration branch (optional for solo)
Feature Branches
Format: <type>/<short-description>

Examples:

feat/jwt-authentication
fix/search-empty-query
docs/update-readme
refactor/extract-book-service
Solo Workflow
Bash

# Start new feature
git checkout main
git pull
git checkout -b feat/book-search

# Work on feature
git add .
git commit -m "feat(books): add search endpoint"
git commit -m "test(books): add search tests"

# When done, merge to main
git checkout main
git merge feat/book-search
git push

# Delete feature branch
git branch -d feat/book-search
Python Backend Rules
Style Enforcement
Use these tools:

Formatter: black (line length: 100)
Import sorter: isort
Linter: flake8
Type checker: mypy (recommended)
Before Every Commit
Bash

black backend/src backend/tests
isort backend/src backend/tests
flake8 backend/src
mypy backend/src
Type Hints (Mandatory)
Every function must have complete type hints.

Wrong:

Python

def get_user_by_id(user_id, db):
    return db.query(User).filter(User.id == user_id).first()
Right:

Python

def get_user_by_id(user_id: str, db: Session) -> Optional[User]:
    """Fetch user by UUID."""
    return db.query(User).filter(User.id == user_id).first()
Async/Await Rules
Wrong:

Python

async def fetch_book(book_id: str) -> Book:
    time.sleep(1)  # BLOCKS EVENT LOOP
    response = requests.get(...)  # SYNCHRONOUS
    return response.json()
Right:

Python

async def fetch_book(book_id: str) -> Book:
    await asyncio.sleep(1)
    async with httpx.AsyncClient() as client:
        response = await client.get(f"/books/{book_id}")
        return response.json()
Docstring Format (Google Style)
Python

def calculate_recommendation_score(
    user_ratings: list[Rating],
    book_features: BookFeatures,
    model_type: str = "hybrid"
) -> float:
    """Calculate recommendation score for a user-book pair.
    
    Combines content-based and collaborative filtering scores
    with configurable model weights.
    
    Args:
        user_ratings: User's historical ratings (min 5 for reliable score)
        book_features: Feature vector of the book
        model_type: One of 'content', 'collaborative', 'hybrid'
    
    Returns:
        Recommendation score between 0.0 and 1.0
    
    Raises:
        ValueError: If user_ratings is empty
        InvalidModelError: If model_type is unknown
    """
    if not user_ratings:
        raise ValueError("user_ratings cannot be empty")
    ...
Import Order
Python

# 1. Standard library
import os
from datetime import datetime
from typing import Optional, List

# 2. Third-party
import numpy as np
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

# 3. Local
from src.config import settings
from src.database.models import User
from src.services.book_service import BookService
Constants
Python

# Group in module-level constants section
MAX_SEARCH_RESULTS = 40
DEFAULT_PAGE_SIZE = 20
JWT_EXPIRATION_MINUTES = 1440
BCRYPT_ROUNDS = 12

# Or group in classes if many related
class CacheKeys:
    """Redis cache key patterns."""
    
    BOOK = "book:{book_id}"
    SEARCH = "search:{query}"
    USER_RECS = "recs:user:{user_id}"
TypeScript Frontend Rules
tsconfig.json Requirements
JSON

{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true
  }
}
Type Definitions (Mandatory)
Wrong:

TypeScript

function processData(data: any): any {
  return data;
}

function getBook(id) {
  return fetchBook(id);
}
Right:

TypeScript

interface Book {
  id: string;
  title: string;
  authors: string[];
  coverUrl?: string;
  averageRating: number;
}

function formatRating(rating: number): string {
  return `${rating.toFixed(1)}/5`;
}

interface BookCardProps {
  book: Book;
  onPress: (bookId: string) => void;
}

const BookCard: React.FC<BookCardProps> = ({ book, onPress }) => {
  return <TouchableOpacity onPress={() => onPress(book.id)}>...</TouchableOpacity>;
};
React Component Rules
TypeScript

export const HomeScreen: React.FC = () => {
  // 1. Hooks at top
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const { user } = useAuth();
  
  // 2. Effects
  useEffect(() => {
    fetchBooks();
  }, []);
  
  // 3. Handlers with 'handle' prefix
  const handleBookPress = (bookId: string) => {
    navigation.navigate('BookDetails', { bookId });
  };
  
  // 4. Early returns for edge states
  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorView message={error} />;
  
  // 5. Main render
  return (
    <ScrollView>
      {books.map(book => (
        <BookCard key={book.id} book={book} onPress={handleBookPress} />
      ))}
    </ScrollView>
  );
};
Custom Hooks
TypeScript

// Naming: use<Feature>
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

// Return object (not array) for readability
export const useBooks = () => {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  
  return {
    books,
    loading,
    refetch: fetchBooks,
  };
};
Import Order
TypeScript

// 1. React
import React, { useState, useEffect } from 'react';

// 2. React Native
import { View, Text, StyleSheet } from 'react-native';

// 3. Third-party
import { useNavigation } from '@react-navigation/native';
import axios from 'axios';

// 4. Local absolute imports
import { BookCard } from '@/components/BookCard';
import { useAuth } from '@/hooks/useAuth';

// 5. Local relative imports
import { styles } from './styles';

// 6. Types (at end)
import type { Book, User } from '@/types';
File and Folder Organization
Naming Rules
Type	Convention	Example
Python files	snake_case.py	book_service.py
Python folders	snake_case/	services/, database/
TypeScript components	PascalCase.tsx	BookCard.tsx
TypeScript utilities	camelCase.ts	formatDate.ts
TypeScript folders	camelCase/ or kebab-case/	components/, book-details/
Docs	UPPER_CASE.md	README.md, RULES.md
Backend Structure
text

backend/src/
    api/routes/          # One file per resource
        auth.py
        books.py
        ratings.py
    services/            # Business logic
    database/models/     # One file per entity
        user.py
        book.py
    schemas/             # Pydantic models
    ml/                  # ML models
Frontend Structure
text

mobile/src/
    screens/             # One file per screen
        HomeScreen.tsx
        BookDetailsScreen.tsx
    components/          # Reusable UI
        common/
        books/
    services/            # API clients
    hooks/               # Custom hooks
    theme/               # Theme tokens, context, hook
        tokens.ts
        ThemeContext.tsx
        spacing.ts
        typography.ts
        radius.ts
    types/               # TypeScript types
API Design Rules
RESTful URL Structure
Right:

text

GET    /api/v1/books
GET    /api/v1/books/{id}
POST   /api/v1/books
PATCH  /api/v1/books/{id}
DELETE /api/v1/books/{id}
GET    /api/v1/books/{id}/similar
Wrong:

text

GET  /api/v1/getBooks
POST /api/v1/book/create
GET  /api/v1/books/{id}/get_similar
GET  /api/v1/book
HTTP Status Codes
Code	Use When
200	Successful GET/PATCH
201	Successful POST (created)
204	Successful DELETE (no content)
400	Invalid request
401	Not authenticated
403	Authenticated but forbidden
404	Not found
409	Conflict (duplicate)
422	Validation error
429	Rate limited
500	Server error
503	External service unavailable
Response Format (Mandatory)
Success:

JSON

{
  "success": true,
  "data": { },
  "meta": {
    "timestamp": "2025-01-15T10:30:00Z",
    "version": "v1"
  }
}
Error:

JSON

{
  "success": false,
  "error": {
    "code": "BOOK_NOT_FOUND",
    "message": "Book with ID xyz not found",
    "details": {}
  },
  "meta": {
    "timestamp": "2025-01-15T10:30:00Z"
  }
}
API Versioning
Always version: /api/v1/...
Breaking changes = new version (v2)
Deprecation notice: 30 days minimum
Database Rules
Query Rules
Right:

Python

# Use ORM (prevents SQL injection)
user = db.query(User).filter(User.email == email).first()

# Parameterized queries for raw SQL
result = db.execute(
    text("SELECT * FROM users WHERE email = :email"),
    {"email": email}
)

# Eager loading to prevent N+1
users = db.query(User).options(selectinload(User.ratings)).all()
Wrong:

Python

# String concatenation (SQL injection risk)
query = f"SELECT * FROM users WHERE email = '{email}'"

# Returns all columns when few needed
users = db.query(User).all()

# N+1 queries
for user in users:
    ratings = db.query(Rating).filter(Rating.user_id == user.id).all()
Migration Rules
Test migrations on dev DB first
Make migrations reversible (write downgrade)
Add nullable columns first, backfill, then set NOT NULL
Review auto-generated migrations before applying
Never edit applied migrations (create new one)
Index Rules
Index all foreign keys
Index columns in WHERE clauses
Composite indexes for multi-column queries
Don't over-index (slows writes)
Monitor with EXPLAIN ANALYZE
Security Rules
Password Rules
Right:

Python

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash password using bcrypt with cost factor 12."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Verify plain password against bcrypt hash."""
    return pwd_context.verify(plain, hashed)
Wrong:

Python

# NEVER store plain text
user.password = password

# NEVER use weak hashing
import hashlib
hashed = hashlib.md5(password.encode())
hashed = hashlib.sha256(password.encode())  # Unsalted

# NEVER log passwords
logger.info(f"User login: {email} with password {password}")
JWT Rules
Use strong secret (256-bit random)
Short access token expiry (24h max)
Refresh tokens for renewal
Store in Authorization header (not cookies for API)
Never put sensitive data in JWT payload
Input Validation
Right:

Python

from pydantic import BaseModel, EmailStr, Field, validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=100)
    name: str = Field(min_length=2, max_length=100)
    
    @validator('password')
    def password_complexity(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError('Password needs uppercase')
        return v
Sensitive Data Handling
HTTPS only in production
Sanitize logs (no passwords, tokens, PII)
Validate all user input
Use CORS whitelist
Rate limit auth endpoints (5/min)
Never log JWT tokens
Never expose internal errors to users
Never trust client-side validation alone
Testing Standards
Coverage Requirements
Backend: 70%+ coverage (target 80%)
Critical paths: 100% coverage (auth)
Frontend: Test complex logic (hooks, utilities)
Don't test framework code
Test Structure (Arrange-Act-Assert)
Python

def test_search_books_returns_results():
    # Arrange
    query = "sapiens"
    mock_client = Mock()
    mock_client.search.return_value = [{"title": "Sapiens"}]
    service = BookService(client=mock_client)
    
    # Act
    results = await service.search_books(query)
    
    # Assert
    assert len(results) == 1
    assert results[0]["title"] == "Sapiens"
    mock_client.search.assert_called_once_with(query)
Test Naming
Format: test_<what>_<condition>_<expected>

Right:

Python

def test_hash_password_returns_bcrypt_hash():
def test_verify_password_with_correct_password_returns_true():
def test_verify_password_with_wrong_password_returns_false():
def test_search_books_with_empty_query_raises_error():
def test_create_user_with_duplicate_email_returns_409():
Wrong:

Python

def test1():
def test_user():
def test_it_works():
Test Isolation
Each test independent (any order)
Use fixtures for setup
Clean up after tests
Use test database (never production)
Tests should never affect each other
Documentation Standards
When to Add Comments
Add comments to explain:

Non-obvious business logic
Why a workaround exists
External API quirks
Performance decisions
Complex algorithms
Do NOT add comments for:

Obvious code
Repeating what code does
Old code (delete it)
Signatures (Git tracks this)
Function Documentation
Every public function/class MUST have:

Docstring
Args descriptions
Return description
Raises (if any)
Example (if non-obvious)
README Updates
Update README when:

Adding new setup step
Changing environment variables
Adding new commands
Changing project structure
Change Log
Track breaking changes in CHANGELOG.md:

Markdown

## [1.2.0] - 2025-02-15

### Added
- Neural recommender endpoint

### Changed
- Auth token expiry: 12h to 24h

### Deprecated
- /api/v1/users/list (use /api/v1/users instead)

### Fixed
- Search returning duplicates
Performance Rules
Backend
Do:

Use async for I/O (DB, API calls)
Cache expensive computations (Redis)
Use database indexes on frequently queried columns
Paginate large result sets
Use selectinload to prevent N+1
Compress responses (gzip via Nginx)
Do NOT:

Block async functions with sync code
Fetch entire tables (SELECT *)
Skip pagination on lists
Cache without TTL (memory leak)
Frontend
Do:

Use React.memo for expensive components
Use useCallback for stable function references
Use useMemo for expensive calculations
Lazy load screens (React.lazy)
Debounce user input (search)
Use FlatList for long lists
Do NOT:

Fetch inside render (use useEffect)
Create new objects/arrays in render
Use inline styles for repeated components
Load all data at once (paginate)
Response Time Targets
Operation	Target
Cached endpoint	less than 100ms
DB query	less than 50ms
External API call	less than 2s (with fallback)
Full page load (web)	less than 2s
Time to interactive (mobile)	less than 3s
Error Handling
Backend
Right:

Python

try:
    user = await get_user(user_id)
except UserNotFoundError:
    raise HTTPException(status_code=404, detail="User not found")
except DatabaseError as e:
    logger.error(f"DB error: {e}")
    raise HTTPException(status_code=500, detail="Internal error")


# Return meaningful errors
raise HTTPException(
    status_code=422,
    detail={
        "code": "INVALID_RATING",
        "message": "Rating must be between 1 and 5",
        "field": "rating"
    }
)
Wrong:

Python

# Never catch all exceptions silently
try:
    ...
except:
    pass

# Never expose internal errors
except Exception as e:
    return {"error": str(e)}
Frontend
Right:

TypeScript

try {
  const books = await bookService.search(query);
  setBooks(books);
} catch (error) {
  if (error.response?.status === 401) {
    navigation.navigate('Login');
  } else if (error.response?.status === 429) {
    showToast('Too many requests. Please wait.');
  } else {
    showToast('Something went wrong. Please try again.');
  }
  console.error('Search error:', error);
}
Logging Levels
Level	Use When
DEBUG	Dev only, verbose
INFO	Normal operations
WARNING	Recoverable issues
ERROR	Failed operations
CRITICAL	System failures
Logging Format
Python

logger.info(
    "Book search completed",
    extra={
        "query": query,
        "user_id": user_id,
        "results_count": len(results),
        "duration_ms": duration
    }
)
Never Log
Passwords
JWT tokens
Credit card numbers
Full PII
API keys
Dependency Management
Adding Dependencies
Before adding a package, ask:

Do we really need it?
Is it actively maintained (last commit less than 6 months)?
How many stars/downloads?
What's the bundle size impact?
Are there security vulnerabilities?
Check with:

Bash

# Python
pip install pip-audit
pip-audit

# Node
npm audit
Version Pinning
Right:

text

# Python: exact versions for production
fastapi==0.115.4
sqlalchemy==2.0.36

# Node: caret for minor updates
"react-native": "^0.85.3"
Wrong:

text

# Never use loose versions in production
fastapi>=0.100.0
fastapi
Update Strategy
Security patches: Immediate
Minor updates: Weekly review
Major updates: Batch, test thoroughly
Automate with Dependabot
Environment and Secrets
.env Rules
Structure:

text

# Database
DATABASE_URL=postgresql://...

# Cache
REDIS_URL=redis://localhost:6379

# External APIs
GOOGLE_BOOKS_API_KEY=xxx
Rules:

.env in .gitignore (ALWAYS)
.env.example committed (template)
Comment purpose of each var
Group related vars
Never commit real secrets
Never share via chat/email
Secret Rotation
Rotate secrets:

Every 90 days (best practice)
Immediately on breach
When team member leaves
Forbidden Practices
The Absolute Never List
1. Never use emojis in code

2. Never use decorative comment blocks

3. Never commit secrets

If accidentally committed:

Bash

git rm --cached .env
git commit -m "chore: remove accidentally committed .env"
# Then ROTATE the exposed secret immediately
4. Never use console.log or print in production

Wrong:

TypeScript

console.log("User data:", user);
Right:

TypeScript

logger.info("User data fetched", { userId: user.id });
5. Never catch all exceptions silently

Wrong:

Python

try:
    do_something()
except:
    pass
Right:

Python

try:
    do_something()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
    raise
6. Never trust user input

Wrong:

Python

query = f"SELECT * FROM users WHERE id = {user_id}"
Right:

Python

query = "SELECT * FROM users WHERE id = :id"
db.execute(text(query), {"id": user_id})
7. Never hardcode configuration

Wrong:

Python

API_URL = "http://localhost:8000"
Right:

Python

API_URL = os.getenv("API_URL", "http://localhost:8000")
8. Never use any in TypeScript (except truly dynamic)

Wrong:

TypeScript

function process(data: any): any { }
Right:

TypeScript

function process<T>(data: T): T { }
// Or use unknown with type guards
function process(data: unknown): Book { }
9. Never commit dead code

Wrong:

Python

def get_user(id):
    # user = old_way(id)
    # if user:
    #     return user
    return new_way(id)
Right:

Python

def get_user(id):
    return new_way(id)
Git remembers old code.

10. Never push directly to main without review

11. Never skip tests to save time (you'll pay 10x later)

12. Never ignore linter warnings

13. Never hardcode hex color values in components

All color values in components and screens must come from semantic
theme tokens via the useTheme hook. Raw hex is only permitted inside
theme/tokens.ts.

Wrong:

TypeScript

<View style={{ backgroundColor: '#252542' }}>
  <Text style={{ color: '#ffffff' }}>Title</Text>
</View>
Right:

TypeScript

const { theme } = useTheme();

<View style={{ backgroundColor: theme.background.card }}>
  <Text style={{ color: theme.text.primary }}>Title</Text>
</View>
14. Never introduce a second brand accent color

Amber (#FFC93C) is the only brand voltage. Do not add new accent
colors. Do not use amber decoratively. Scarcity is the point.

15. Never use rounded corners on primary CTAs or cards

borderRadius on primary buttons and book cards is always 0.
No exceptions. See design.md.

Pre-Commit Checklist
Before running git commit, verify:

Code Quality
 Auto-formatted (black/prettier)
 Linter passing (flake8/eslint)
 Type checks passing (mypy/tsc)
 No console.log / print statements
 No commented-out code
 No TODO without ticket link
 No emojis in code
 No decorative comment blocks
 No hardcoded hex values in components (design token audit)
Testing
 All tests pass locally
 New tests added for new logic
 Coverage not decreased
Security
 No secrets in code
 No hardcoded URLs/keys
 Input validation present
 Auth checks in place
Documentation
 Docstrings for new functions
 README updated if needed
Git
 Meaningful commit message (Conventional Commits)
 Correct branch
 Files intentionally staged
 .env NOT staged (double check)
Theme & Design (Frontend only)
 Every new component uses useTheme hook
 No raw hex values outside theme/tokens.ts
 SplashScreen and PersonalizingScreen force dark mode
 No new spacing values outside spacing token ladder
 No new border radius values outside radius token scale
 Primary CTA borderRadius is 0
Debugging Standards
Debug-Friendly Code Practices
Write code that is easy to debug from the start:

1. Descriptive variable names

Wrong:

Python

x = get_data()
y = process(x)
z = format(y)
return z
Right:

Python

raw_books = fetch_books_from_api()
enriched_books = enrich_with_metadata(raw_books)
formatted_response = format_for_client(enriched_books)
return formatted_response
2. Early returns for edge cases

Wrong:

Python

def process_user(user):
    if user is not None:
        if user.is_active:
            if user.has_permission:
                return do_something(user)
            else:
                return None
        else:
            return None
    else:
        return None
Right:

Python

def process_user(user: Optional[User]) -> Optional[Result]:
    if user is None:
        return None
    
    if not user.is_active:
        return None
    
    if not user.has_permission:
        return None
    
    return do_something(user)
3. Small, focused functions

Each function should do one thing. If you need to explain what a function does with "and", split it.

Wrong:

Python

def fetch_and_process_and_save_user(user_id):
    # 100 lines doing three things
    pass
Right:

Python

def fetch_user(user_id: str) -> User:
    pass

def process_user_data(user: User) -> ProcessedUser:
    pass

def save_processed_user(user: ProcessedUser) -> None:
    pass
4. Meaningful log messages

Wrong:

Python

logger.info("Done")
logger.error("Error")
logger.debug("Value: " + str(x))
Right:

Python

logger.info("Book search completed", extra={
    "query": query,
    "results_count": len(results),
    "duration_ms": duration
})

logger.error("Failed to fetch book from Google Books API", extra={
    "book_id": book_id,
    "error": str(e),
    "attempt": attempt_number
})
5. Use structured logging

Wrong:

Python

print(f"User {user.id} did {action} at {time}")
Right:

Python

logger.info("User action", extra={
    "user_id": user.id,
    "action": action,
    "timestamp": time
})
6. Explicit error messages

Wrong:

Python

if not valid:
    raise ValueError("Invalid")
Right:

Python

if not valid:
    raise ValueError(
        f"Rating must be between 1 and 5, got {rating}"
    )
7. Guard clauses

Wrong:

Python

def calculate_discount(price, user):
    if user is not None:
        if user.is_premium:
            return price * 0.8
    return price
Right:

Python

def calculate_discount(price: float, user: Optional[User]) -> float:
    if user is None or not user.is_premium:
        return price
    
    return price * 0.8
Debug Toolkit
Recommended tools:

Python: pdb, ipdb, VS Code debugger
TypeScript: Chrome DevTools, VS Code debugger, React DevTools
API: Postman, Thunder Client, Swagger UI
DB: pgAdmin, DBeaver
Logs: Loguru (Python), structured JSON logs
Debug Workflow
Reproduce the bug consistently
Read the error message carefully
Check logs for context
Add strategic print/log statements
Use debugger (breakpoints, step through)
Isolate the smallest failing case
Fix root cause (not just symptom)
Write a test to prevent regression
Remove debug prints/logs before commit
Enforcement Tools
Backend (Python)
Install dev tools:

Bash

pip install black isort flake8 mypy pre-commit
Setup pre-commit hooks:

Bash

pre-commit install
.pre-commit-config.yaml:

YAML

repos:
  - repo: https://github.com/psf/black
    rev: 24.10.0
    hooks:
      - id: black
        language_version: python3.11
  
  - repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
      - id: isort
  
  - repo: https://github.com/PyCQA/flake8
    rev: 7.1.1
    hooks:
      - id: flake8
Frontend (TypeScript)
VS Code settings (.vscode/settings.json):

JSON

{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
Git Hooks
.git/hooks/pre-commit (make executable):

Bash

#!/bin/bash
cd backend && black --check src/ && flake8 src/
cd ../mobile && npm run lint
VS Code Settings (Recommended)
JSON

{
  "editor.formatOnSave": true,
  "editor.rulers": [100],
  "editor.tabSize": 2,
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "typescript.tsdk": "node_modules/typescript/lib",
  "eslint.validate": ["javascript", "typescript", "typescriptreact"]
}
Design Token Rules
This section is mandatory for all frontend work. It enforces the
Kitabee design system defined in design.md.

The Core Rule
Every color, spacing, radius, and typography value used in a component
or screen must come from a design token. Raw values in component files
are a build-breaking violation.

Token Files (Single Source of Truth)
text

mobile/src/theme/
    tokens.ts        Raw color palette + darkTheme + lightTheme objects
    ThemeContext.tsx  ThemeProvider + useTheme hook
    spacing.ts       8px ladder (xxxs through super)
    typography.ts    All type scale tokens
    radius.ts        All border radius tokens
No other file defines color, spacing, radius, or typography values.

Using Tokens in Components
TypeScript

// Every component that renders visual elements must:
// 1. Import useTheme
// 2. Destructure theme
// 3. Reference only semantic tokens

import { useTheme } from '@/theme/ThemeContext';

const BookCard: React.FC<BookCardProps> = ({ book }) => {
  const { theme } = useTheme();
  
  return (
    <View style={{
      backgroundColor: theme.background.card,
      borderWidth: 1,
      borderColor: theme.border.default,
      borderRadius: 0,
      padding: spacing.sm,
    }}>
      <Text style={{ color: theme.text.primary, ...typography['title-md'] }}>
        {book.title}
      </Text>
      <Text style={{ color: theme.text.secondary, ...typography['body-sm'] }}>
        {book.author}
      </Text>
    </View>
  );
};
Semantic Token Reference (Summary)
Full reference is in design.md. Quick guide:

What you need	Token to use
Screen background	theme.background.primary
Card background	theme.background.card
Elevated panel	theme.background.elevated
Sunken/inset area	theme.background.sunken
Primary text	theme.text.primary
Body/secondary text	theme.text.secondary
Muted/caption text	theme.text.muted
Disabled text	theme.text.disabled
Text on amber CTA	theme.text.onPrimary
Link text	theme.text.link
Input placeholder	theme.text.placeholder
Default border	theme.border.default
Subtle border	theme.border.subtle
Focus ring	theme.border.focus
Input border	theme.border.input
Input focus border	theme.border.inputFocus
Primary CTA bg	theme.brand.primary
CTA press state	theme.brand.primaryActive
Success color	theme.brand.semanticSuccess
Error color	theme.brand.semanticWarning
Info color	theme.brand.semanticInfo
Screens That Must Always Force Dark Mode
TypeScript

// SplashScreen.tsx and PersonalizingScreen.tsx only

// These screens bypass the user theme preference.
// They always render on the dark canvas (#1a1a2e).
// Import darkTheme directly. Do not use useTheme.

import { darkTheme } from '@/theme/tokens';

const SplashScreen: React.FC = () => {
  const theme = darkTheme; // forced — not from context
  ...
};
What Never Changes Between Modes
These values are immutable. They must be identical in dark and light:

text

theme.brand.primary          #FFC93C
theme.brand.primaryActive    #E6A800
theme.brand.onPrimary        #1a1a2e
theme.border.focus           #FFC93C
theme.border.inputFocus      #FFC93C
theme.brand.semanticSuccess  #03904a
theme.brand.semanticWarning  #f13a2c
theme.brand.semanticInfo     #4c98b9
Star fill color              #FFC93C
Tab active color             #FFC93C
Primary CTA border radius    0px
Token Audit Command
Run this before every PR to catch raw hex values in components:

Bash

# Finds hardcoded hex values in component and screen files
# Should return zero results
grep -rn "#[0-9a-fA-F]\{3,6\}" mobile/src/screens/ mobile/src/components/ \
  --include="*.tsx" --include="*.ts" \
  | grep -v "theme/tokens.ts" \
  | grep -v ".test."
Zero results means the audit passes. Any result is a violation.

Spacing Token Usage
TypeScript

import { spacing } from '@/theme/spacing';

// Right
paddingHorizontal: spacing.sm   // 24px
marginBottom: spacing.xs        // 16px
gap: spacing.xxs                // 8px

// Wrong
paddingHorizontal: 24
marginBottom: 16
gap: 8
Typography Token Usage
TypeScript

import { typography } from '@/theme/typography';

// Right
<Text style={{ ...typography['body-md'], color: theme.text.primary }}>
  {content}
</Text>

// Wrong
<Text style={{ fontSize: 14, fontWeight: '400', color: '#ffffff' }}>
  {content}
</Text>
Radius Token Usage
TypeScript

import { radius } from '@/theme/radius';

// Right
borderRadius: radius.none    // 0  — cards, CTAs
borderRadius: radius.sm      // 4  — inputs
borderRadius: radius.lg      // 8  — bottom sheets (top only)
borderRadius: radius.full    // 9999 — avatars, badge pills

// Wrong
borderRadius: 0
borderRadius: 4
borderRadius: 8
borderRadius: 9999
React Native Mobile Rules
Rules specific to the Expo React Native frontend. These supplement the
TypeScript Frontend Rules above.

Navigation Rules
TypeScript

// Use typed navigation params. Never use untyped navigation.

// types/navigation.ts — define all routes and params here
export type RootStackParamList = {
  Splash: undefined;
  Welcome: undefined;
  Login: undefined;
  Register: undefined;
  Home: undefined;
  BookDetails: { bookId: string };
  Library: undefined;
  Search: undefined;
  Insights: undefined;
  Profile: undefined;
  Settings: undefined;
};

// In components
import { NativeStackScreenProps } from '@react-navigation/native-stack';
type Props = NativeStackScreenProps<RootStackParamList, 'BookDetails'>;

const BookDetailsScreen: React.FC<Props> = ({ route, navigation }) => {
  const { bookId } = route.params;
  ...
};
StyleSheet Rules
TypeScript

// Use StyleSheet.create for static styles.
// Use inline style only for dynamic theme-driven values.

// Right
const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingHorizontal: spacing.sm,
  },
});

// Then in render, merge static + dynamic
<View style={[styles.container, { backgroundColor: theme.background.primary }]}>

// Wrong — all inline (performance + readability issue)
<View style={{ flex: 1, paddingHorizontal: 24, backgroundColor: '#1a1a2e' }}>
FlatList Rules
TypeScript

// Always use FlatList for lists longer than 10 items.
// Never use ScrollView with .map() for long lists.
// Always provide keyExtractor. Always provide getItemLayout if items
// are fixed height (dramatically improves performance).

<FlatList
  data={books}
  keyExtractor={(item) => item.id}
  renderItem={({ item }) => <BookCard book={item} />}
  getItemLayout={(_, index) => ({
    length: BOOK_CARD_HEIGHT,
    offset: BOOK_CARD_HEIGHT * index,
    index,
  })}
  showsVerticalScrollIndicator={false}
/>
Image Rules
TypeScript

// Use expo-image for all images. Not React Native's Image component.
// expo-image has built-in caching, blurhash placeholders, and
// significantly better performance.

import { Image } from 'expo-image';

<Image
  source={{ uri: book.coverUrl }}
  style={{ width: 120, height: 180 }}
  contentFit="cover"
  placeholder={book.blurhash}
  transition={200}
/>
AsyncStorage Rules
TypeScript

// Wrap all AsyncStorage calls in try/catch.
// Never assume storage is available.
// Use typed helper functions instead of calling AsyncStorage directly.

// storage/themeStorage.ts
import AsyncStorage from '@react-native-async-storage/async-storage';

const THEME_KEY = 'kitabee_theme_mode';

export const saveThemeMode = async (mode: ThemeMode): Promise<void> => {
  try {
    await AsyncStorage.setItem(THEME_KEY, mode);
  } catch (error) {
    // Storage failure is non-fatal — theme defaults gracefully
    console.error('Failed to save theme preference:', error);
  }
};

export const loadThemeMode = async (): Promise<ThemeMode | null> => {
  try {
    const stored = await AsyncStorage.getItem(THEME_KEY);
    return stored as ThemeMode | null;
  } catch (error) {
    return null;
  }
};
Keyboard Handling Rules
TypeScript

// Wrap forms in KeyboardAvoidingView.
// Use behavior="padding" on iOS, behavior="height" on Android.
// Dismiss keyboard on scroll.

import { KeyboardAvoidingView, Platform, ScrollView, Keyboard } from 'react-native';

<KeyboardAvoidingView
  behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
  style={{ flex: 1 }}
>
  <ScrollView
    keyboardShouldPersistTaps="handled"
    onScrollBeginDrag={Keyboard.dismiss}
  >
    {/* form fields */}
  </ScrollView>
</KeyboardAvoidingView>
Touch Target Rules
TypeScript

// All interactive elements must meet minimum touch target sizes.
// See design.md Accessibility Standards.

// Primary CTA: height 48px minimum
// Tab bar items: 44px effective area
// Icon buttons: wrap in 44x44 touchable

<TouchableOpacity
  style={{ minHeight: 44, minWidth: 44, justifyContent: 'center', alignItems: 'center' }}
  onPress={handlePress}
  activeOpacity={0.7}
>
  <Icon name="close" size={24} color={theme.text.secondary} />
</TouchableOpacity>
Platform-Specific Code Rules
TypeScript

// Isolate platform differences with Platform.OS or platform-specific files.
// Never scatter Platform.OS checks throughout component logic.

// Good: isolated at usage point
const shadowStyle = Platform.select({
  ios: {
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
  },
  android: {
    elevation: 4,
  },
});

// Good: platform-specific file
// Component.ios.tsx
// Component.android.tsx
Safe Area Rules
TypeScript

// All screens must handle safe areas.
// Use useSafeAreaInsets for fine-grained control.
// Never use hardcoded status bar heights.

import { useSafeAreaInsets } from 'react-native-safe-area-context';

const HomeScreen: React.FC = () => {
  const insets = useSafeAreaInsets();
  
  return (
    <View style={{ flex: 1, paddingTop: insets.top }}>
      ...
    </View>
  );
};
Animation Rules
TypeScript

// Use React Native Reanimated 2+ for all animations.
// Never use the Animated API from React Native core (deprecated behavior).
// Respect reduce motion accessibility preference.

import Animated, { useSharedValue, withTiming } from 'react-native-reanimated';
import { useReducedMotion } from 'react-native-reanimated';

const ShimmerLoader: React.FC = () => {
  const reduceMotion = useReducedMotion();
  const opacity = useSharedValue(1);
  
  useEffect(() => {
    if (reduceMotion) return; // skip animation for accessibility
    opacity.value = withTiming(0.4, { duration: 700 });
  }, []);
  
  ...
};
State Management Rules
TypeScript

// Local UI state: useState
// Server/async state: React Query (TanStack Query)
// Global app state: Context API (auth, theme)
// Do not introduce Redux or Zustand unless Context becomes genuinely
// insufficient. Document the reason in a comment if you do.

// React Query usage pattern
import { useQuery } from '@tanstack/react-query';

const useBookDetails = (bookId: string) => {
  return useQuery({
    queryKey: ['book', bookId],
    queryFn: () => bookService.getById(bookId),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
Expo-Specific Rules
TypeScript

// Use Expo SDK modules over bare React Native equivalents
// where they exist. Expo modules are tested against the
// managed workflow and have better cross-platform behavior.

// Prefer:
// expo-image          over react-native Image
// expo-font           over custom font loading
// expo-camera         over react-native-camera
// expo-notifications  over other notification libraries
// expo-haptics        for haptic feedback

// Always check Expo SDK compatibility before adding a bare
// React Native library. Some are incompatible with managed workflow.
Claude Code Interaction Rules
These rules govern how Claude Code is used during development.
They exist to prevent drift, token waste, and scope creep.

Session Start Protocol
Every Claude Code session begins with:

text

Read the following files. Confirm you have read them. Do not summarize.
- PRD.md
- TECHSPEC.md
- APPFLOW.md
- schema.md
- design.md
- implementationplan.md
- tracker.md
- rules.md
Do not give Claude Code a task until it has confirmed it has read
all eight context files.

Command Style
Write commands as direct imperatives. No preamble. No pleasantries.

Right:

text

Build component: BookCard
Spec: design.md Component Library / Book Card
Use useTheme hook. No hardcoded hex.
Wrong:

text

Hey Claude, could you please help me build the BookCard component?
I was thinking it should probably follow the design system. What do
you think would be the best approach?
Scope Control
Each command covers exactly one unit of work:

One component, or
One screen, or
One service file, or
One bug fix
Do not ask Claude to build multiple components in one command.
Large scope = large drift risk.

Right:

text

Build component: PrimaryButton
Spec: design.md Buttons / Primary Button
Wrong:

text

Build all the button components and the BookCard and the tab bar
and also set up navigation
Preventing Unsolicited Changes
Add this line to commands for existing files:

text

Only modify [FileName]. Do not touch other files.
Claude Code must not:

Refactor files it was not asked to touch
Install new dependencies without being asked
Create new files beyond what was specified
Add configuration it was not asked for
When Claude Drifts
If Claude produces output that deviates from design.md or rules.md:

text

Stop. This does not match [design.md / rules.md / TECHSPEC.md].
Specifically: [describe the deviation].
Redo this following the spec exactly.
Do not accept and manually patch drifted output. Always correct at source.

Tracker Updates
After each completed task:

text

Update tracker.md. Mark complete: [task name].
Do not change any other section of the file.
Never let tracker.md fall behind. It is the source of truth for
what has been built.

Audit Commands
Run these periodically to catch accumulated drift:

text

Audit all files in mobile/src/components/ and mobile/src/screens/.
Find any hardcoded hex values. List every file and line number.
Fix all violations. Use semantic theme tokens only.
text

Audit all files in mobile/src/screens/.
Find any screen missing the useTheme hook.
List them. Fix them.
text

Confirm SplashScreen and PersonalizingScreen force darkTheme directly
and do not use useTheme from context. Show me the relevant code.
Fix if incorrect.
What Claude Code Must Never Do
Add emojis to source code files
Add decorative comment blocks
Hardcode hex color values outside theme/tokens.ts
Use rounded corners on primary CTAs
Introduce dependencies not in TECHSPEC.md without explicit approval
Modify files outside the scope of the current command
Invent design decisions not covered in design.md
Skip the useTheme hook in any component or screen
Handling Ambiguity
If a spec is ambiguous, Claude Code asks before building:

text

Ambiguity in [spec reference]: [describe the ambiguity].
Which interpretation is correct?
A) [option A]
B) [option B]
Do not allow Claude to make assumptions on ambiguous design or
architecture decisions. Always resolve before building.

Token Efficiency
Keep commands short. Context is already loaded from the eight
reference files. Commands should reference those files rather than
restating their contents.

Right:

text

Build screen: SearchScreen
Spec: design.md Screen-by-Screen / Search Screen + APPFLOW.md
Wrong:

text

Build the search screen. It should have a dark background of #1a1a2e
in dark mode and the input should have a focus border of #FFC93C and
the placeholder text should be #666680 and...
The spec files contain all of this. Reference them. Do not repeat them.

Appendix
Rule Update Process
To modify these rules:

Discuss impact
Update this document
Update tooling (linters, hooks)
Update Change Log
Notify team
Rule Exceptions
When a rule doesn't fit:

Document the exception in code
Explain WHY it's OK to break
Add link to discussion
Get review before merging
Example:

Python

# NOTE: Breaking naming convention here because we're
# matching Google Books API response field exactly.
# See RULES.md section 11.4 for exception guidelines.
volumeInfo = response['volumeInfo']  # noqa
Related Documents
PRD.md
TECHSPEC.md
SCHEMA.md
IMPLEMENTATION_PLAN.md
TRACKER.md
DESIGN.md
APPFLOW.md
Change Log
Version	Date	Author	Changes
1.0	[Prev Date]	[Your Name]	Initial engineering rules
2.0	[Prev Date]	[Your Name]	Removed emoji/decoration rules; enforced clean code
3.0	[Today]	[Your Name]	Added Design Token Rules, React Native Mobile Rules, Claude Code Interaction Rules; updated pre-commit checklist; updated folder structure; added forbidden practices 13-15
Summary
The Kitabee code standard is simple:

Write code that solves the problem
Add comments that explain WHY
No emojis, no decorations, no noise
Small functions, small files, clear names
Type everything
Test everything
Handle errors specifically
Never commit secrets
Follow the pre-commit checklist
Debug-friendly from the start
Every color from a semantic token — never raw hex in components
Every spacing from the token ladder — never ad-hoc values
Every new screen and component uses useTheme
SplashScreen and PersonalizingScreen always force dark mode
Give Claude Code one task at a time with full spec references
Follow these rules and your code will be:

Professional
Readable
Debuggable
Maintainable
Consistent across every theme
Portfolio-ready
That's the standard. No exceptions.





