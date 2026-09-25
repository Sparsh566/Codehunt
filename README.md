# 🌊 Codehunt v2 — Interactive Ocean Literacy & Maritime Decision-Training Platform

[![Smart India Hackathon 2024 / 2026](https://img.shields.io/badge/SIH-Problem%201660-blue.svg)](https://incois.gov.in)
[![Ministry of Earth Sciences](https://img.shields.io/badge/MoES-INCOIS-teal.svg)](https://moes.gov.in)
[![FastAPI Backend](https://img.shields.io/badge/Backend-FastAPI-green.svg)](https://fastapi.tiangolo.com)
[![Game Engine](https://img.shields.io/badge/Game%20Engine-100%25%20Deterministic-emerald.svg)]()
[![AI Tutor](https://img.shields.io/badge/AI%20Layer-Groq%20Llama--3.3--70b-orange.svg)]()
[![Authoritative Search](https://img.shields.io/badge/Research-Tavily%20INCOIS%20Filtered-purple.svg)]()

> **SIH Problem Statement 1660:** Interactive gamified approach to Ocean Literacy  
> **Host Organization:** Ministry of Earth Sciences (MoES) / Indian National Centre for Ocean Information Services (INCOIS)  
> **Collaborative Alignment:** UN Decade of Ocean Science for Sustainable Development (Challenge 10: *Change Humanity’s Relationship with the Ocean*)

---

## 🌟 Executive Overview

**Codehunt v2** evolves static quiz prototypes into a full-scale, role-based maritime decision-training ecosystem. Rather than merely memorizing facts, players interpret **live and simulated INCOIS ocean telemetry** (significant wave heights $H_s$, sustained wind velocities, swell wave periods, sea surface temperature [SST], and Potential Fishing Zones [PFZ]) and make life-and-livelihood decisions under dynamic marine conditions.

### Core Non-Negotiable Architectural Principles
1. **Deterministic Safety Decisions (Zero AI Judgement):**  
   All gameplay verdicts, vessel damage states, score deltas, and resource impacts are evaluated by **pure, deterministic Python rule functions**. An LLM is **never** used to decide whether an action was safe or lawful.
2. **AI Layer as Post-Decision Educational Tutor:**  
   **Groq (`llama-3.3-70b-versatile`)** is called strictly **after** the deterministic verdict to provide empathetic, bilingual (**English & Hindi**) explanations of *why* the physical ocean dynamics produced that outcome.
3. **Authoritative Research Retrieval:**  
   **Tavily Search** powers the "Learn More" drawer, hard-restricted to official domains (`incois.gov.in`, `moes.gov.in`, `imd.gov.in`, `oceandecade.org`).
4. **Resilience & 100% Offline Uptime:**  
   Circuit breakers guarantee that if external APIs or internet connections drop, gameplay, grading, and explanations fall back seamlessly to offline deterministic templates.

---

## 🎮 Dual Game Modes

### 1. 📖 Learn Mode
- **Curriculum-Driven Quiz**: 10 comprehensive ocean science questions (Thermohaline Conveyor Belt, Ocean Acidification, Coral Reef Biodiversity, Phytoplankton Oxygen Production, Mariana Trench, Bioluminescence).
- **Gamified Pressure**: 15-second countdown timer, dynamic on-demand hint toggles, instant grading, and automated XP rank progression.
- **REST Endpoints**: Backed by `/api/learn/questions` and `/api/learn/submit`.

### 2. ⚓ Play Mode (Ocean Command Simulator)
- **3 Interactive Sea-Going Roles**:
  - 🎣 **Fisherman**: Navigating coastal waters, interpreting Potential Fishing Zones (PFZ) and avoiding High Wave Alerts.
  - 🚢 **Ship Captain**: Commanding commercial cargo vessels, navigating tidal channels and executing cyclonic storm track diversions.
  - 🏴‍☠️ **Pirate King**: High-seas adventures evading naval patrols through deepwater rip current channels and navigating shallow coral atoll labyrinths.
- **Ocean Command Dashboard**:
  - Real-time animated sea surface simulator calibrated to swell frequency.
  - INCOIS Alert Banners (Green, Yellow, Orange, Red) with pulsing indicators.
  - Telemetry strip: Significant wave height, wind speed, swell period, SST gradient, and PFZ coordinates.
  - Groq AI explanation drawer with English / Hindi toggles.
  - Tavily authoritative reference drawer linking to official INCOIS bulletins.

---

## 🏛️ Project Architecture

```
Codehunt/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application, static mounting, CORS
│   │   ├── config.py                # Pydantic Settings, JWT secrets, API keys
│   │   ├── api/                     # REST API Routers
│   │   │   ├── auth.py              # JWT Register, Login, Me endpoints
│   │   │   ├── learn.py             # Learn Mode quiz endpoints
│   │   │   ├── scenarios.py         # Scenario listing & coastal station telemetry
│   │   │   ├── decisions.py         # Deterministic evaluation, Groq AI & Tavily
│   │   │   └── leaderboard.py       # Live DB rankings by role
│   │   ├── game_engine/             # DETERMINISTIC ENGINE (Pure Python, 0% AI)
│   │   │   ├── evaluator.py         # Pure evaluation function (idempotent)
│   │   │   ├── rules.py             # WMO Sea State, Beaufort Scale, role thresholds
│   │   │   └── schemas.py           # Pydantic schemas for scenarios & verdicts
│   │   ├── ocean_adapter/           # Simulated / Live INCOIS Data Service
│   │   │   ├── base.py              # Abstract OceanDataProvider interface
│   │   │   ├── simulated_provider.py# Coastal stations (Veraval, Paradip, Kovalam, etc.)
│   │   │   └── models.py            # OceanStateForecast, HighWaveAlert, PFZAdvisory
│   │   ├── ai_service/              # AI EXPLANATIONS & RETRIEVAL
│   │   │   ├── groq_explainer.py    # Llama-3.3-70b explainer (English + Hindi)
│   │   │   ├── tavily_retriever.py  # Authoritative search (incois.gov.in filtered)
│   │   │   └── fallback_engine.py   # Offline deterministic explanatory fallback
│   │   ├── models/                  # SQLAlchemy ORM Models
│   │   │   ├── user.py              # User credentials, role, XP, level
│   │   │   ├── scenario.py          # ScenarioRecord & ocean telemetry
│   │   │   ├── decision.py          # DecisionLog audit trail
│   │   │   ├── leaderboard.py       # LeaderboardEntry rankings
│   │   │   ├── learner_profile.py   # 4-Pillar Ocean Literacy mastery
│   │   │   └── question.py          # LearnMode question bank
│   │   └── db/
│   │       ├── session.py           # DB session factory (SQLite / PostgreSQL drop-in)
│   │       └── init_db.py           # Automatic table creation & seeding
│   ├── fixtures/
│   │   └── scenarios.json           # 6 realistic maritime scenario fixtures
│   └── tests/                       # 21 unit & integration tests
│
├── frontend/                        # Responsive Client UI (Desktop & Mobile)
│   ├── index.html                   # Mode Selection Hub & Live Buoy Preview
│   ├── login.html                   # JWT Login & Registration
│   ├── learn.html                   # Timed Ocean Literacy Quiz
│   ├── play.html                    # Ocean Command Simulator (Fisherman, Captain, Pirate King)
│   ├── leaderboard.html            # Real-time Honor Roll with Podium
│   ├── css/
│   │   └── style.css                # Deep ocean glassmorphic design system
│   └── js/
│       └── api.js                   # Unified REST API client with JWT handling
│
├── implementation.md                # Comprehensive Architecture Specification
└── README.md
```

---

## ⚡ Quick Start & Installation

### 1. Prerequisites
- Python 3.10+ (tested on Python 3.10 to 3.14)
- Git

### 2. Environment Setup
Clone the repository and create a virtual environment:
```bash
git clone https://github.com/Sparsh566/Codehunt.git
cd Codehunt

python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r backend/requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `backend/.env`:
```bash
cp backend/.env.example backend/.env
```
Fill in your API keys in `backend/.env`:
```ini
PROJECT_NAME="Codehunt v2 - Ocean Literacy Decision Platform"
DATABASE_URL="sqlite:///./codehunt.db"
SECRET_KEY="ocean-literacy-secret-incois-sih-2026-key-super-secure"

GROQ_API_KEY="your_groq_api_key_here"
GROQ_MODEL="llama-3.3-70b-versatile"
TAVILY_API_KEY="your_tavily_api_key_here"

OCEAN_DATA_PROVIDER="simulated"
```

### 4. Run the Application
Start the unified FastAPI server:
```bash
uvicorn backend.app.main:app --reload --port 8000
```
Open your browser:
- **Interactive Web App**: [http://127.0.0.1:8000/app/index.html](http://127.0.0.1:8000/app/index.html)
- **Interactive Swagger API Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **API Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)

---

## 🧪 Running the Test Suite

The platform includes 21 comprehensive unit and integration tests covering:
- PBKDF2 JWT Authentication & Session Lifecycle
- WMO Sea State & Beaufort Scale Classifications
- Deterministic Evaluation Idempotency across 6 Scenarios
- Ocean Data Adapter Telemetry Verification
- Groq AI Explanations in English & Hindi
- Tavily Authoritative Domain Whitelisting
- Offline Fallback Circuit Breakers

Execute tests with:
```bash
pytest backend/tests -v
```

---

## 🔄 Swapping to Live INCOIS Open Data

The `Ocean Data Adapter` pattern abstracts telemetry retrieval:
```python
from backend.app.ocean_adapter.base import OceanDataProvider

class LiveINCOISProvider(OceanDataProvider):
    def get_latest_telemetry(self, station_id: str):
        # 1. Fetch real-time OGC/REST XML/JSON feed from https://incois.gov.in/portal/osf
        # 2. Parse wave buoy observations and ERDDAP datasets
        # 3. Return INCOISTelemetrySnapshot
        pass
```
To activate live INCOIS data post-hackathon, simply set:
```ini
OCEAN_DATA_PROVIDER="live_incois"
```
**No game engine or frontend code changes are required.**

---

## 🏆 SIH Evaluation Highlights

- **Pedagogical Impact**: Teaches citizens and coastal workers how to act upon real INCOIS warnings (High Wave Alerts, Swell Surges, PFZ advisories).
- **Zero AI Hallucination in Maritime Safety**: Deterministic pure-function evaluation guarantees life-critical maritime rules are never left to stochastic LLM judgements.
- **Inclusive & Accessible**: Multilingual explanations in Hindi and English.
- **Enterprise-Grade**: JWT authentication, database-persisted leaderboards, and clean modular decoupling.

---
*Developed for Smart India Hackathon (SIH 1660) in collaboration with the Ministry of Earth Sciences and INCOIS.*
