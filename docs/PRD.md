
# 📄 Kitabee — Product Requirements Document

> **Document Version:** 2.0
> **Last Updated:** [Today's Date]
> **Author:** [Your Name]
> **Status:** 🟢 Active Development
> **Timeline:** 5 Weeks (MVP)

---

## 📚 Table of Contents

1. [Executive Summary](#-executive-summary)
2. [Problem Statement](#-problem-statement)
3. [Target Users](#-target-users)
4. [Product Vision & Goals](#-product-vision--goals)
5. [Success Metrics](#-success-metrics)
6. [Feature Scope (MVP)](#-feature-scope-mvp)
7. [Out of Scope](#-out-of-scope)
8. [User Stories](#-user-stories)
9. [User Flows](#-user-flows)
10. [Technical Architecture](#-technical-architecture)
11. [AI/ML Approach](#-aiml-approach)
12. [Data Strategy](#-data-strategy)
13. [UX & Design Principles](#-ux--design-principles)
14. [Constraints & Assumptions](#-constraints--assumptions)
15. [Risks & Mitigation](#-risks--mitigation)
16. [Milestones & Timeline](#-milestones--timeline)
17. [Future Roadmap](#-future-roadmap)
18. [Appendix](#-appendix)

---

## 🎯 Executive Summary

**Kitabee** is an AI-powered book and comics discovery platform that helps readers and comic fans find their next great read through personalized recommendations, Netflix-style themed collections, and free access to public domain content via Internet Archive.

### The One-Liner
> *"Bee curious. Bee well-read."*

### The Elevator Pitch
Millions of readers and comic fans struggle to find content they will love. Existing platforms rely on basic filters, paid promotions, or shallow "you liked X so try Y" logic. Kitabee combines **content-based filtering, collaborative filtering, neural network personalization, and Netflix-style themed collection curation** — delivering explainable recommendations organized into catchy, mood-driven rows that feel personal and delightful. Users can also read thousands of public domain books and comics for free, directly inside the app.

### Key Differentiators
1. **🧠 Multi-Model AI** — 8+ techniques working together
2. **🎬 Netflix-Style Collections** — Themed rows with catchy titles like "Epic Worlds Built From Scratch" or "Dark But You Cannot Put It Down"
3. **📚 Books + Comics** — One app for both, unified discovery experience
4. **📖 Free Reading** — Public domain books and comics via Internet Archive
5. **🔢 Series Order Guide** — Know exactly what order to read any series or trilogy
6. **🔍 Explainable AI** — Users see WHY each book or comic is recommended
7. **📊 Reading DNA** — Personality-driven insights, not just genre tags
8. **🌐 Cross-Platform** — Web + Mobile from single codebase
9. **⚡ Real-Time API Integration** — Fresh data from multiple external sources
10. **🎯 Zero Cold-Start Problem** — Smart onboarding survey

---

## ❓ Problem Statement

### The Core Problem
> **"There are too many books and comics, and no reliable way to find the RIGHT one for ME — or know where to even start."**

### Supporting Evidence
- 📚 **4 million+ new books** published annually worldwide
- 🦸 **Thousands of comic series** with complex reading orders confuse new readers
- 📊 **74% of readers** cite "finding good books" as their top frustration (Pew Research)
- ⏱️ Average reader spends **30+ minutes** deciding on a next book
- 🔢 New comic readers often **quit** because they cannot figure out where to start in a series
- 💰 **$2.8B lost annually** in returns from mismatched book purchases
- 📱 Existing apps show **60%+ generic bestsellers** vs personalized picks
- 🎬 No book app presents recommendations in the **engaging Netflix-style row format** readers are already comfortable with

### Current Solutions & Their Gaps

| Platform | Approach | Gap |
|----------|----------|-----|
| **Goodreads** | Social ratings + basic recs | Outdated UX, generic suggestions, books only |
| **Amazon** | Purchase-based recs | Biased toward monetization |
| **StoryGraph** | Mood-based filtering | Manual tagging burden, books only |
| **Marvel Unlimited** | Comics subscription | Paid, Marvel only, no discovery guidance |
| **Bookstore staff** | Personal knowledge | Does not scale, limited hours |
| **Instagram/BookTok** | Social proof | Trend-driven, not personalized |
| **Google/Reddit** | Manual search | User must know what to search for |

### The Kitabee Solution
Combine the best of all worlds: **AI-driven personalization** + **Netflix-style themed collections** + **books and comics unified** + **free public domain reading** + **series order guidance** + **modern UX**.

---

## 👥 Target Users

### Primary Persona: "The Curious Reader" — Priya

- **Age:** 22-35
- **Occupation:** Student / Young Professional
- **Reading Habits:** 15-30 books/year
- **Tech Comfort:** High
- **Pain Point:** *"I have 200 books on my TBR list but never know which to start next."*
- **Device:** Smartphone (primary) + Laptop (secondary)
- **Location:** Urban India / Global English-speaking markets

### Secondary Persona: "The Comics Newcomer" — Rohan

- **Age:** 18-30
- **Occupation:** Student / gamer / movie fan
- **Comics Experience:** Loves Marvel/DC movies, never read comics
- **Pain Point:** *"I want to read Batman comics but there are thousands of issues. Where do I even start?"*
- **Device:** Mobile-first
- **What Kitabee gives him:** Series order guide + beginner-friendly collection rows + free public domain classics

### Tertiary Persona: "The Rediscoverer" — Arjun

- **Age:** 30-50
- **Occupation:** Working professional returning to reading
- **Reading Habits:** 3-10 books/year, wants to read more
- **Tech Comfort:** Medium
- **Pain Point:** *"I don't have time to browse. Just tell me what's worth reading."*
- **Device:** Mobile-first
- **What Kitabee gives him:** Curated themed rows, no browsing needed

### Quaternary Persona: "The Bookstagram Creator" — Meera

- **Age:** 18-28
- **Occupation:** Content creator, student
- **Reading Habits:** 50+ books/year
- **Pain Point:** *"I need niche recommendations beyond bestsellers to keep my content fresh."*
- **Device:** Mobile-only
- **What Kitabee gives her:** Hidden gems collections, reading DNA insights, diverse picks

### Anti-Personas (NOT Our Users)
- ❌ Academic researchers needing scholarly databases
- ❌ Publishers looking for market analytics
- ❌ Non-English readers (Phase 1 is English-only)

---

## 🌟 Product Vision & Goals

### Vision Statement
> *"To make discovering your next great book or comic as delightful and personal as a recommendation from your smartest reader friend — organized into collections so good they feel made just for you."*

### 3-Year North Star
Become the **#1 personalized book and comics discovery platform** for Gen-Z and Millennial readers globally, with 10M+ users, industry-leading recommendation accuracy, and the largest free public domain reading library in a mobile app.

### MVP Goals (5-Week Timeline)

| Goal | Description | Measurement |
|------|-------------|-------------|
| 🎯 **Prove AI Value** | Netflix-style collections + personalized recs work better than generic | User engagement with collection rows |
| 🏗️ **Full-Stack Portfolio** | Showcase end-to-end skills | Deployed live app + GitHub |
| 📱 **Cross-Platform** | Web + Mobile from one codebase | Works on both |
| 🔬 **ML Depth** | Cover 8+ ML techniques | All implemented + documented |
| 📚 **Books + Comics** | Unified discovery for both | Both content types searchable |
| 📖 **Free Reading** | Public domain content readable in-app | Internet Archive integrated |
| 🚀 **Production Quality** | Real engineering | Docker, CI/CD, tests, monitoring |

### Non-Goals for MVP
- ❌ Monetization / payments
- ❌ Social features (following, sharing)
- ❌ Modern copyrighted book full reading (legal constraint)
- ❌ Multi-language support
- ❌ Voice interface
- ❌ Native iOS/Android app store deployment

---

## 📊 Success Metrics

### Product Metrics

| Metric | Target | Why It Matters |
|--------|--------|----------------|
| **User Onboarding Completion** | 80%+ | Do users get to value fast? |
| **Books/Comics Rated Per User (30-day)** | 15+ | Engagement depth |
| **Collection Row Click-Through Rate** | 40%+ | Are themed collections compelling? |
| **Free Reading Session Start Rate** | 25%+ | Do users engage with free content? |
| **Series Guide Usage Rate** | 30%+ | Is order guide useful? |
| **User-Reported Satisfaction** | 4.2/5 | Would you use this again? |
| **Return User Rate (Weekly)** | 30%+ | Habit formation |

### Technical Metrics

| Metric | Target | Purpose |
|--------|--------|---------|
| **API Response Time (p95)** | < 300ms | User experience |
| **Recommendation Latency** | < 2s | Perceived intelligence |
| **Collection Generation Time** | < 3s | Home screen load |
| **API Cache Hit Rate** | 70%+ | Cost & speed |
| **System Uptime** | 99.5%+ | Reliability |
| **Test Coverage** | 70%+ | Code quality |

### ML Model Metrics

| Model | Metric | Target |
|-------|--------|--------|
| **Content-Based (TF-IDF)** | Precision@10 | 0.65+ |
| **Collaborative (KNN)** | Recall@10 | 0.55+ |
| **Neural Recommender** | RMSE | < 0.9 |
| **Collection Engine (KMeans)** | Silhouette Score | 0.45+ |
| **Mood Classifier** | Accuracy | 80%+ |
| **Sentiment Analyzer** | Accuracy | 85%+ |
| **Genre Classifier** | F1 Score | 0.80+ |

### Portfolio Metrics (Recruiter-Facing)

| Metric | Target |
|--------|--------|
| **GitHub Stars** | 20+ |
| **README Quality** | Complete with diagrams, badges, demo |
| **Demo Video** | < 2 min, professional quality |
| **Blog Post** | 1 detailed Medium/Dev.to article |
| **Live Deployment** | Both web + mobile QR working 24/7 |

---

## 🎯 Feature Scope (MVP)

### Feature Priority Framework
- 🔴 **P0** — Must have (project fails without it)
- 🟡 **P1** — Should have (significantly weakens without)
- 🟢 **P2** — Nice to have (delighter, if time permits)

---

### 🔐 F1: Authentication System (P0)

**Description:** User accounts with secure login.

**Requirements:**
- Email + password registration
- JWT-based authentication
- Password hashing (bcrypt)
- Token refresh mechanism
- Logout functionality

**Acceptance Criteria:**
- [ ] User can register with email in < 30 seconds
- [ ] Login persists across app restarts
- [ ] Passwords never stored in plain text
- [ ] Invalid credentials show clear error

---

### 📚 F2: Book + Comics Search (P0)

**Description:** Search across millions of books and comics via external APIs.

**Requirements:**
- Search by title, author, ISBN (books)
- Search by title, character, publisher (comics)
- Real-time results with debounce
- Cover images, ratings, descriptions
- Content type filter: Books / Comics / All
- Multi-source data:
  - Books: Google Books API (primary)
  - Comics metadata: Comic Vine API
  - Free reading availability: Internet Archive API
- Redis caching for repeated queries

**Acceptance Criteria:**
- [ ] Search returns results in < 500ms (cached) or < 2s (fresh)
- [ ] Books and comics clearly distinguished in results
- [ ] Free reading badge shown on eligible content
- [ ] Displays cover, title, author/creator, avg rating

---

### ⭐ F3: Rating System (P0)

**Description:** Users rate books and comics to train personalized recommendations.

**Requirements:**
- 5-star rating scale
- Optional text review
- Rating history per user
- Works for both books and comics
- Onboarding flow: rate 5+ items

**Acceptance Criteria:**
- [ ] User can rate in ≤ 2 taps
- [ ] Ratings immediately update recommendations and collections
- [ ] Cannot rate same item twice (edit only)
- [ ] Ratings persist across sessions

---

### 🎬 F4: Netflix-Style Themed Collections (P0)

**Description:** AI-curated rows of books and comics with catchy themed titles, displayed on the home screen exactly like Netflix rows.

**Requirements:**

**Personalized rows (ML-driven):**
- "Because you loved [Book/Comic]..."
- "Your Next [Genre] Obsession"
- "Readers Like You Also Loved..."
- "Authors Similar to [Favourite]"

**Mood-based rows (NLP-driven):**
- "Perfect for a Rainy Day"
- "Dark But You Cannot Put It Down"
- "Feel Good Reads"
- "Laugh Out Loud Funny"
- "Epic Worlds Built From Scratch"
- "Inspiring True Stories"

**Utility rows (rule + data driven):**
- "Complete Series — Read in Order"
- "Finish in One Weekend"
- "Award Winners"
- "Trending This Week"
- "New Releases"
- "Everyone Is Reading This"

**Content type rows:**
- "Free to Read Right Now" (Internet Archive)
- "Comics — New Reader Friendly"
- "Public Domain Classics"
- "Start Here — Beginner Friendly"

**Technical requirements:**
- Collections generated by ML clustering + mood detection
- Catchy titles generated by template engine
- Collections rotate to avoid staleness
- Each row shows 8-12 items, horizontally scrollable
- Tap row title to see full collection

**Acceptance Criteria:**
- [ ] Home screen shows minimum 6 collection rows
- [ ] Each row has distinct catchy title
- [ ] Collections are personalized per user
- [ ] New user sees popular/mood-based rows (cold start handled)
- [ ] Collections refresh at least daily
- [ ] Both books and comics appear in relevant rows

---

### 🔢 F5: Series & Reading Order Guide (P0)

**Description:** For any book series or comic run, Kitabee shows the correct reading order with context — which to start with, what is a prequel, what is a spin-off.

**Requirements:**
- Detect if a book/comic belongs to a series
- Display full series in correct reading order
- Label each entry: "Start Here", "Prequel", "Spin-off", "Optional"
- Separate main series from companion/prequel series
- Works for both books and comics
- Tips shown for complex universes (e.g. DC, Marvel)

**Example output:**
```
DUNE SERIES — Reading Order
1. Dune ← Start Here
2. Dune Messiah
3. Children of Dune
4. God Emperor of Dune
5. Heretics of Dune
6. Chapterhouse: Dune

PREQUEL SERIES (by Brian Herbert):
1. House Atreides
2. House Harkonnen
3. House Corrino
💡 Tip: Read after Book 1 or after all 6 originals.
```

**Acceptance Criteria:**
- [ ] Series detected from metadata automatically
- [ ] Reading order correct for top 50 popular series
- [ ] Labels (Start Here, Prequel, Spin-off) shown
- [ ] Tips shown for complex universes
- [ ] Works on book detail page and in "Complete Series" collection row

---

### 🤖 F6: AI Recommendation Engine (P0)

**Description:** Multi-model personalized recommendations powering the collection rows.

**Requirements:**
- **Content-based:** TF-IDF on descriptions + genres + authors
- **Collaborative:** KNN on user ratings
- **Neural:** Keras-based deep recommender
- **Collection engine:** KMeans clustering for themed grouping
- **Mood detection:** NLP on descriptions for mood signals
- **Hybrid ranking:** Weighted combination
- Explainability: "Why this book?"
- Works for both books and comics

**Acceptance Criteria:**
- [ ] Recommendations update after each new rating
- [ ] Diversity: not all same genre/author in one collection
- [ ] Explanation shown for each rec
- [ ] Handles cold-start via onboarding data
- [ ] Collection titles are catchy and contextually accurate

---

### 📖 F7: Personal Library (P0)

**Description:** User's collection of books and comics they have engaged with.

**Requirements:**
- Categories: Want to Read, Currently Reading, Read
- Add/remove items
- Works for both books and comics
- Rating linked to library status
- Search within library
- Filter by content type (books / comics)

**Acceptance Criteria:**
- [ ] Can categorize item in ≤ 2 taps
- [ ] Library syncs across web and mobile
- [ ] Books and comics shown separately or together (toggle)
- [ ] Empty states with clear CTAs

---

### 📖 F8: Free Reading — Public Domain (P1)

**Description:** Users can read public domain books and comics directly inside the app via Internet Archive integration.

**Requirements:**
- Internet Archive API integration
- Free reading badge on eligible books and comics
- EPUB reader for public domain books (WebView-based)
- Image-based reader for public domain comics (page-by-page)
- Reading progress tracked per user
- "Free to Read Right Now" collection row on home screen
- Works offline once content is loaded (stretch goal)

**Content available:**
- Classic literature (Dickens, Austen, Tolstoy, Shakespeare etc.)
- Golden Age comics (1930s-1950s: early Superman, Batman, horror)
- Public domain manga (stretch goal)

**Acceptance Criteria:**
- [ ] Free reading badge visible on search results and book detail
- [ ] EPUB reader opens within app (no external browser)
- [ ] Comics reader shows pages clearly on mobile screen
- [ ] Reading progress saved across sessions
- [ ] "Free to Read Right Now" row appears on home screen

---

### 🔍 F9: Book & Comic Details Page (P0)

**Description:** Rich information hub for any book or comic.

**Requirements:**
- Cover, title, author/creator, publisher, year
- Description with expand/collapse
- Rating distribution
- Similar items (books or comics)
- Series order section (if part of series)
- Free reading button (if available via Internet Archive)
- "Why we recommend this" (if applicable)
- Add to library button
- Content type clearly labeled (Book / Comic)

**Acceptance Criteria:**
- [ ] Loads in < 1 second (cached)
- [ ] Series order shown if applicable
- [ ] Free read button shown if available
- [ ] Similar items section shows 5+ items
- [ ] Works for both books and comics

---

### 📊 F10: Reading Insights Dashboard (P1)

**Description:** Personalized reading analytics — "Reading DNA".

**Requirements:**
- Genre distribution chart (books + comics separate)
- Reading pace over time
- Top authors + creators
- Reading personality profile (AI-generated)
- Diversity metrics
- Books vs comics breakdown

**Acceptance Criteria:**
- [ ] Insights update weekly
- [ ] Charts are visually clear
- [ ] Reading DNA is unique per user
- [ ] Shows both book and comic activity

---

### 💬 F11: Sentiment Analysis (P1)

**Description:** AI analysis of descriptions and reviews for tone and mood signals.

**Requirements:**
- Analyze book/comic descriptions
- Visualize sentiment breakdown
- Flag polarizing content
- Mood tags generated (dark, funny, romantic, thrilling, inspiring)
- Mood tags feed into themed collection generation

**Acceptance Criteria:**
- [ ] Sentiment displayed on detail page
- [ ] Mood tags visible and accurate
- [ ] Mood tags feed collection engine

---

### 🏆 F12: Trending & Bestsellers (P1)

**Description:** Curated trending content from NYT + community activity.

**Requirements:**
- NYT Books API integration
- Weekly bestseller lists
- "Trending This Week" collection row
- "Everyone Is Reading This" collection row
- Cached for 24 hours

**Acceptance Criteria:**
- [ ] Trending rows appear on home screen
- [ ] Personalized to user preferences where possible
- [ ] Freshness < 24 hours

---

### 🌗 F13: Dark Mode (P2)

**Description:** Light + Dark theme support.

**Requirements:**
- Toggle in settings
- Persists across sessions
- Respects system preference initially

---

## 🚫 Out of Scope

### Features
- ❌ Book/comic purchasing (affiliate links are Phase 2)
- ❌ Full reading of modern copyrighted books (legal constraint)
- ❌ Full reading of modern copyrighted comics (legal constraint)
- ❌ Audiobook integration
- ❌ Social features (following, DMs, groups)
- ❌ Book clubs / discussion forums
- ❌ Author/creator profiles
- ❌ Book quotes / highlights
- ❌ Reading challenges / goals
- ❌ Multi-language support
- ❌ Offline mode (except stretch goal for free reading)
- ❌ Push notifications
- ❌ Email digests

### Platforms
- ❌ Native iOS App Store deployment
- ❌ Native Android Play Store deployment
- ❌ Desktop app

### Business
- ❌ Monetization / subscriptions
- ❌ Advertising
- ❌ Publisher partnerships
- ❌ API for third parties

---

## 📖 User Stories

### As a New User...

**US-1:** *As a new user, I want to quickly sign up so I can start getting recommendations without friction.*

**US-2:** *As a new user, I want to tell Kitabee my taste so recommendations are personal from day one.*
- Onboarding: rate 5-10 books/comics
- Alternative: select favorite genres + content type preference (books / comics / both)

**US-3:** *As a new comics reader, I want to know where to start reading Batman so I am not overwhelmed.*
- Series order guide shown immediately
- "Start Here" label on first issue

### As a Returning User...

**US-4:** *As a returning user, I want to see fresh themed collections every time I open the app.*
- Home screen shows Netflix-style rows
- Collections rotate and refresh daily

**US-5:** *As a returning user, I want to understand why a book was recommended to me.*
- Each rec shows explanation
- "Because you loved Dune..." row title explains the connection

**US-6:** *As a returning user, I want to track books and comics I have read, am reading, or want to read.*
- Unified library for books and comics
- Filter by content type

**US-7:** *As a returning user, I want to read a classic novel or old comic for free inside the app.*
- Free reading badge visible
- In-app reader opens immediately

### As a Data-Curious User...

**US-8:** *As a data-curious user, I want to see insights about my reading habits across books and comics.*

**US-9:** *As a data-curious user, I want to compare my taste with other readers.*
- Reading DNA personality profile
- Uniqueness score

### As a Cross-Device User...

**US-10:** *As a cross-device user, I want my library and reading progress synced between phone and laptop.*

---

## 🔄 User Flows

### Flow 1: New User Onboarding

```
[Landing Page]
      ↓
[Sign Up: Email + Password]
      ↓
[Welcome: "What do you love?"]
      ↓
[Choose: Books / Comics / Both]
      ↓
[Rate 5 items from popular list]
      ↓
[Select 3 favorite genres]
      ↓
[Loading: "Building your personal collections..."]
      ↓
[Home: Netflix-style themed collection rows]
      ↓
[Success: User is now active]
```

### Flow 2: Netflix-Style Discovery

```
[Home Screen]
      ↓
[Sees themed collection rows]
   "Because you loved Dune..."
   "Epic Worlds Built From Scratch"
   "Free to Read Right Now"
   "Comics — New Reader Friendly"
      ↓
[Taps a collection title]
      ↓
[Full collection page — all items in this theme]
      ↓
[Taps a book or comic]
      ↓
[Detail Page]
   ├─ Description + mood tags
   ├─ "Why we recommend this"
   ├─ Series order (if applicable)
   ├─ Free Read button (if available)
   └─ Similar items
      ↓
[User Actions]
   ├─ Read Free (Internet Archive)
   ├─ Add to Library
   └─ Rate it
```

### Flow 3: Series Order Discovery

```
[User searches "Batman"]
      ↓
[Search results show Batman comics]
      ↓
[Taps Batman: Year One]
      ↓
[Detail Page]
      ↓
[Series Order section visible]
   📖 New Reader Path:
   1. Batman: Year One ← You are here
   2. The Long Halloween
   3. The Dark Knight Returns
      ↓
[User adds all three to "Want to Read"]
      ↓
["Complete Series" collection row appears on home]
```

### Flow 4: Free Reading Flow

```
[User taps "Free to Read Right Now" collection]
      ↓
[Sees list of public domain books + comics]
      ↓
[Taps "Pride and Prejudice"]
      ↓
[Detail Page — Free Read button visible]
      ↓
[Taps "Read Free"]
      ↓
[Internet Archive EPUB fetched]
      ↓
[In-app EPUB reader opens]
      ↓
[Reading progress saved]
      ↓
[Next session: "Continue Reading" row on home screen]
```

### Flow 5: Getting Better Recommendations

```
[User rates a new book or comic]
      ↓
[Rating stored in DB]
      ↓
[ML models triggered async]
      ↓
[Collection rows refreshed with new data]
      ↓
[New themed rows appear based on updated taste]
      ↓
[Engagement loop continues]
```

---

## 🏗️ Technical Architecture

### System Overview

```
┌──────────────────────────────────────────────────────────┐
│                    CLIENT LAYER                          │
│  ┌──────────────────┐      ┌──────────────────────┐      │
│  │   Web (Vercel)   │      │  Mobile (Expo Go)    │      │
│  │  React Native    │      │  React Native        │      │
│  └────────┬─────────┘      └──────────┬───────────┘      │
└───────────┼────────────────────────── ┼──────────────────┘
            └──────────────┬────────────┘
                           ↓ HTTPS
┌──────────────────────────────────────────────────────────┐
│                    API LAYER (AWS EC2)                   │
│  ┌───────────────────────────────────────────────────┐   │
│  │              FastAPI (Python 3.11)                │   │
│  │  ├─ Authentication (JWT)                          │   │
│  │  ├─ Book + Comics Search                         │   │
│  │  ├─ Ratings                                      │   │
│  │  ├─ Netflix-Style Collections (ML)               │   │
│  │  ├─ Series Order Guide                           │   │
│  │  ├─ Free Reading (Internet Archive proxy)        │   │
│  │  ├─ Insights                                     │   │
│  │  └─ /docs (Swagger)                              │   │
│  └───────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
            │                          │
            ↓                          ↓
┌───────────────────────┐  ┌───────────────────────────────┐
│      DATA LAYER       │  │          ML LAYER             │
│  ┌─────────────────┐  │  │  ┌─────────────────────────┐  │
│  │  PostgreSQL     │  │  │  │ Vectorizer              │  │
│  │  (Users,        │  │  │  │ TF-IDF (books + comics) │  │
│  │   Ratings,      │  │  │  └─────────────────────────┘  │
│  │   Library,      │  │  │  ┌─────────────────────────┐  │
│  │   Collections,  │  │  │  │ Collection Engine       │  │
│  │   Reading       │  │  │  │ KMeans + Mood Detection │  │
│  │   Progress)     │  │  │  └─────────────────────────┘  │
│  └─────────────────┘  │  │  ┌─────────────────────────┐  │
│  ┌─────────────────┐  │  │  │ Personalizer            │  │
│  │  Redis          │  │  │  │ KNN Collaborative       │  │
│  │  (API Cache,    │  │  │  └─────────────────────────┘  │
│  │   Collections   │  │  │  ┌─────────────────────────┐  │
│  │   Cache)        │  │  │  │ Neural Recommender      │  │
│  └─────────────────┘  │  │  │ Keras Deep Model        │  │
└───────────────────────┘  │  └─────────────────────────┘  │
                           │  ┌─────────────────────────┐  │
                           │  │ Series Intelligence     │  │
                           │  │ NLP + Metadata Parser   │  │
                           │  └─────────────────────────┘  │
                           │  ┌─────────────────────────┐  │
                           │  │ Sentiment + Mood        │  │
                           │  │ NLTK + TextBlob         │  │
                           │  └─────────────────────────┘  │
                           └───────────────────────────────┘
                                         │
                                         ↓
┌──────────────────────────────────────────────────────────┐
│                    EXTERNAL APIs                         │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │ Google      │  │ Comic Vine   │  │ Internet        │  │
│  │ Books API   │  │ API          │  │ Archive API     │  │
│  │ (books)     │  │ (comics      │  │ (free reading   │  │
│  │             │  │  metadata)   │  │  books+comics)  │  │
│  └─────────────┘  └──────────────┘  └─────────────────┘  │
│  ┌─────────────┐                                          │
│  │ NYT Books   │                                          │
│  │ API         │                                          │
│  │ (trending)  │                                          │
│  └─────────────┘                                          │
└──────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility |
|-----------|----------------|
| **React Native App** | UI, state management, API consumption, EPUB/comic reader |
| **FastAPI Backend** | Business logic, ML serving, API orchestration |
| **PostgreSQL** | Durable data (users, ratings, library, reading progress, collections) |
| **Redis** | Fast cache (API responses, generated collections) |
| **Google Books API** | Primary book metadata source |
| **Comic Vine API** | Comics metadata source |
| **Internet Archive API** | Free public domain reading (books + comics) |
| **NYT Books API** | Trending and bestseller data |
| **ML Layer** | Collection generation, recommendations, series detection, sentiment |

---

## 🤖 AI/ML Approach

### The ML Modules

Kitabee's intelligence is organized into five focused modules:

---

### Module 1 — Vectorizer (Foundation)
**Technique:** TF-IDF Vectorization + Cosine Similarity
**Library:** scikit-learn
**Purpose:** Represent books and comics as vectors based on descriptions, genres, authors, tags
**Output:** Similarity scores between any two content items
**Used by:** All other modules

---

### Module 2 — Collection Engine (Core Feature)
**Techniques:** KMeans Clustering + NLP Mood Detection + Template Title Generation
**Library:** scikit-learn + NLTK + TextBlob
**Purpose:** Group books and comics into themed collections with catchy titles

**How it works:**
```
Step 1 — Vectorize all content (Module 1)
Step 2 — KMeans clusters similar content together
Step 3 — Mood detection scans descriptions
          Dark words → "Dark But You Cannot Put It Down"
          Funny words → "Laugh Out Loud Funny"
          Epic words → "Epic Worlds Built From Scratch"
Step 4 — Template engine generates collection title
Step 5 — Collections ranked per user by preference match
Step 6 — Collections cached in Redis, refreshed daily
```

**Collection title templates:**
```
Cluster: same author → "From the Mind of [Author]"
Cluster: fantasy + epic + series → "Epic Worlds Built From Scratch"
Cluster: thriller + dark → "Dark But You Cannot Put It Down"
Cluster: short + contemporary → "Read It Before Bed Tonight"
Cluster: user rated 5 stars similar → "Your Next Obsession — Guaranteed"
Cluster: book + movie adaptation → "Read It Before You Watch It"
Cluster: series + complete → "The Full Journey — Start to Finish"
Cluster: trending + recent → "Everyone Is Reading This Right Now"
Cluster: public domain → "Free to Read Right Now"
Cluster: comics + beginner → "Comics — New Reader Friendly"
```

---

### Module 3 — Personalizer
**Techniques:** KNN Collaborative Filtering + User Preference Matching
**Library:** scikit-learn
**Purpose:** Rank and filter collections per individual user

**How it works:**
```
User profile signals:
  → Ratings history
  → Library contents
  → Onboarding preferences
  → Content type preference (books/comics/both)
  → Reading history

KNN finds similar users
Similar users' highly-rated content surfaces in collections
"Because you loved X" rows generated from this
```

---

### Module 4 — Series Intelligence
**Techniques:** Metadata parsing + NLP pattern extraction + rule-based ordering
**Library:** NLTK + regex + Google Books / Comic Vine metadata
**Purpose:** Detect series membership, determine reading order, classify entry type

**How it works:**
```
Step 1 — Parse metadata fields (series name, volume number)
Step 2 — NLP on description ("Book 2 of...", "sequel to...")
Step 3 — Cross-reference Comic Vine issue numbers for comics
Step 4 — Classify: Main Series / Prequel / Spin-off / Companion
Step 5 — Generate ordered list with labels
Step 6 — Add contextual tip for complex universes
```

---

### Module 5 — Neural Recommender
**Technique:** Neural Collaborative Filtering
**Library:** Keras + TensorFlow
**Purpose:** Deep personalization — learns complex patterns beyond simple similarity

**How it works:**
```
Input: user embedding + content embedding
Hidden layers learn complex preference patterns
Output: predicted rating score
Used to surface items collaborative filtering misses
```

---

### Full ML Techniques Count

| # | Technique | Module | Library |
|---|-----------|--------|---------|
| 1 | TF-IDF Vectorization | Vectorizer | scikit-learn |
| 2 | Cosine Similarity | Vectorizer | scikit-learn |
| 3 | KMeans Clustering | Collection Engine | scikit-learn |
| 4 | Mood Detection NLP | Collection Engine | NLTK + TextBlob |
| 5 | K-Nearest Neighbors | Personalizer | scikit-learn |
| 6 | Neural Collaborative Filtering | Neural Recommender | Keras |
| 7 | Metadata NLP Parsing | Series Intelligence | NLTK + regex |
| 8 | Sentiment Analysis | Sentiment Module | TextBlob |
| 9 | Naive Bayes Genre Classifier | Collection Engine | scikit-learn |
| 10 | Anomaly Detection (Isolation Forest) | Ratings Quality | scikit-learn |

---

### Recommendation Hybrid Strategy

```
User requests home screen
         ↓
┌──────────────────────────────────────────┐
│ Module 1: Vectorizer                     │
│ → All content represented as vectors     │
└──────────────────────────────────────────┘
         +
┌──────────────────────────────────────────┐
│ Module 2: Collection Engine              │
│ → Groups content into themed clusters    │
│ → Generates catchy collection titles     │
└──────────────────────────────────────────┘
         +
┌──────────────────────────────────────────┐
│ Module 3: Personalizer                   │
│ → Ranks collections for this user        │
│ → Adds "Because you loved X..." rows     │
└──────────────────────────────────────────┘
         +
┌──────────────────────────────────────────┐
│ Module 5: Neural Recommender             │
│ → Surfaces deep personalization picks    │
│ → Fills gaps collaborative misses        │
└──────────────────────────────────────────┘
         ↓
[Diversity filter: balanced genres + content types]
         ↓
[Minimum 6 collection rows assembled]
         ↓
[Cached in Redis for fast home screen load]
         ↓
[Netflix-style home screen rendered]
```

### Cold Start Solution

**Problem:** New users have no rating history.

**Solution:**
1. **Onboarding** — Choose books/comics/both + rate 5 items + select genres
2. **Content-type rows** — Show books or comics rows based on stated preference
3. **Mood-based rows** — Universal, no personalization needed
4. **Popular rows** — "Everyone Is Reading This" works for anyone
5. **Progressive personalization** — Personalized rows appear as ratings grow

---

## 📦 Data Strategy

### Data Sources

| Source | Type | What It Provides | Frequency | Storage |
|--------|------|-----------------|-----------|---------|
| **Google Books API** | Book metadata | Title, author, description, cover, ISBN | On-demand | Redis (24h) |
| **Comic Vine API** | Comics metadata | Title, creator, publisher, issue, characters | On-demand | Redis (24h) |
| **Internet Archive API** | Free content | EPUB/PDF/image links for public domain | On-demand | Redis (24h) |
| **NYT Books API** | Bestsellers | Weekly trending books | Weekly | Redis (1 week) |
| **User Ratings** | User-generated | ML training data | Real-time | PostgreSQL |
| **User Library** | User-generated | Reading status | Real-time | PostgreSQL |
| **Reading Progress** | User-generated | Position in book/comic | Real-time | PostgreSQL |

### Database Schema (High-Level)

```sql
-- Core tables (already built)
users (id, email, password_hash, name, onboarding_completed, ...)
books (id, external_id, title, author, description, genre, cover_url, ...)
ratings (id, user_id, book_id, rating, review_text, ...)
library_items (id, user_id, book_id, status, ...)
user_preferences (id, user_id, favorite_genres, content_type_preference, ...)
recommendations (id, user_id, book_id, score, model_type, ...)

-- New tables (Week 3+)
comics (id, external_id, title, creator, publisher, description,
        cover_url, issue_number, series_name, content_type, ...)

comic_ratings (id, user_id, comic_id, rating, review_text, ...)

comic_library_items (id, user_id, comic_id, status, ...)

collections (id, name, title, description, content_type,
             collection_type, items_json, generated_at, ...)
-- collection_type: personalized | mood | utility | trending | free_reading | series

user_collections (id, user_id, collection_id, rank, shown_at, ...)

reading_progress (id, user_id, content_id, content_type,
                  progress_percent, last_position, last_read_at, ...)

series_metadata (id, series_name, content_type, ordered_items_json,
                 tips, generated_at, ...)
```

### Data Privacy
- Passwords bcrypt-hashed
- No PII shared with external APIs
- User data deletable on request (GDPR-ready)
- Reading progress stored locally + synced to backend
- No third-party analytics in MVP

---

## 🎨 UX & Design Principles

### Design Philosophy
> **"Feels like your smartest reader friend recommending books and comics — organized into collections so good they feel made just for you."**

### Core Principles

1. **🎬 Netflix Familiarity** — Row-based layout users already know and love
2. **🎯 Speed to Value** — First themed collection visible in < 60 seconds from signup
3. **📖 Content First** — Covers dominate; UI is invisible
4. **💛 Warm & Human** — Bee mascot brings personality
5. **🧠 Explainable AI** — Never black-box; collection titles explain the why
6. **📱 Mobile-Native** — Designed for thumbs, not mice
7. **♿ Accessible** — WCAG AA compliance minimum
8. **📚 Unified** — Books and comics feel like one seamless world

### Visual Identity

**Brand:** Kitabee 🐝
**Mascot:** Kit the Bee (curious, wise, helpful)
**Tone:** Friendly, smart, warm, non-intimidating

**Color Palette:**
- 🟡 Primary: `#FFC93C` (Honey Yellow)
- 🔵 Secondary: `#1E3A8A` (Deep Blue)
- 🟢 Accent: `#10B981` (Green)
- ⚪ Background: `#FFF8E7` (Warm Cream)
- ⚫ Text: `#1F2937` (Charcoal)

**Typography:**
- Headings: **Poppins** (rounded, friendly)
- Body: **Inter** (clean, readable)

### Home Screen Layout
```
┌─────────────────────────────────────┐
│  Good evening, [Name] 👋             │
│                                     │
│  ▶ Continue Reading                 │
│    [Last item] — Progress bar       │
│                                     │
│  🔥 Because You Loved [Book]...     │
│  [Cover][Cover][Cover][Cover] →     │
│                                     │
│  🌍 Epic Worlds Built From Scratch  │
│  [Cover][Cover][Cover][Cover] →     │
│                                     │
│  📖 Free to Read Right Now          │
│  [Cover][Cover][Cover][Cover] →     │
│                                     │
│  🦸 Comics — New Reader Friendly    │
│  [Cover][Cover][Cover][Cover] →     │
│                                     │
│  ✅ Complete Series — Start to Fin  │
│  [Cover][Cover][Cover][Cover] →     │
│                                     │
│  💎 Hidden Gems You Will Love       │
│  [Cover][Cover][Cover][Cover] →     │
│                                     │
│  🔥 Everyone Is Reading This        │
│  [Cover][Cover][Cover][Cover] →     │
└─────────────────────────────────────┘
```

---

## ⚠️ Constraints & Assumptions

### Constraints

**Time:**
- 5-week MVP delivery timeline
- Solo developer
- 4-6 hours/day dev capacity

**Budget:**
- ₹0-₹800 total (domain only)
- AWS free tier
- No paid tools

**Technical:**
- Free-tier API rate limits
- Comic Vine API requires free key registration
- Internet Archive rate limits (polite usage)
- Single-region deployment
- Windows 11 dev environment

**Legal:**
- Only public domain content available for free reading
- Modern copyrighted books and comics cannot be served
- Internet Archive CDL (Controlled Digital Lending) requires user login to their system for modern books

### Assumptions
- Users have reliable internet
- English-language reader base primarily
- Google Books + Comic Vine + Internet Archive sufficient for MVP content
- Users willing to rate 5+ items in onboarding
- Modern browser / smartphone (last 3 years)

---

## ⚡ Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| **External API rate limits** | High | Medium | Aggressive Redis caching, multi-source fallback |
| **Comic Vine API changes** | Medium | Low | Abstract behind service layer, easy to swap |
| **Internet Archive content availability** | Medium | Low | Cache availability flags, graceful fallback |
| **ML collections feel generic** | High | Medium | Tune clustering, expand mood word lists, user feedback loop |
| **Series order data incomplete** | Medium | Medium | Manual curation for top 50 series, community corrections later |
| **Cold start for comics** | Medium | High | Mood-based and popular rows work without personalization |
| **EPUB reader complexity** | Medium | Medium | Use proven WebView library, test early |
| **AWS free tier exceeded** | Medium | Low | Monitor usage, optimize queries |
| **Timeline slip** | High | Medium | Cut P2 features aggressively |
| **React Native learning curve** | Medium | High | Reference templates, use starter |

---

## 🗓️ Milestones & Timeline

### Overall: 5 Weeks

| Week | Phase | Key Deliverables |
|------|-------|-----------------|
| **Week 1** | Foundation + APIs | Backend + Google Books + Redis cache working |
| **Week 2** | Auth + Users | User system + JWT + rating collection |
| **Week 3** | AI/ML Core | Vectorizer + Collection Engine + Series Intelligence |
| **Week 4** | Mobile App | Expo app + Netflix-style home + book/comic detail + free reader |
| **Week 5** | Deploy + Polish | AWS + Vercel + Expo Go + Demo video |

### Week 3 Detailed (ML Focus)
- [ ] Day 15: TF-IDF Vectorizer (books + comics)
- [ ] Day 16: KMeans Collection Engine + mood detection
- [ ] Day 17: Collection title templates + catchy naming
- [ ] Day 18: Series Intelligence (metadata parsing + order generation)
- [ ] Day 19: KNN Collaborative Filtering + Personalizer
- [ ] Day 20: Neural Recommender (Keras) + hybrid API endpoint
- [ ] Day 21: Week 3 review + ML integration tests

### Week 4 Detailed (Frontend Focus)
- [ ] Day 22: Expo project setup + navigation
- [ ] Day 23: Netflix-style home screen (collection rows)
- [ ] Day 24: Search screen (books + comics unified)
- [ ] Day 25: Book/comic detail page + series order UI
- [ ] Day 26: Library screen + reading progress
- [ ] Day 27: Free reading — EPUB reader + comics reader
- [ ] Day 28: Week 4 review + frontend integration

### Success Definition per Week
- **Week 1:** Can search books via API ✅
- **Week 2:** Users can register and rate books ✅
- **Week 3:** Netflix-style collections generated by ML
- **Week 4:** Full app usable on phone including free reading
- **Week 5:** Publicly accessible + demo-ready

---

## 🚀 Future Roadmap (Post-MVP)

### Phase 2 (Weeks 6-10)
- 📱 Native iOS/Android via EAS Build
- 🛒 Amazon affiliate links (Buy button — monetization)
- 🌐 Social features (follow readers, share libraries)
- 📖 Reading progress tracking enhancements
- 🏆 Reading challenges and achievements
- 🔔 Push notifications ("New in your collections")
- 🌍 Regional trending (India, UK, USA separate)

### Phase 3 (Months 3-6)
- 🌍 Multi-language support (Hindi, Tamil, Spanish)
- 📚 Audiobook integration
- 🤖 GPT-powered book chat ("Discuss this book with AI")
- 💰 Premium tier (advanced reading DNA, exclusive collections)
- 🎤 "What should I read next?" voice interface

### Phase 4 (Year 1+)
- 🏢 B2B: API for bookstores and libraries
- 🎓 Educational: School reading list recommendations
- 🌐 Full community features + book clubs
- 📊 Publisher analytics dashboard
- 🤝 Comic publisher partnerships (preview chapters)

---

## 📎 Appendix

### Glossary

- **PRD:** Product Requirements Document
- **MVP:** Minimum Viable Product
- **TF-IDF:** Term Frequency-Inverse Document Frequency
- **KNN:** K-Nearest Neighbors
- **JWT:** JSON Web Token
- **Collection Row:** A horizontally scrollable themed group of books/comics (Netflix-style)
- **Series Intelligence:** ML module that detects series membership and generates reading order
- **Cold Start:** ML problem where new users have no data
- **Public Domain:** Content where copyright has expired — free to use legally
- **CDL:** Controlled Digital Lending — Internet Archive's library borrowing system
- **Expo Go:** Mobile app for testing Expo projects via QR code

### References

- Google Books API: [developers.google.com/books](https://developers.google.com/books)
- Open Library API: [openlibrary.org/developers/api](https://openlibrary.org/developers/api)
- Internet Archive API: [archive.org/developers](https://archive.org/developers)
- Comic Vine API: [comicvine.gamespot.com/api](https://comicvine.gamespot.com/api)
- NYT Books API: [developer.nytimes.com/docs/books-product](https://developer.nytimes.com/docs/books-product)
- FastAPI Docs: [fastapi.tiangolo.com](https://fastapi.tiangolo.com)
- Expo Docs: [docs.expo.dev](https://docs.expo.dev)

### Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Original] | [Your Name] | Initial PRD created |
| 2.0 | [Today] | [Your Name] | Added comics discovery, free reading via Internet Archive, Netflix-style themed collections, series reading order guide, Comic Vine API, updated ML modules, new DB tables, updated user personas, updated user flows |

---

**End of PRD** 🐝

*"Bee curious. Bee well-read."*

---

