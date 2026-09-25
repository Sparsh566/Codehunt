import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.config import settings
from backend.app.db.init_db import init_db
from backend.app.api import auth, learn, scenarios, decisions, leaderboard, analytics, admin

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables & seed on startup
    init_db()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Interactive, role-based ocean decision-training platform for SIH 1660 (Ministry of Earth Sciences / INCOIS)",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware for local development & browser clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router)
app.include_router(learn.router)
app.include_router(scenarios.router)
app.include_router(decisions.router)
app.include_router(leaderboard.router)
app.include_router(analytics.router)
app.include_router(admin.router)

from pathlib import Path
from fastapi.responses import RedirectResponse

# Mount Frontend directory if exists
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/app", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")

@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "healthy",
        "service": "Codehunt v2 Backend",
        "env": settings.ENV,
        "ocean_data_provider": settings.OCEAN_DATA_PROVIDER,
        "groq_configured": bool(settings.GROQ_API_KEY),
        "tavily_configured": bool(settings.TAVILY_API_KEY)
    }

@app.get("/", tags=["Root"])
def root():
    return RedirectResponse(url="/app/index.html")

@app.get("/admin", tags=["Root"])
def admin_redirect():
    return RedirectResponse(url="/app/admin.html")
