"""FastAPI application entry point — no business logic here."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import HealthResponse
from routes import upload, chat, plan

app = FastAPI(
    title="AI Employee Onboarding Assistant",
    description="RAG-powered backend for company document Q&A and onboarding plan generation.",
    version="1.0.0",
)

# ── CORS (allow all origins for development) ────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include routers ─────────────────────────────────────────
app.include_router(upload.router, tags=["Documents"])
app.include_router(chat.router, tags=["Chat"])
app.include_router(plan.router, tags=["Onboarding Plan"])


# ── Root ────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "message": "AI Employee Onboarding Assistant API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# ── Health check ────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check() -> HealthResponse:
    return HealthResponse(status="ok")
