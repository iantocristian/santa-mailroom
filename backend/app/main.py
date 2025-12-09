import logging
import sys

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db

# Import all models to ensure they're registered with Base
from app import models  # noqa: F401
from app import job_queue  # noqa: F401 - Import to create jobs table

# Import routers
from app.routers import auth, family, children, wishlist, letters, deeds, moderation, notifications

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

