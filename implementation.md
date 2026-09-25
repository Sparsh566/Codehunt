# Codehunt v2 — Ocean Literacy Gamified Platform (SIH 1660)
## Complete Architecture & Implementation Plan

**Problem Statement:** SIH 1660 — Interactive Gamified Approach to Ocean Literacy  
**Client / Partner:** Ministry of Earth Sciences (MoES) / Indian National Centre for Ocean Information Services (INCOIS)  
**Document Version:** 2.0 (Phase 0 Audit & Roadmap)

---

## 1. Executive Summary & Core Architectural Principles

Codehunt v2 transforms an initial static prototype into an enterprise-grade, role-based ocean decision-training platform. The platform teaches marine stakeholders and citizens how to interpret ocean intelligence (weather advisories, Potential Fishing Zones [PFZ], High Wave Alerts, Ocean State Forecasts, and Tsunami Warnings) and make life-and-livelihood decisions under dynamic maritime conditions.

### Non-Negotiable Core Principles
1. **Deterministic Game Engine (Pure Python):**  
   - All gameplay mechanics, safety evaluations, scoring deltas, and resource/vessel consequences are calculated by **deterministic rule-based pure functions**.
   - **Zero LLM evaluation:** An AI model is **never** used to decide whether a player's action is safe, legal, or optimal. This guarantees safety integrity, auditability, and SIH 1660 compliance.
2. **AI Layer Strictly as Explanatory & Multilingual Tutor:**  
   - Groq (`llama-3.3-70b-versatile`) is called **only post-decision** to translate the engine's verdict into empathetic, contextual, educational explanations in English, Hindi, and regional languages.
3. **Authoritative Retrieval (Tavily):**  
   - Tavily is strictly utilized for the "Learn More" research drawer, restricted to authoritative maritime domains (`incois.gov.in`, `moes.gov.in`, `imd.gov.in`, `oceandecade.org`). It never validates game actions.
4. **Resilience & Graceful Degradation:**  
   - If Groq or Tavily APIs are unreachable or exceed rate limits, the core gameplay loop, deterministic feedback, scoring, and progression proceed without interruption using pre-computed deterministic feedback templates.
5. **Security & Clean Abstraction:**  
   - Zero API keys exposed on client browsers. All calls routed through the FastAPI backend.
   - The Ocean Data Adapter simulates INCOIS REST endpoints today and can be switched to live INCOIS OGC/REST feeds tomorrow via a single environment variable change (`OCEAN_DATA_PROVIDER=live_incois`).

---

## 2. Phase 0: Repository Audit & Canonical UI Recommendation

### 2.1 File-by-File Audit

| File | Type & Tech | Strengths | Limitations | Status in v2 |
| :--- | :--- | :--- | :--- | :--- |
| `Game.html` | Static HTML/CSS/Vanilla JS | Contains **10 complete, high-quality ocean literacy questions** with correct answers and explanations; clean gradient design. | Relies on `localStorage.getItem("loggedInUser")`; hardcoded question array; no timer or backend. | **Question Content Source**: Questions will be seeded into DB. |
| `front.html` | Static HTML/CSS/Vanilla JS | Has active 10s countdown timer, per-question feedback loop, restart quiz action. | Only 4 questions; plain inline styling; no server persistence. | Experimental precursor to `frontend.html`. |
| `frontend.html` | Static HTML/CSS/Vanilla JS | Clean layout, hints system (`hint` + `explanation`), timer, client-side leaderboard calculation. | Only 4 questions; client-side array sorting; no backend auth. | **Recommended Base for Learn Mode UX flow**. |
| `Login.html` | Static HTML/CSS/Vanilla JS | Basic registration and login forms with validation alert banners. | In-memory `const users = {}` wiped on page refresh; stores plaintext credentials. | Replaced by JWT Auth views backed by `/api/auth`. |
| `ui.html` | React / JSX Component | Attempts shadcn/ui buttons and cards with Firebase auth bindings. | Unfinished snippet; imports non-existent `@/components/ui`; not runnable standalone. | Reference only. |
| `ui2.html` | HTML5 Canvas / Vanilla JS | Introduces **Role Selection** (Fisherman, Ship Captain, Marine Scientist) and an HTML5 canvas sea/wave simulation. | Anime character placeholders; no actual decision logic; incomplete canvas loop. | **Inspirational Seed for Play Mode Role Selection**. |
| `ui3.html` | Pre-rendered Next.js Export | Heavy (477KB) bundle export from v0 containing UI component skeletons. | Bloated static snapshot with dead webpack chunks. | Archive / Reference only. |
| `ocean-literacy-game.zip` | Full Next.js 14 / Tailwind codebase | Comprehensive UI kit with Radix UI components, shadcn cards, auth views, and layout wrappers. | Requires Node build setup; heavy dependencies. | Design asset library for future React migrations. |

