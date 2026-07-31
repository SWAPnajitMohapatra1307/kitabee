# 🔄 Kitabee — Application Flow Document

> **Document Version:** 1.0  
> **Last Updated:** [Today's Date]  
> **Author:** [Your Name]  
> **Status:** 🟢 Approved for Implementation  
> **Related Docs:** [PRD.md](./PRD.md) | [TECHSPEC.md](./TECHSPEC.md)

---

## 📚 Table of Contents

1. [Overview](#-overview)
2. [App Structure Map](#-app-structure-map)
3. [Global Navigation](#-global-navigation)
4. [Screen Inventory](#-screen-inventory)
5. [Flow 1: First-Time User Onboarding](#-flow-1-first-time-user-onboarding)
6. [Flow 2: Returning User Login](#-flow-2-returning-user-login)
7. [Flow 3: Book Discovery](#-flow-3-book-discovery)
8. [Flow 4: Book Search](#-flow-4-book-search)
9. [Flow 5: Rating a Book](#-flow-5-rating-a-book)
10. [Flow 6: Personal Library Management](#-flow-6-personal-library-management)
11. [Flow 7: Reading Insights](#-flow-7-reading-insights)
12. [Flow 8: Profile & Settings](#-flow-8-profile--settings)
13. [Screen States](#-screen-states)
14. [Error Handling Flows](#-error-handling-flows)
15. [Empty States](#-empty-states)
16. [Loading States](#-loading-states)
17. [Success States](#-success-states)
18. [Cross-Platform Considerations](#-cross-platform-considerations)
19. [Accessibility Flows](#-accessibility-flows)
20. [Analytics Events](#-analytics-events)

---

## 🎯 Overview

### Purpose
This document maps every user journey through Kitabee — from first launch to power-user engagement. It defines screen states, transition triggers, and edge cases.

### Scope
- ✅ All MVP user flows (auth, discovery, ratings, library, insights)
- ✅ All screen states (loading, error, empty, success)
- ✅ Cross-platform behavior (web vs mobile)
- ✅ Accessibility considerations
- ❌ Post-MVP features (social, sharing, notifications)

### How to Read This Doc

- **Flows** — Complete user journeys with entry/exit points
- **Screens** — Individual UI destinations
- **States** — Different conditions of the same screen
- **Transitions** — What triggers moving between screens
- **Actions** — What the user does (tap, type, swipe)
- **Feedback** — What the app shows in response

### Legend

- 🏠 = Home/Root screens
- 🔐 = Authentication screens
- 📚 = Book-related screens
- ⭐ = Rating screens
- 📖 = Library screens
- 📊 = Insights screens
- 👤 = Profile screens
- ⚠️ = Error/Edge states
- ✅ = Success states
- 🔄 = Loading states
- 📭 = Empty states

---

## 🗺️ App Structure Map

### High-Level Architecture

```
KITABEE APP
│
├── 🔐 Auth Stack (unauthenticated users)
│   ├── Splash Screen
│   ├── Welcome Screen
│   ├── Login Screen
│   ├── Register Screen
│   └── Password Reset Screen (Post-MVP)
│
├── 🚀 Onboarding Stack (first-time users)
│   ├── Onboarding Intro
│   ├── Genre Selection
│   ├── Rate Initial Books
│   └── Personalization Loading
│
└── 🏠 Main App (authenticated users)
    │
    ├── Bottom Tab Navigator
    │   ├── 📚 Home Tab
    │   ├── 🔍 Search Tab
    │   ├── 📖 Library Tab
    │   ├── 📊 Insights Tab
    │   └── 👤 Profile Tab
    │
    └── Modal Stack (overlays)
        ├── Book Details Modal
        ├── Rating Modal
        ├── Filter Modal
        └── Confirmation Dialogs
```

### Navigation Hierarchy

```
Root Navigator (Stack)
    │
    ├── Auth Navigator (Stack) ────► Not authenticated
    │   ├── Splash
    │   ├── Welcome
    │   ├── Login
    │   └── Register
    │
    ├── Onboarding Navigator (Stack) ────► First login only
    │   ├── OnboardingIntro
    │   ├── GenreSelection
    │   ├── RateInitialBooks
    │   └── Personalizing
    │
    └── Main Navigator (Tabs) ────► Authenticated + Onboarded
        ├── Home Tab (Stack)
        │   ├── HomeScreen
        │   └── BookDetailsScreen
        ├── Search Tab (Stack)
        │   ├── SearchScreen
        │   └── BookDetailsScreen
        ├── Library Tab (Stack)
        │   ├── LibraryScreen
        │   └── BookDetailsScreen
        ├── Insights Tab (Stack)
        │   └── InsightsScreen
        └── Profile Tab (Stack)
            ├── ProfileScreen
            ├── SettingsScreen
            ├── EditProfileScreen
            └── AboutScreen
```

---

## 🧭 Global Navigation

### Bottom Tab Bar (Main App)

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│              [Current Screen Content]               │
│                                                     │
│                                                     │
├─────────────────────────────────────────────────────┤
│  🏠      🔍       📖        📊       👤             │
│ Home  Search   Library  Insights  Profile           │
└─────────────────────────────────────────────────────┘
```

**Behavior:**
- Always visible in main app
- Active tab highlighted with primary color (`#FFC93C`)
- Icons use Material Icons via `@expo/vector-icons`
- Tapping current tab scrolls to top OR goes to root of stack
- Hidden during modal presentations

**Cross-Platform:**
| Feature | Mobile | Web |
|---------|--------|-----|
| Tab bar position | Bottom | Bottom (or left sidebar > 1024px) |
| Tap area | 44x44 min | 44x44 min |
| Badge support | ✅ Yes | ✅ Yes |
| Long-press menu | ✅ Yes | ❌ No |

### Header Navigation

```
┌─────────────────────────────────────────────────────┐
│  ←  Screen Title              🔍  ⋮                 │
├─────────────────────────────────────────────────────┤
```

**Components:**
- **Back button** (←) — Left side, shown when in stack (not root)
- **Title** — Centered on iOS, left-aligned on Android/Web
- **Actions** — Right side (search, menu, etc.)

---

## 📱 Screen Inventory

### Complete Screen List

| # | Screen | Purpose | Access | Auth Required |
|---|--------|---------|--------|---------------|
| 1 | **SplashScreen** | Brand reveal, auth check | Auto on launch | ❌ |
| 2 | **WelcomeScreen** | Marketing intro | Auto if not logged in | ❌ |
| 3 | **LoginScreen** | Sign in | From Welcome | ❌ |
| 4 | **RegisterScreen** | Create account | From Welcome | ❌ |
| 5 | **OnboardingIntro** | Explain flow | Auto after register | ✅ |
| 6 | **GenreSelection** | Pick favorite genres | Continue from intro | ✅ |
| 7 | **RateInitialBooks** | Rate 5-10 books | Continue from genres | ✅ |
| 8 | **PersonalizingScreen** | ML loading state | Auto after ratings | ✅ |
| 9 | **HomeScreen** | Personalized recs | Main tab | ✅ |
| 10 | **SearchScreen** | Book search | Main tab | ❌ |
| 11 | **BookDetailsScreen** | Full book info | From any book tap | ❌ |
| 12 | **RatingModal** | Rate a book | From book details | ✅ |
| 13 | **LibraryScreen** | User's books | Main tab | ✅ |
| 14 | **InsightsScreen** | Reading DNA | Main tab | ✅ |
| 15 | **ProfileScreen** | User profile | Main tab | ✅ |
| 16 | **SettingsScreen** | App settings | From Profile | ✅ |
| 17 | **EditProfileScreen** | Edit info | From Profile | ✅ |
| 18 | **AboutScreen** | App info | From Settings | ❌ |

---

## 🚀 Flow 1: First-Time User Onboarding

### Purpose
Convert a new visitor into an active user with personalized recommendations within 3 minutes.

### Entry Points
- App launched for first time (no auth token)
- User taps "Get Started" on WelcomeScreen

### Exit Points
- ✅ Success: Land on HomeScreen with personalized recommendations
- ⚠️ Failure: Back to Welcome (if abandoned)

### Complete Flow Diagram

```
┌─────────────────┐
│  App Launched   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ SplashScreen 🔄 │  Duration: 1-2s
│ (Logo + brand)  │  Check: Auth token exists?
└────────┬────────┘
         │
         ▼
       ┌───────────────┐
       │ Token exists? │
       └───┬───────┬───┘
           │ No    │ Yes
           ▼       │
┌─────────────────┐│
│ WelcomeScreen   ││  User sees:
│ - Logo          ││  - Hero image
│ - Value prop    ││  - "Get Started" CTA
│ - "Get Started" ││  - "Already have account? Sign in"
│ - "Sign in"     ││
└────────┬────────┘│
         │         │
    ┌────┴────┐    │
    │ Signup? │    │
    └─┬─────┬─┘    │
      │ Yes │ No   │
      ▼     │      │
┌──────────┐│      │
│ Register ││      │
│ - Name   ││      │
│ - Email  ││      │
│ - Passwd ││      │
│ [Submit] ││      │
└────┬─────┘│      │
     │      │      │
     │      ▼      │
     │ ┌─────────┐ │
     │ │ Login   │ │
     │ │ - Email │ │
     │ │ - Passwd│ │
     │ │[Submit] │ │
     │ └────┬────┘ │
     │      │      │
     │      ▼      │
     │  ┌─────────┐│
     │  │Valid?   ││
     │  └─┬─────┬─┘│
     │    │ Yes │No│
     │    │     │  │
     │    │     ▼  │
     │    │  [Error │
     │    │   toast]│
     │    │        │
     │    └────────┼──────► Skip to HomeScreen
     │             │
     ▼             │
┌─────────────────┐│
│Register Success ││
│ + Auto-login    ││
└────────┬────────┘│
         │         │
         ▼         │
┌─────────────────┐│
│OnboardingIntro  ││  User sees:
│"Let's find your ││  - 3-slide carousel
│  next read"     ││  - Skip button (top right)
│                 ││  - "Get Started" CTA
└────────┬────────┘│
         │         │
         ▼         │
┌─────────────────┐│
│Genre Selection  ││  User picks:
│Pick 3+ genres:  ││  - At least 3 genres
│                 ││  - Visual grid (12 options)
│ 📚 Fiction      ││  - "Continue" enabled when 3+ selected
│ 📖 Non-fiction  ││
│ 🔬 Sci-Fi       ││
│ 💔 Romance      ││
│ 🕵️ Mystery      ││
│ [12 total...]   ││
│                 ││
│ [Continue →]    ││
└────────┬────────┘│
         │         │
         ▼         │
┌─────────────────┐│
│RateInitialBooks ││  User sees:
│Rate 5 books:    ││  - Grid of 15 popular books
│                 ││  - From selected genres
│ [Book1] ⭐⭐⭐⭐⭐ ││  - 5-star rating for each
│ [Book2] ⭐⭐⭐   ││  - "Haven't read" skip option
│ [Book3] ⭐⭐⭐⭐  ││  - Progress: "3/5 rated"
│ [Book4] Skip    ││  - "Continue" enabled at 5 rated
│ [Book5] ⭐⭐    ││
│                 ││
│ Progress: 5/5   ││
│ [Continue →]    ││
└────────┬────────┘│
         │         │
         ▼         │
┌─────────────────┐│
│Personalizing 🔄 ││  User sees:
│                 ││  - Animated bee mascot
│ 🐝              ││  - "Kit is analyzing your taste..."
│ Training your   ││  - Progress bar (fake but reassuring)
│ personal AI...  ││  - Duration: 2-3s
│ ████████░░ 80%  ││  - Backend: async ML processing
└────────┬────────┘│
         │         │
         ▼         │
┌─────────────────┐│
│  HomeScreen ✅  │◄┘  User arrives at personalized home
│                 │    - "Welcome, [Name]!"
│ Your first recs │    - Top 10 recommendations ready
│ are ready! 🎉   │    - Onboarding complete flag set
└─────────────────┘
```

### Screen-by-Screen Details

#### SplashScreen (1-2 seconds)
- **Purpose:** Brand impression + auth check
- **Elements:** Kitabee logo (animated), tagline
- **Actions:** None (auto-transitions)
- **Backend:** Check for stored JWT token
- **Success:** Route based on auth state
- **Failure:** Route to Welcome (default)

#### WelcomeScreen
- **Purpose:** Convert visitor to signup
- **Elements:**
  - Kitabee logo (top)
  - Hero image (reading illustration)
  - Headline: "Discover your next great read"
  - Subheadline: "AI-powered book recommendations"
  - Primary CTA: "Get Started" (yellow button)
  - Secondary link: "Already have an account? Sign in"
- **Actions:**
  - Tap "Get Started" → RegisterScreen
  - Tap "Sign in" → LoginScreen

#### RegisterScreen
- **Purpose:** Create account
- **Elements:**
  - Back button
  - Title: "Create Account"
  - Form fields:
    - Name (required, 2-50 chars)
    - Email (required, valid format)
    - Password (required, 8+ chars, 1 uppercase, 1 number)
    - Password confirmation
  - Submit button: "Sign Up"
  - Legal: "By signing up, you agree to..."
- **Validation:**
  - Real-time field validation
  - Show password strength indicator
  - Disable submit until valid
- **Actions:**
  - Successful register → OnboardingIntro
  - API error → Show error toast
- **Backend:** POST `/api/v1/auth/register`

#### OnboardingIntro (3-slide carousel)
- **Slide 1:** "Meet Kit 🐝 — Your reading buddy"
- **Slide 2:** "Rate books you love, get personalized picks"
- **Slide 3:** "Discover your Reading DNA"
- **Actions:**
  - Swipe/tap through slides
  - "Skip" (top right) → GenreSelection
  - "Get Started" (last slide) → GenreSelection

#### GenreSelection
- **Purpose:** Solve cold-start problem (part 1)
- **Elements:**
  - Header: "What do you love to read?"
  - Subheader: "Pick at least 3 genres"
  - Grid of 12 genre tiles with icons
  - Selected genres highlighted
  - Bottom: "Continue" button (disabled until 3+)
- **Actions:**
  - Tap genre → Toggle selected
  - Tap Continue → RateInitialBooks
- **Data stored:** User preferences in DB

#### RateInitialBooks
- **Purpose:** Solve cold-start problem (part 2)
- **Elements:**
  - Header: "Rate a few books you've read"
  - Progress: "X of 5 rated"
  - Vertical list of 15 popular books (from selected genres)
  - Each book: cover, title, author, 5-star rating input
  - "Haven't read this" button
  - Continue button (enabled at 5 ratings)
- **Actions:**
  - Tap stars → Set rating (1-5)
  - Tap "Haven't read" → Skip to next
  - Rate 5+ books → Enable Continue
  - Tap Continue → PersonalizingScreen
- **Backend:** POST `/api/v1/ratings` (bulk)

#### PersonalizingScreen (2-3 seconds)
- **Purpose:** Set expectation + build anticipation
- **Elements:**
  - Bee mascot animation
  - "Kit is analyzing your taste..."
  - Animated progress bar
  - Rotating fun facts: "Did you know? Kitabee uses 8 AI models..."
- **Actions:** None (auto-transition)
- **Backend:** Trigger ML model refresh (async)
- **Duration:** Min 2s (feel important), max 5s (patience limit)

---

## 🔐 Flow 2: Returning User Login

### Purpose
Get returning users to their personalized home in under 10 seconds.

### Complete Flow

```
┌─────────────────┐
│ App Launched    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ SplashScreen 🔄 │  Check: Stored JWT valid?
└────────┬────────┘
         │
    ┌────┴────┐
    │ Token?  │
    └─┬─────┬─┘
      │ Yes │ No
      ▼     ▼
┌─────────┐┌──────────┐
│Validate ││ Welcome  │
│ token   ││ Screen   │
└────┬────┘└────┬─────┘
     │          │
 ┌───┴───┐      ▼
 │Valid? │  ┌────────┐
 └─┬───┬─┘  │ Login  │
   │Yes│No  │ Screen │
   │   │    └───┬────┘
   │   │        │
   │   └────────┤
   │            ▼
   │       [Enter creds]
   │            │
   │            ▼
   │       [Validate]
   │            │
   │       ┌────┴────┐
   │       │Success? │
   │       └─┬─────┬─┘
   │         │Yes  │No
   │         │     │
   │         │     ▼
   │         │  [Error toast]
   │         │  "Invalid email/password"
   │         │
   │         │  ┌──────────────┐
   │         │  │ Forgot Pass? │
   │         │  │ (Post-MVP)   │
   │         │  └──────────────┘
   │         │
   ▼         ▼
┌─────────────────┐
│  HomeScreen ✅  │  User arrives home
└─────────────────┘
```

### Login Screen Details

- **Elements:**
  - Back button → Welcome
  - Title: "Welcome back!"
  - Email field
  - Password field (with show/hide toggle)
  - "Forgot password?" link (Post-MVP: shows "Coming soon")
  - "Sign In" button
  - Divider: "or"
  - Social sign-in (Post-MVP)
  - "New here? Create account" link
- **Validation:**
  - Email format check
  - Password non-empty
- **Actions:**
  - Submit → API call
  - Success → HomeScreen (skip onboarding if `onboarding_completed=true`)
  - Failure → Error toast with retry
- **Backend:** POST `/api/v1/auth/login`

---

## 📚 Flow 3: Book Discovery (Home Screen)

### Purpose
Present personalized recommendations that inspire the user to explore books.

### Home Screen Layout

```
┌─────────────────────────────────────────┐
│  Kitabee                    🔔  ⚙️      │  Header
├─────────────────────────────────────────┤
│                                         │
│  Good evening, Priya 👋                 │  Personalized greeting
│                                         │
│  ┌────────────────────────────────────┐ │
│  │ 🎯 Recommended for You             │ │
│  │                                    │ │
│  │ [Book1] [Book2] [Book3] [Book4]  ►│ │  Horizontal scroll
│  │                                    │ │
│  └────────────────────────────────────┘ │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │ 🔥 Trending Now                    │ │
│  │                                    │ │
│  │ [Book1] [Book2] [Book3] [Book4]  ►│ │
│  │                                    │ │
│  └────────────────────────────────────┘ │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │ 👥 Readers Like You Loved          │ │
│  │                                    │ │
│  │ [Book1] [Book2] [Book3] [Book4]  ►│ │
│  │                                    │ │
│  └────────────────────────────────────┘ │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │ 📖 Based on [Recent Rating]        │ │
│  │                                    │ │
│  │ [Book1] [Book2] [Book3] [Book4]  ►│ │
│  │                                    │ │
│  └────────────────────────────────────┘ │
│                                         │
├─────────────────────────────────────────┤
│  🏠     🔍     📖     📊     👤         │  Tab bar
└─────────────────────────────────────────┘
```

### Home Screen Flow

```
┌─────────────────┐
│  HomeScreen 🔄  │  Loading state on entry
└────────┬────────┘
         │
         ▼
    [Fetch data]
    ├─ GET /recommendations
    ├─ GET /books/trending
    └─ GET /users/me
         │
    ┌────┴────┐
    │Success? │
    └─┬─────┬─┘
      │Yes  │No
      ▼     ▼
┌──────────┐┌──────────────┐
│ Show     ││ Error state  │
│ sections ││ + Retry btn  │
└────┬─────┘└──────────────┘
     │
     ▼
[User Actions]
     │
     ├─► Tap book card ────► BookDetailsScreen
     │
     ├─► Swipe horizontally ─► Scroll section
     │
     ├─► Pull to refresh ────► Re-fetch data
     │
     ├─► Tap "See all" ──────► Section list view (Post-MVP)
     │
     └─► Tap bell icon ──────► Notifications (Post-MVP)
```

### Book Card Component

```
┌──────────────┐
│              │
│  📚          │  Book cover (2:3 ratio)
│  [Cover]     │  
│              │
├──────────────┤
│ Book Title   │  1-2 lines (truncated)
│ Author Name  │  1 line
│ ⭐ 4.5       │  Average rating
└──────────────┘

On tap: Navigate to BookDetailsScreen
Long press: Quick actions (Add to library, Rate)
```

### Personalization Logic

**"Recommended for You" section:**
- Powered by hybrid ML model (Content + Collaborative + Neural)
- Refreshed every 24 hours OR on new rating
- Shows top 10 books
- Each book has "Why?" tooltip explaining the recommendation

**"Trending Now" section:**
- NYT Books API bestsellers
- Filtered by user's preferred genres
- Refreshed weekly

**"Readers Like You Loved" section:**
- KMeans clustering finds similar users
- Books highly rated by cluster mates
- User hasn't rated these

**"Based on [Recent Rating]" section:**
- TF-IDF similar books to user's last 5-star rating
- Direct connection: "You loved X, try Y"

---

## 🔍 Flow 4: Book Search

### Purpose
Enable users to find any book by title, author, or ISBN in real-time.

### Search Screen Layout

```
┌─────────────────────────────────────────┐
│  ┌────────────────────────────────┐ ✕   │
│  │ 🔍 Search books, authors...    │     │  Search input
│  └────────────────────────────────┘     │
├─────────────────────────────────────────┤
│                                         │
│  Filter by: [All ▼] [Genre ▼]           │  Filter chips
│                                         │
│  Popular searches:                      │  When empty
│  #Fiction #SciFi #Biography             │
│                                         │
│  Recent searches:                       │  When user has history
│  🕐 Sapiens                             │
│  🕐 Harry Potter                        │
│  🕐 Atomic Habits                       │
│                                         │
├─────────────────────────────────────────┤
```

### Search Flow

```
┌─────────────────┐
│  SearchScreen   │  Empty state on entry
└────────┬────────┘
         │
    [User types]
         │
    [300ms debounce]
         │
         ▼
    [Show loading]
         │
    ┌────┴────┐
    │Query    │
    │valid?   │
    └─┬─────┬─┘
      │Yes  │No (< 2 chars)
      │     ▼
      │  [Show suggestions]
      │
      ▼
[GET /api/v1/books/search?q=...]
      │
      ▼
[Try Redis cache]
      │
  ┌───┴────┐
  │ Cached?│
  └─┬────┬─┘
    │Yes │No
    │    ▼
    │ [Try Google Books API]
    │    │
    │ ┌──┴──┐
    │ │OK?  │
    │ └┬──┬─┘
    │  │Y │N
    │  │  ▼
    │  │ [Fallback to Open Library]
    │  │  │
    │  │  └───┐
    │  ▼      ▼
    │ [Cache result]
    │  │
    ▼  ▼
[Show results]
      │
      ▼
[User Actions]
      │
      ├─► Tap result ────► BookDetailsScreen
      │
      ├─► Clear search ──► Reset to empty state
      │
      ├─► Apply filter ──► Refine results
      │
      └─► Scroll ────────► Pagination (load more)
```

### Search States

#### Empty State (First Visit)
- Popular searches (tags)
- Suggestions: "Try 'Sapiens' or 'Harry Potter'"

#### Empty State (Returning User)
- Recent searches (last 10)
- Tap to re-search
- Swipe to delete

#### Loading State
- Skeleton loaders (5 placeholder cards)
- Shimmer effect

#### Results State
- Vertical list of book cards
- Each card: cover, title, author, rating, "Add" button
- Pagination: Load 20 at a time
- Empty result: "No books found for 'xyz'. Try different keywords."

#### Error State
- Sad bee illustration 🐝
- "Something went wrong"
- "Retry" button

### Search Optimizations

- **Debouncing:** 300ms delay before API call
- **Caching:** 30-minute Redis TTL for queries
- **Prefetching:** Fetch details on card hover (web)
- **History:** Store last 10 searches locally
- **Autocomplete:** Show recent + popular suggestions

---

## 📖 Flow 5: Book Details & Rating

### Purpose
Provide rich book information and enable users to rate/save books.

### Book Details Screen Layout

```
┌─────────────────────────────────────────┐
│  ←                                  ⋮   │  Header
├─────────────────────────────────────────┤
│                                         │
│         ┌──────────────┐                │
│         │              │                │
│         │              │                │
│         │   [Cover]    │                │  Hero section
│         │              │                │  (Blurred bg with cover)
│         │              │                │
│         └──────────────┘                │
│                                         │
│         Sapiens                         │  Title
│         by Yuval Noah Harari            │  Author
│         ⭐ 4.5 (12,345 ratings)         │  Rating summary
│                                         │
│  ┌──────────┬──────────┬──────────┐     │
│  │ +Library │  Rate    │  Share   │     │  Action buttons
│  └──────────┴──────────┴──────────┘     │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  🎯 Why we recommend this               │  AI explanation
│  Based on your love for "Homo Deus"     │  (Only if from recs)
│  and 87% of users like you.             │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  📖 About                               │
│  Sapiens is a compelling narrative of   │  Description
│  humanity from cave-dwellers to...      │  (Read more)
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  💬 Sentiment Analysis                  │  NLP feature
│  ┌────────────────────────────────┐     │
│  │ 😊 Positive: 78%               │     │
│  │ 😐 Neutral:  15%               │     │
│  │ 😞 Negative:  7%               │     │
│  └────────────────────────────────┘     │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  📚 Similar Books                       │
│  [Book1] [Book2] [Book3] [Book4] ►      │
│                                         │
│  ─────────────────────────────────────  │
│                                         │
│  ℹ️ Details                             │
│  Published: 2011                        │
│  Pages: 464                             │
│  Publisher: Harper                      │
│  ISBN: 978-0062316097                   │
│                                         │
└─────────────────────────────────────────┘
```

### Book Details Flow

```
┌─────────────────────┐
│ BookDetailsScreen 🔄│
└──────────┬──────────┘
           │
           ▼
      [Fetch book data]
      GET /books/{id}
           │
       ┌───┴────┐
       │Cached? │
       └─┬────┬─┘
         │Yes │No
         │    ▼
         │ [Fetch from API]
         │    │
         │    ▼
         │ [Cache in Redis]
         ▼    │
      ┌──────┘
      ▼
   [Fetch related]
   ├─ Similar books
   ├─ User rating (if any)
   └─ Sentiment analysis
      │
      ▼
   [Render screen]
      │
      ▼
[User Actions]
      │
      ├─► Tap "+ Library" ─► Show library modal
      │                       │
      │                       ├─ Want to Read
      │                       ├─ Currently Reading
      │                       └─ Read
      │
      ├─► Tap "Rate" ──────► Show RatingModal
      │                       │
      │                       └─► [Rate flow below]
      │
      ├─► Tap "Share" ─────► Native share dialog
      │
      ├─► Tap similar book ► New BookDetailsScreen
      │
      └─► Tap "Read more" ─► Expand description
```

### Rating Modal Flow

```
┌────────────────────────┐
│    Rate this book      │
├────────────────────────┤
│                        │
│  How would you rate    │
│  "Sapiens"?            │
│                        │
│    ⭐ ⭐ ⭐ ⭐ ⭐       │  Interactive stars
│                        │
│  ┌──────────────────┐  │
│  │ Add a review     │  │  Optional text
│  │ (optional)       │  │
│  └──────────────────┘  │
│                        │
│  ┌──────────────────┐  │
│  │    Submit        │  │
│  └──────────────────┘  │
│                        │
│         Cancel         │
└────────────────────────┘

Flow:
[Tap stars] → [Optional review] → [Submit]
                                     │
                                     ▼
                              [POST /ratings]
                                     │
                                 ┌───┴────┐
                                 │Success?│
                                 └─┬────┬─┘
                                   │Yes │No
                                   ▼    ▼
                              [Success ┌────────┐
                               toast]  │Error   │
                                       │toast   │
                                   │   └────────┘
                                   ▼
                              [Modal closes]
                                   │
                                   ▼
                              [Recommendations
                               refresh async]
```

---

## 📚 Flow 6: Personal Library Management

### Purpose
Let users organize books they've engaged with into meaningful categories.

### Library Screen Layout

```
┌─────────────────────────────────────────┐
│  My Library                        🔍   │  Header
├─────────────────────────────────────────┤
│                                         │
│  Want (12) │ Reading (3) │ Read (47)    │  Tabs
│  ─────────                              │  Active tab underlined
│                                         │
│  Sort by: [Recently added ▼]            │  Sort options
│  View: [Grid] [List]                    │  View toggle
│                                         │
│  ┌────┐ ┌────┐ ┌────┐                   │
│  │📚 │ │📚 │ │📚 │                     │  Book grid
│  │Cvr│ │Cvr│ │Cvr│                     │
│  └────┘ └────┘ └────┘                   │
│  Title  Title  Title                    │
│  Author Author Author                   │
│                                         │
│  ┌────┐ ┌────┐ ┌────┐                   │
│  │📚 │ │📚 │ │📚 │                     │
│  │Cvr│ │Cvr│ │Cvr│                     │
│  └────┘ └────┘ └────┘                   │
│                                         │
└─────────────────────────────────────────┘
```

### Library Flow

```
┌─────────────────┐
│ LibraryScreen   │
└────────┬────────┘
         │
         ▼
    [Load library]
    GET /library?status=want_to_read
         │
    ┌────┴────┐
    │ Empty?  │
    └─┬─────┬─┘
      │Yes  │No
      │     ▼
      │  [Show grid]
      │
      ▼
┌──────────────────┐
│  Empty state 📭  │  "Your library is empty"
│  🐝              │  "Start by rating books!"
│  [Explore books] │  CTA → HomeScreen
└──────────────────┘

[User Actions]
      │
      ├─► Tap tab ────────► Filter by status
      │
      ├─► Tap book ───────► BookDetailsScreen
      │
      ├─► Long press ─────► Quick actions menu
      │                     │
      │                     ├─ Move to "Reading"
      │                     ├─ Move to "Read"
      │                     ├─ Remove from library
      │                     └─ Rate (if not rated)
      │
      ├─► Change sort ────► Re-order list
      │
      └─► Toggle view ────► Grid ↔ List
```

### Library Status Transitions

```
       ┌───────────────┐
       │ Want to Read  │
       └───────┬───────┘
               │
     "Start Reading"
               │
               ▼
       ┌───────────────┐
       │Currently      │
       │Reading        │
       └───────┬───────┘
               │
      "Mark as Read"
               │
               ▼
       ┌───────────────┐
       │     Read      │
       └───────────────┘

Additional flows:
- Remove: Any status → Removed
- Add: Book Details → Want to Read (default)
- Direct add: Rated 4-5 stars → Prompt "Add to Read?"
```

---

## 📊 Flow 7: Reading Insights (DNA)

### Purpose
Show users their unique reading personality through beautiful data visualizations.

### Insights Screen Layout

```
┌─────────────────────────────────────────┐
│  Your Reading DNA 🧬          [Share]   │  Header
├─────────────────────────────────────────┤
│                                         │
│  ┌────────────────────────────────────┐ │
│  │  🐝 You're a                       │ │  Personality
│  │  "Contemplative Explorer"          │ │
│  │                                    │ │
│  │  You love complex characters,      │ │
│  │  philosophical themes, and         │ │
│  │  non-linear narratives.            │ │
│  └────────────────────────────────────┘ │
│                                         │
│  📊 Genre Breakdown                     │  Pie chart
│  ┌────────────────────────────────────┐ │
│  │      ┌─────┐                       │ │
│  │      │Fic  │ 40%                   │ │
│  │      │Non  │ 30%                   │ │
│  │      │SciFi│ 20%                   │ │
│  │      │Other│ 10%                   │ │
│  │      └─────┘                       │ │
│  └────────────────────────────────────┘ │
│                                         │
│  📈 Reading Pace (Last 6 Months)        │  Line chart
│  ┌────────────────────────────────────┐ │
│  │  📚                                │ │
│  │  6│    ▲                           │ │
│  │  4│   ╱ ╲   ▲                      │ │
│  │  2│  ╱   ╲ ╱ ╲                     │ │
│  │  0└──────────────                  │ │
│  │    J F M A M J                     │ │
│  └────────────────────────────────────┘ │
│                                         │
│  🏆 Top Authors                         │  List
│  1. Yuval Noah Harari (3 books)         │
│  2. Malcolm Gladwell (2 books)          │
│  3. Michelle Obama (2 books)            │
│                                         │
│  🌍 Diversity Score                     │  Metric
│  ┌────────────────────────────────────┐ │
│  │  8.5/10                            │ │
│  │  Above average! You explore        │ │
│  │  diverse voices.                   │ │
│  └────────────────────────────────────┘ │
│                                         │
│  📅 Reading Timeline                    │  Optional
│                                         │
└─────────────────────────────────────────┘
```

### Insights Flow

```
┌──────────────────┐
│ InsightsScreen 🔄│
└────────┬─────────┘
         │
         ▼
    [Fetch analytics]
    GET /insights/dna
         │
    ┌────┴────┐
    │Enough   │  Need 10+ rated books
    │data?    │  for meaningful insights
    └─┬─────┬─┘
      │Yes  │No
      │     ▼
      │  ┌──────────────────┐
      │  │  Empty state 📭  │
      │  │  "Rate 10 books  │
      │  │  to unlock your  │
      │  │  Reading DNA"    │
      │  │  Progress: 3/10  │
      │  └──────────────────┘
      ▼
[Render dashboard]
   │
   ├─ Personality profile
   ├─ Genre pie chart
   ├─ Reading pace chart
   ├─ Top authors
   └─ Diversity score
   │
   ▼
[User Actions]
   │
   ├─► Tap chart ─────► Detailed view
   │
   ├─► Tap share ─────► Generate image + share
   │
   └─► Pull refresh ──► Regenerate insights
```

### Reading DNA Personalities (Examples)

- 🔮 **Contemplative Explorer** — Philosophy, deep non-fiction
- 🎭 **Story Lover** — Fiction, character-driven narratives
- 🚀 **Future Thinker** — Sci-fi, technology, futurism
- 🧠 **Knowledge Seeker** — Non-fiction, education, self-help
- 💔 **Emotion Reader** — Romance, drama, memoirs
- 🕵️ **Mystery Detective** — Crime, thriller, suspense
- 🌍 **Cultural Traveler** — International, diverse voices
- 📖 **Classic Enthusiast** — Older, timeless literature

**Algorithm:** KMeans clustering on user's rated books' features

---

## 👤 Flow 8: Profile & Settings

### Profile Screen Layout

```
┌─────────────────────────────────────────┐
│  Profile                          ⚙️    │  Header
├─────────────────────────────────────────┤
│                                         │
│         ┌──────────────┐                │
│         │   [Avatar]   │                │  Profile pic
│         └──────────────┘                │
│                                         │
│         Priya Sharma                    │  Name
│         priya@example.com               │  Email
│                                         │
│  ┌───────┬───────┬───────┬───────┐      │  Stats
│  │  47   │  12   │  4.2  │  8.5  │      │
│  │Books  │In Lib │  Avg  │Divers │      │
│  │ Read  │       │ Rating│ Score │      │
│  └───────┴───────┴───────┴───────┘      │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │ 👤 Edit Profile             →      │ │
│  ├────────────────────────────────────┤ │
│  │ 🔔 Notifications            →      │ │
│  ├────────────────────────────────────┤ │
│  │ 🎨 Theme              Light  →     │ │
│  ├────────────────────────────────────┤ │
│  │ 🔒 Privacy                  →      │ │
│  ├────────────────────────────────────┤ │
│  │ ℹ️ About                    →      │ │
│  ├────────────────────────────────────┤ │
│  │ ❓ Help & Support           →      │ │
│  └────────────────────────────────────┘ │
│                                         │
│  ┌────────────────────────────────────┐ │
│  │        Log Out                     │ │  Danger action
│  └────────────────────────────────────┘ │
│                                         │
└─────────────────────────────────────────┘
```

### Settings Flow

```
Profile Screen
     │
     ├─► Tap "Edit Profile" ──► EditProfileScreen
     │                          - Name, email, avatar
     │                          - Save button
     │
     ├─► Tap "Notifications" ──► NotificationsScreen
     │                          - Toggle categories
     │                          - Post-MVP
     │
     ├─► Tap "Theme" ──────────► ThemeMenu
     │                          - Light
     │                          - Dark
     │                          - System
     │
     ├─► Tap "Privacy" ────────► PrivacyScreen
     │                          - Data export
     │                          - Delete account
     │
     ├─► Tap "About" ──────────► AboutScreen
     │                          - Version
     │                          - Credits
     │                          - Links
     │
     └─► Tap "Log Out" ────────► Confirmation dialog
                                 │
                             ┌───┴────┐
                             │Confirm?│
                             └─┬────┬─┘
                               │Yes │No
                               ▼    ▼
                          [Clear token]  [Dismiss]
                          [Navigate to
                           Welcome]
```

---

## 🎬 Screen States

### Universal State Types

Every screen has 4 potential states:

```
┌─────────────────┐
│  Loading  🔄    │  Data being fetched
├─────────────────┤
│  Success  ✅    │  Data loaded, ready
├─────────────────┤
│  Error   ⚠️     │  Something failed
├─────────────────┤
│  Empty   📭     │  Loaded but no data
└─────────────────┘
```

### State Transitions

```
     [Enter Screen]
           │
           ▼
       [Loading]
           │
      ┌────┴────┐
      │         │
      ▼         ▼
   [Success] [Error]
      │         │
      │         ├─► [Retry] → Loading
      │         │
      ▼         └─► [Back]
   [Empty?]
      │
   ┌──┴──┐
   │ Yes │
   ▼
[Empty state]
```

---

## ⚠️ Error Handling Flows

### Error Types & Responses

| Error Type | Detection | User Sees | Action |
|------------|-----------|-----------|--------|
| **Network offline** | fetch fails | Offline banner | Auto-retry when online |
| **API timeout** | 30s timeout | "Taking longer than expected" | Retry button |
| **401 Unauthorized** | Token invalid | Silent redirect to Login | Auto-logout |
| **403 Forbidden** | Permission denied | "You don't have access" | Back button |
| **404 Not Found** | Resource missing | "Book not found" | Back button |
| **500 Server Error** | Backend crash | "Something went wrong" | Retry button |
| **Rate limit (429)** | Too many requests | "Slow down!" | Countdown timer |

### Global Error Handling

```
API Response
     │
     ▼
[HTTP status check]
     │
  ┌──┴──┐
  │2xx? │
  └┬───┬┘
   │Yes│No
   │   ▼
   │ [Error type?]
   │   │
   │   ├─ 401 ─► Logout + Redirect
   │   ├─ 429 ─► Show cooldown UI
   │   ├─ 5xx ─► Show generic error + retry
   │   └─ Other ─► Show specific message
   ▼
[Success handler]
```

### Error UI Component

```
┌────────────────────────┐
│                        │
│         😕            │  Sad bee illustration
│                        │
│   Oops! Something      │
│   went wrong.          │
│                        │
│   [Error message]      │
│                        │
│  ┌──────────────────┐  │
│  │     Try Again    │  │  Primary action
│  └──────────────────┘  │
│                        │
│         Go Back        │  Secondary action
│                        │
└────────────────────────┘
```

---

## 📭 Empty States

### When Empty States Appear

| Screen | Empty Condition | CTA |
|--------|-----------------|-----|
| **Home** | No recommendations yet | "Rate books to get started" |
| **Search** | No results for query | "Try different keywords" |
| **Library (Want)** | No books added | "Explore recommendations" |
| **Library (Reading)** | Not reading anything | "Move a book from Want to Read" |
| **Library (Read)** | Haven't finished any | "Rate books you've read" |
| **Insights** | < 10 books rated | "Rate 10 books to unlock" |
| **Ratings history** | No ratings yet | "Start rating books" |

### Empty State Template

```
┌────────────────────────┐
│                        │
│         🐝             │  Illustration
│                        │
│   [Contextual title]   │  Empty message
│                        │
│   [Helpful subtitle]   │  Explanation
│                        │
│  ┌──────────────────┐  │
│  │  [Primary CTA]   │  │  Action button
│  └──────────────────┘  │
│                        │
└────────────────────────┘
```

---

## 🔄 Loading States

### Loading Patterns

**Pattern 1: Full-Screen Loader**
- Used for: Initial screen loads, splash
- UI: Centered spinner + Kitabee logo

**Pattern 2: Skeleton Screens**
- Used for: List/grid content
- UI: Grey placeholder shapes matching final layout
- Shimmer animation

**Pattern 3: Inline Loader**
- Used for: Button actions, form submissions
- UI: Small spinner replacing button text

**Pattern 4: Progress Bar**
- Used for: Multi-step processes (uploads)
- UI: Determinate progress bar

**Pattern 5: Optimistic UI**
- Used for: Rating a book, adding to library
- UI: Instant feedback, sync in background

---

## ✅ Success States

### Success Feedback Types

| Action | Feedback Type | Duration |
|--------|---------------|----------|
| **Rate a book** | Toast + confetti | 2s |
| **Add to library** | Toast + haptic | 1.5s |
| **Save profile** | Toast | 2s |
| **Login** | Screen transition | Immediate |
| **Register** | Welcome message | Persistent |

### Success Toast Template

```
┌──────────────────────────────┐
│  ✅  Book rated!             │
│      "Sapiens" - 5 stars     │
└──────────────────────────────┘

Position: Top of screen
Duration: 2 seconds
Animation: Slide down + fade
```

---

## 🌐 Cross-Platform Considerations

### Platform-Specific Behaviors

| Feature | Web | iOS | Android |
|---------|-----|-----|---------|
| **Back navigation** | Browser back | Swipe from edge | Hardware back |
| **Pull to refresh** | ❌ | ✅ | ✅ |
| **Haptic feedback** | ❌ | ✅ | ✅ (limited) |
| **Share sheet** | Web Share API | Native | Native |
| **Deep linking** | URLs | Universal Links | App Links |
| **Storage** | localStorage | AsyncStorage | AsyncStorage |
| **Modals** | Overlay | Bottom sheet | Bottom sheet |
| **Keyboard handling** | Auto | KeyboardAvoiding | KeyboardAvoiding |

### Responsive Breakpoints

```
Mobile:   0 - 767px       (single column)
Tablet:   768 - 1023px    (two columns)
Desktop:  1024px+          (max-width: 1200px, centered)
```

---

## ♿ Accessibility Flows

### Screen Reader Support

**Every interactive element has:**
- Accessibility label
- Accessibility hint (if action unclear)
- Accessibility role (button, link, etc.)

**Example:**
```typescript
<TouchableOpacity
  accessibilityLabel="Rate this book"
  accessibilityHint="Opens rating modal"
  accessibilityRole="button"
>
```

### Keyboard Navigation (Web)

- **Tab** — Move focus forward
- **Shift+Tab** — Move focus backward
- **Enter/Space** — Activate button
- **Esc** — Close modal
- **Arrow keys** — Navigate lists

### Color Contrast

All text meets WCAG AA:
- Normal text: 4.5:1 ratio
- Large text: 3:1 ratio
- Interactive elements: 3:1 ratio

---

## 📊 Analytics Events

### Events to Track (Post-MVP)

| Event | Trigger | Data |
|-------|---------|------|
| **app_open** | App launched | user_id, timestamp |
| **screen_view** | Screen displayed | screen_name |
| **book_view** | Book details opened | book_id, source |
| **search** | Search executed | query, results_count |
| **rating_submitted** | Book rated | book_id, rating |
| **library_add** | Book added to library | book_id, status |
| **recommendation_click** | Rec tapped | book_id, model_type, position |
| **onboarding_complete** | Setup finished | duration, books_rated |

---

## 📎 Appendix

### Related Documents
- [PRD.md](./PRD.md) — Product requirements
- [TECHSPEC.md](./TECHSPEC.md) — Technical specification

### Design Assets (Coming Soon)
- Figma mockups: `figma.com/kitabee-designs`
- Brand guidelines: `docs/BRAND.md`

### Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | [Today] | [Your Name] | Initial app flow document |

---

**End of App Flow Document** 🔄

*"Every tap. Every screen. Every state. Documented."*