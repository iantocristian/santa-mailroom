import logging
import sys

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base

# Import all models to ensure they're registered with Base
from app import models  # noqa: F401

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