### 2.2 Canonical UI Recommendation for Learn Mode
**Recommendation:**  
We synthesize the **10 verified ocean curriculum questions from `Game.html`** with the **interactive hints and timer mechanics from `frontend.html`**, refactoring it into a modern, responsive single-page web app in `/frontend/learn.html`.

**Why this combination:**
1. `Game.html` provides the complete 10-question ocean science bank (ocean coverage, Thermohaline Circulation, ocean acidification, coral reefs, Mariana Trench, phytoplankton, etc.).
2. `frontend.html` provides the better pedagogic UX: timed pressure, contextual hints on demand, and immediate feedback before progressing.
3. Unifying them into a single clean frontend served by FastAPI connects the quiz to the real `/api/learn` and `/api/auth` endpoints with zero technical debt.

---

## 3. Clean Target Project Structure

```
Codehunt/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI entry point, CORS, lifespan, router registry
│   │   ├── config.py                # Pydantic BaseSettings (DB URL, Groq, Tavily, JWT secret)
│   │   │
│   │   ├── api/                     # REST API Routers
│   │   │   ├── __init__.py
│   │   │   ├── auth.py              # /api/auth (register, login, me, refresh)
│   │   │   ├── scenarios.py         # /api/scenarios (get active, filter by role)
│   │   │   ├── decisions.py         # /api/decisions (evaluate player choice)
│   │   │   ├── leaderboard.py       # /api/leaderboard (global, role-based, daily/weekly)
│   │   │   ├── analytics.py         # /api/analytics (learner mastery radar, decision logs)
│   │   │   ├── learn.py             # /api/learn (quiz questions, quiz submissions)
│   │   │   └── admin.py             # /api/admin (CRUD scenarios, metrics, system stats)
│   │   │
│   │   ├── game_engine/             # DETERMINISTIC ENGINE (Pure Python, 0% AI)
│   │   │   ├── __init__.py
│   │   │   ├── evaluator.py         # Pure outcome evaluation: safety, score, vessel status
│   │   │   ├── rules.py             # Maritime safety thresholds (Beaufort scale, PFZ, wave limits)
│   │   │   ├── scoring.py           # XP, score calculation, penalties, streak multipliers
│   │   │   └── schemas.py           # Engine input/output Pydantic schemas
│   │   │
│   │   ├── ocean_adapter/           # Simulated / Live INCOIS Ocean Data Service
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # Abstract OceanDataProvider interface
│   │   │   ├── simulated_provider.py# Realistic INCOIS generator (OSF, High Wave, PFZ, Tsunami)
│   │   │   ├── live_incois_provider.py # Plug-in connector for live INCOIS Open Data feeds
│   │   │   └── models.py            # OceanState, PFZAdvisory, MarineWarning dataclasses
│   │   │
│   │   ├── ai_service/              # AI EXPLANATIONS & RETRIEVAL (Only called post-verdict)
│   │   │   ├── __init__.py
│   │   │   ├── groq_explainer.py    # Groq Llama-3.3-70b-versatile client (EN + HI explanations)
│   │   │   ├── tavily_retriever.py  # Authoritative source search (incois.gov.in, moes.gov.in)
│   │   │   └── fallback_engine.py   # Offline deterministic explanatory fallback templates
│   │   │
│   │   ├── models/                  # Database Models (SQLAlchemy 2.0 / SQLModel)
│   │   │   ├── __init__.py
│   │   │   ├── base.py              # DB Base and metadata
│   │   │   ├── user.py              # User account, hashed password, role, total XP
│   │   │   ├── scenario.py          # ScenarioRecord, options, conditions, expected verdict
│   │   │   ├── decision.py          # DecisionLog (user_id, scenario_id, choice, outcome, telemetry)
│   │   │   ├── leaderboard.py       # LeaderboardEntry view / table
│   │   │   ├── learner_profile.py   # LearnerProfile (mastery scores across ocean topics)
│   │   │   └── question.py          # LearnModeQuestion & QuizResult
│   │   │
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── session.py           # SQLAlchemy async/sync session factory (SQLite/PostgreSQL)
│   │   │   └── init_db.py           # Database seeder (seeds questions & play mode scenarios)
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── security.py          # Passlib bcrypt hashing, JWT create/decode tokens
│   │
│   ├── fixtures/
│   │   ├── scenarios_fisherman.json
│   │   ├── scenarios_captain.json
│   │   ├── scenarios_tourism.json
│   │   └── quiz_questions.json
│   │
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_game_engine.py      # Comprehensive unit tests for deterministic engine
│   │   ├── test_ocean_adapter.py    # Unit tests for simulated INCOIS telemetry
│   │   ├── test_auth_api.py         # End-to-end API tests for authentication
│   │   └── test_decisions_api.py    # End-to-end API tests for decision pipeline
│   │
│   ├── requirements.txt             # FastAPI, uvicorn, sqlalchemy, groq, tavily-python, etc.
│   └── .env.example
│
├── frontend/                        # Responsive Client UI (Vanilla HTML5 / Modern CSS / ES6 JS)
│   ├── index.html                   # Landing page: Platform hub, Mode Selection (Learn vs Play)
│   ├── login.html                   # Auth view: Modern modal login & registration
│   ├── learn.html                   # Learn Mode: Refactored timed quiz with hints, explanations
│   ├── play.html                    # Play Mode: Maritime Role Dashboard, Ocean Gauges, Decision Center
│   ├── leaderboard.html            # Live Global & Role-based Leaderboard with daily/weekly filters
│   ├── profile.html                # Learner Analytics: Ocean Literacy Radar Chart, Badges, XP History
│   ├── css/
│   │   ├── style.css                # Oceanic design system (dark marine theme, glassmorphism)
│   │   └── components.css           # Gauges, radar displays, animated telemetry indicators
│   └── js/
│       ├── api.js                   # Unified API client handling JWT storage and REST calls
│       ├── auth.js                  # Login/logout/session validation
│       ├── learn.js                 # Learn Mode quiz logic
│       ├── play.js                  # Play Mode decision loop and ocean telemetry visualizer
│       ├── leaderboard.js           # Leaderboard fetching and rendering
│       └── profile.js               # Analytics and mastery charts
│
├── admin/                           # INCOIS Staff Admin Console
│   ├── index.html                   # Admin Dashboard: Scenario CRUD, question bank, live analytics
│   ├── js/admin.js                  # Scenario management script
│   └── css/admin.css                # Clean administrative styling
│
├── implementation.md                # This comprehensive implementation blueprint
└── README.md                        # Documentation, INCOIS adapter guide, setup instructions
```

