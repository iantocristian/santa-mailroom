import logging
import sys

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.database import engine, Base, get_db
from app.rate_limit import limiter

# Import all models to ensure they're registered with Base
from app import models  # noqa: F401
from app import job_queue  # noqa: F401 - Import to create jobs table

# Import routers
from app.routers import auth, family, children, wishlist, letters, deeds, moderation, notifications, sent_emails

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stdout,
)

# Set specific loggers
logging.getLogger("app.services").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Santa Wishlist API",
    description="Christmas wish list application where children email Santa",
    version="1.0.0"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(family.router)
app.include_router(children.router)
app.include_router(wishlist.router)
app.include_router(letters.router)
app.include_router(deeds.router)
app.include_router(moderation.router)
app.include_router(notifications.router)
app.include_router(sent_emails.router)


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "santa-wishlist"}


@app.post("/api/admin/fetch-emails")
def trigger_email_fetch(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    """Manually trigger an email fetch job (admin only)."""
    from app.worker import enqueue_job
    job = enqueue_job(db, "fetch_emails", priority=10)
    return {"message": "Email fetch job queued", "job_id": job.id}

