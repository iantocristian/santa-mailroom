"""
Simple PostgreSQL-based task queue.
Uses a jobs table that workers poll for pending tasks.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base
import enum


class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(Base):
    """Background job for async processing."""
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String(100), nullable=False, index=True)  # e.g., "process_letter", "send_reply"
    payload = Column(JSON, nullable=True)  # Task-specific data
    status = Column(String(20), default=JobStatus.PENDING.value, index=True)
    priority = Column(Integer, default=0)  # Higher = more urgent
    
    # Tracking
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    scheduled_for = Column(DateTime(timezone=True), server_default=func.now())  # For delayed jobs