---

## 4. Phase-by-Phase Roadmap

### Phase 1: Backend Foundation
- [ ] Scaffold FastAPI backend with CORS, unified exception handlers, and configuration management (`pydantic-settings`).
- [ ] Set up SQLAlchemy database layer (defaults to SQLite `codehunt.db` locally, easily swapped to PostgreSQL/Supabase via `DATABASE_URL`).
- [ ] Implement JWT authentication system (PBKDF2/bcrypt hashing, access token issuing, `/api/auth/me`).
- [ ] Create database models:
  - `User`: id, username, email, hashed_password, role, xp, level, created_at.
  - `ScenarioRecord`: id, role, title, location, telemetry (wave, wind, swell, pfz, advisory), options, recommended_action, consequences.
  - `DecisionLog`: id, user_id, scenario_id, chosen_option, is_safe, score_delta, ai_explanation, created_at.
  - `LearnerProfile`: user_id, ocean_conditions_score, safety_awareness_score, pfz_understanding_score, hazard_response_score.
  - `LearnQuestion`: id, question, options, answer, hint, explanation, category, difficulty.
- [ ] Write DB seeder `init_db.py` to migrate the 10 quiz questions from `Game.html` into the database.

### Phase 2: Deterministic Game Engine & Scenario System
- [ ] Define the official **Scenario JSON Schema** matching INCOIS operational bulletins:
  - Roles: `fisherman`, `ship_captain`, `tourism_operator`.
  - Ocean Parameters: `wave_height_m`, `wind_speed_knots`, `swell_period_sec`, `pfz_zone_active`, `incois_alert_level` (`normal`, `watch`, `alert`, `warning`), `sst_celsius` (Sea Surface Temp).
- [ ] Build **Ocean Data Adapter**:
  - `OceanDataProvider` abstract base class.
  - `SimulatedINCOISProvider`: Deterministic generators and fixture loader that replicates real INCOIS API data structures.
- [ ] Implement **Deterministic Game Engine**:
  - Pure Python evaluation: `evaluate_decision(scenario, chosen_action) -> DecisionVerdict`.
  - Computes `is_safe` (Boolean), `verdict_status` (`optimal`, `suboptimal`, `dangerous`, `catastrophic`), `score_delta` (+100 to -150), `safety_penalty`, and `resource_impact` (fuel, vessel integrity, catch yield).
  - Absolutely **zero AI calls** in the decision verification pipeline.
- [ ] Unit Test Suite: Write pytest tests covering at least 5 critical scenarios across all 3 roles (e.g. Cyclone evacuation, PFZ exploitation vs high swell, Cruise diversion during rough seas, Shallow reef dive during spring tide).

### Phase 3: AI Explanation Layer (Post-Verdict Only)
- [ ] Create `GroqExplainer`:
  - Connects to Groq (`llama-3.3-70b-versatile`).
  - Inputs: Engine's deterministic verdict, scenario conditions, player choice, role.
  - Generates educational breakdown: *Why* the decision was correct/incorrect, citing ocean physics and INCOIS advisory rules.
  - Supports English and Hindi output (`language="en" | "hi"`).
- [ ] Create `TavilyRetriever`:
  - Provides authoritative supplementary context for the "Learn More" drawer.
  - Strict domain filtering: `include_domains=["incois.gov.in", "moes.gov.in", "imd.gov.in", "oceandecade.org"]`.
- [ ] Build `FallbackEngine`:
  - Rich offline dictionary of maritime principles mapped to scenario IDs and outcomes.
  - Guarantees 100% uptime even if Groq or Tavily APIs encounter timeouts or network limits.

### Phase 4: Frontend Integration
- [ ] Design System (`style.css`):
  - Deep ocean palette: Abyss Navy (`#06101E`), Bioluminescent Cyan (`#00F2FE`), Emerald Safety (`#10B981`), Warning Coral (`#F59E0B`), Danger Crimson (`#EF4444`).
  - Glassmorphic panels, modern typography (Outfit / Inter).
  - Fully responsive on desktop and Android mobile viewports.
- [ ] **Learn Mode (`learn.html`)**:
  - Refactored timed quiz driven by FastAPI `/api/learn`.
  - Dynamic hint reveal, instant answer checking, score tallying, results report.
- [ ] **Play Mode (`play.html`)**:
  - Role selection stage: Fisherman, Ship Captain, Tourism Operator.
  - Ocean Telemetry Dashboard: Animated wave height gauges, wind direction compass, INCOIS advisory status banner.
  - Decision options cards with risk/reward indicators.
  - Post-decision reveal: Deterministic score banner + Groq educational explanation + "Learn More" INCOIS references drawer.
- [ ] **Leaderboard (`leaderboard.html`)**:
  - Global rankings, role filters (Fisherman Champions, Captain Navigators), daily/weekly toggles.

### Phase 5: Gamification & Learning Analytics
- [x] Backend progression engine: XP accumulation, Rank badges (e.g., *Novice Seafarer*, *Coastal Guardian*, *Master Oceanographer*), login streaks.
- [x] Analytics aggregator (`/api/analytics/profile`):
  - Aggregates `DecisionLogs` into 4 literacy pillars:
    1. *Ocean Conditions Interpretation* (wave/wind dynamics)
    2. *Safety Awareness & Disaster Response* (rough sea/tsunami protocols)
    3. *Sustainable Resource Management* (PFZ utilization without overharvesting)
    4. *Regulatory & Advisory Compliance* (INCOIS alert obedience)
- [x] Profile Page (`profile.html`):
  - Visual mastery radar / progress bars, unlocked badges, recent voyage log.

### Phase 6: Admin Dashboard
- [x] Lightweight authenticated admin portal (`/admin`):
  - Visual Scenario Editor: Add/modify ocean conditions, role options, and correct outcomes without code modifications.
  - Analytics summary: Total decisions made, dangerous choice frequency, common misconceptions.

### Phase 7: Polish & Documentation
- [x] Multilingual toggle (English / Hindi).
- [x] Accessibility: High-contrast mode, legible font toggles, keyboard navigation.
- [x] SIH Documentation:
  - Architecture diagrams (Mermaid).
  - Clear guide explaining how to swap the Ocean Data Adapter for live INCOIS APIs.
  - Comprehensive video demo script for judges.

---

## 5. Detailed Technical Specifications & Schemas

### 5.1 Scenario Data Schema (INCOIS-Compatible)

```json
{
  "scenario_id": "FISH-ARAB-001",
  "role": "fisherman",
  "title": "High Wave Alert in Potential Fishing Zone (PFZ)",
  "location": "Off the coast of Veraval, Arabian Sea",
  "ocean_data": {
    "wave_height_m": 3.8,
    "wind_speed_knots": 34,
    "swell_period_sec": 14.5,
    "sea_surface_temp_c": 28.2,
    "pfz_available": true,
    "incois_bulletin": {
      "type": "HIGH_WAVE_ALERT",
      "severity": "ORANGE",
      "issued_by": "INCOIS-OSF",
      "valid_hours": 24
    }
  },
  "narrative": "A rich Potential Fishing Zone (PFZ) has been identified 18 nautical miles offshore. However, INCOIS has issued an Orange High Wave Alert warning of sea surges up to 3.8m with high swell periods.",
  "options": [
    {
      "id": "opt_venture_pfz",
      "text": "Proceed immediately to the PFZ to maximize catch before competitors arrive.",
      "action_type": "aggressive_harvest"
    },
    {
      "id": "opt_wait_inshore",
      "text": "Remain inshore within safe harbor limits and monitor subsequent INCOIS bulletin updates.",
      "action_type": "precautionary_shelter"
    },
    {
      "id": "opt_deploy_nets_shallow",
      "text": "Head out halfway into open waters and cast nets quickly before winds peak.",
      "action_type": "compromise_risk"
    }
  ],
  "engine_evaluation_rules": {
    "recommended_action_id": "opt_wait_inshore",
    "hazard_thresholds": {
      "max_safe_wave_m": 2.5,
      "max_safe_wind_knots": 25
    },
    "consequences": {
      "opt_wait_inshore": {
        "is_safe": true,
        "score_delta": 100,
        "vessel_status": "Intact",
        "xp_awarded": 120,
        "feedback_rule": "Obeying INCOIS Orange High Wave Alert protected vessel and crew from dangerous 3.8m swell waves."
      },
      "opt_venture_pfz": {
        "is_safe": false,
        "score_delta": -120,
        "vessel_status": "Severe Capsize Risk",
        "xp_awarded": 10,
        "feedback_rule": "Severe maritime violation: Small fishing craft venturing into >3.5m waves during an active Orange Alert risks capsizing."
      },
      "opt_deploy_nets_shallow": {
        "is_safe": false,
        "score_delta": -60,
        "vessel_status": "Torn Nets / Engine Strain",
        "xp_awarded": 25,
        "feedback_rule": "High swell periods (>14s) cause sudden shoaling waves near intermediate depths, destroying gear."
      }
    }
  }
}
```

### 5.2 Deterministic Safety Matrix

| Role | Environmental Conditions | Safe Threshold | High Risk Action | Safe Action |
| :--- | :--- | :--- | :--- | :--- |
| **Fisherman** | Waves > 2.5m OR Winds > 25 knots | Waves $\le$ 2.0m, Winds $\le$ 20 kts | Venturing into PFZ despite High Wave Alert | Deferring departure, remaining in safe harbor |
| **Fisherman** | Active PFZ with Waves < 1.8m & calm seas | Clean SST thermal front, safe seas | Ignoring PFZ advisory and fishing in barren waters | Navigating to PFZ coordinates to optimize catch & fuel |
| **Ship Captain** | Swell > 4.0m OR Cyclone Alert Level Red | Divert around storm boundary | Maintaining direct course into cyclone track | Initiating heavy-weather diversion protocol |
| **Tourism Operator**| Spring High Tide + Rip Current Advisory | Waves $\le$ 1.2m, No rip currents | Operating passenger snorkel tours near rocky headlands | Cancelling water sports, moving tourists to protected lagoons |

---

## 6. Execution Plan & Next Steps

We are ready to proceed step-by-step through the phases:
1. **Phase 0 (Complete with this Plan)**: Approved canonical UI recommendation and architecture.
2. **Phase 1 (Next)**: Scaffold FastAPI backend, SQLite/SQLAlchemy schema, JWT auth, and seed the question bank.
3. **Phase 2**: Deterministic Game Engine & Ocean Data Adapter + Unit Tests.
4. **Phase 3**: Groq Llama-3.3-70b-versatile explainer & Tavily search + Graceful Fallbacks.
5. **Phase 4**: Modern Learn Mode & Play Mode frontend development.
6. **Phase 5**: Gamification & Learner Mastery Radar.
7. **Phase 6**: Admin Dashboard.
8. **Phase 7**: Polish, Localization (Hindi/English), and Final Readme.
