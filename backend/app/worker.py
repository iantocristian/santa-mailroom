"""
Background worker that polls PostgreSQL for pending jobs and processes them.
Run with: python -m app.worker
"""
import logging
import time
import signal
import sys
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import SessionLocal
from app.job_queue import Job, JobStatus
from app.models import (
    Child, Letter, WishItem, SantaReply, ModerationFlag, GoodDeed,
    LetterStatus, SentEmail
)
from app.services.email_service import get_email_service, EmailService
from app.services.gpt_service import get_gpt_service
from app.services.product_search_service import get_product_search_service
from app.services.notification_service import get_notification_service
from app.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)
settings = get_settings()

# Graceful shutdown
shutdown_requested = False


def signal_handler(signum, frame):
    global shutdown_requested
    logger.info("Shutdown requested, finishing current job...")
    shutdown_requested = True


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


def get_db() -> Session:
    """Get a database session."""
    return SessionLocal()


def claim_next_job(db: Session) -> Optional[Job]:
    """
    Atomically claim the next pending job.
    Uses SELECT FOR UPDATE SKIP LOCKED to allow multiple workers.
    """
    job = db.query(Job).filter(
        and_(
            Job.status == JobStatus.PENDING.value,
            Job.scheduled_for <= datetime.utcnow(),
            Job.attempts < Job.max_attempts
        )
    ).order_by(
        Job.priority.desc(),
        Job.created_at.asc()
    ).with_for_update(skip_locked=True).first()
    
    if job:
        job.status = JobStatus.PROCESSING.value
        job.started_at = datetime.utcnow()
        job.attempts += 1
        db.commit()
        db.refresh(job)
    
    return job


def complete_job(db: Session, job: Job, success: bool, error: Optional[str] = None):
    """Mark a job as completed or failed."""
    if success:
        job.status = JobStatus.COMPLETED.value
    else:
        if job.attempts >= job.max_attempts:
            job.status = JobStatus.FAILED.value
        else:
            job.status = JobStatus.PENDING.value  # Will be retried
        job.error_message = error
    
    job.completed_at = datetime.utcnow()
    db.commit()


def enqueue_job(db: Session, task_type: str, payload: dict = None, priority: int = 0) -> Job:
    """Add a new job to the queue."""
    job = Job(
        task_type=task_type,
        payload=payload or {},
        priority=priority
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    logger.info(f"Enqueued job {job.id}: {task_type}")
    return job


# ============== Task Handlers ==============

def handle_fetch_emails(db: Session, payload: dict):
    """Fetch new emails from inbox and create letters."""
    logger.info("Fetching emails...")
    email_service = get_email_service()
    
    emails = email_service.fetch_new_emails(delete_after_fetch=False)
    logger.info(f"Fetched {len(emails)} emails")
    
    for email_msg in emails:
        # Check if already processed
        existing = db.query(Letter).filter(
            Letter.message_id == email_msg.message_id
        ).first()
        
        if existing:
            logger.debug(f"Skipping already processed email: {email_msg.message_id}")
            continue
        
        # Look up child by email hash
        sender_email = email_msg.from_email.lower().strip()
        sender_hash = EmailService.hash_email(sender_email)
        logger.info(f"Processing email from: {sender_email}")
        logger.info(f"Computed hash: {sender_hash}")
        
        # Log all registered email hashes for debugging
        all_children = db.query(Child).all()
        for c in all_children:
            logger.debug(f"Registered child '{c.name}' hash: {c.email_hash}")
        
        child = db.query(Child).filter(Child.email_hash == sender_hash).first()
        
        if not child:
            logger.warning(f"Email from unregistered address: {sender_email} (hash: {sender_hash})")
            logger.warning(f"Registered hashes: {[c.email_hash for c in all_children]}")
            continue
        
        # Determine Christmas year
        now = datetime.utcnow()
        year = now.year if now.month >= 10 else now.year
        
        # Create letter
        letter = Letter(
            child_id=child.id,
            year=year,
            subject=email_msg.subject,
            body_text=email_msg.body_text,
            body_html=email_msg.body_html,
            received_at=email_msg.received_at,
            message_id=email_msg.message_id,
            from_email=email_msg.from_email,
            status=LetterStatus.PENDING.value
        )
        db.add(letter)
        db.commit()
        db.refresh(letter)
        
        logger.info(f"Created letter {letter.id} from {child.name}")
        
        # Notify parent
        notification_service = get_notification_service(db)
        notification_service.notify_new_letter(letter, child)
        
        # Queue processing
        enqueue_job(db, "process_letter", {"letter_id": letter.id})


def handle_process_letter(db: Session, payload: dict):
    """Process a letter: extract items, moderate, generate reply."""
    letter_id = payload.get("letter_id")
    if not letter_id:
        raise ValueError("Missing letter_id in payload")
    
    logger.info(f"Processing letter {letter_id}")
    gpt_service = get_gpt_service()
    
    letter = db.query(Letter).filter(Letter.id == letter_id).first()
    if not letter:
        raise ValueError(f"Letter {letter_id} not found")
    
    child = db.query(Child).filter(Child.id == letter.child_id).first()
    if not child:
        raise ValueError(f"Child {letter.child_id} not found")
    
    family = child.family
    
    # Update status
    letter.status = LetterStatus.PROCESSING.value
    db.commit()
    
    # 1. Extract wish items
    logger.info(f"Extracting wish items...")
    extracted_items = gpt_service.extract_wish_items(letter.body_text, child.name)
    
    for item in extracted_items:
        wish_item = WishItem(
            letter_id=letter.id,
            raw_text=item.raw_text,
            normalized_name=item.normalized_name,
            category=item.category,
            status="pending"
        )
        db.add(wish_item)
    db.commit()
    logger.info(f"Extracted {len(extracted_items)} wish items")
    
    # 2. Content moderation
    logger.info(f"Running content moderation...")
    strictness = family.moderation_strictness if family else "medium"
    moderation_result = gpt_service.classify_content(
        letter.body_text, child.name, strictness=strictness
    )
    
    notification_service = get_notification_service(db)
    
    for flag_data in moderation_result.flags:
        flag = ModerationFlag(
            letter_id=letter.id,
            flag_type=flag_data.get("type", "unknown"),
            severity=flag_data.get("severity", "medium"),
            excerpt=flag_data.get("excerpt"),
            ai_confidence=flag_data.get("confidence"),
            ai_explanation=flag_data.get("explanation")
        )
        db.add(flag)
        db.commit()
        
        notification_service.notify_moderation_flag(letter, child, flag.flag_type, flag.severity)
    
    # 3. Product search for each item
    logger.info(f"Searching for products...")
    product_search = get_product_search_service()
    wish_items = db.query(WishItem).filter(WishItem.letter_id == letter.id).all()
    
    for wish_item in wish_items:
        if wish_item.normalized_name:
            country = child.country or "US"
            product = product_search.search(wish_item.normalized_name, country)
            
            if product:
                wish_item.estimated_price = product.estimated_price
                wish_item.currency = product.currency
                wish_item.product_url = product.product_url
                wish_item.product_image_url = product.image_url
                wish_item.product_description = product.description
                db.commit()
    
    # 4. Generate Santa's reply
    logger.info(f"Generating Santa reply...")
    
    pending_deeds = db.query(GoodDeed).filter(
        GoodDeed.child_id == child.id,
        GoodDeed.completed == False
    ).all()
    
    completed_deeds = db.query(GoodDeed).filter(
        GoodDeed.child_id == child.id,
        GoodDeed.completed == True,
        GoodDeed.acknowledged_in_reply_id == None
    ).all()
    
    denied_items = db.query(WishItem).filter(
        WishItem.letter_id == letter.id,
        WishItem.status == "denied"
    ).all()
    
    approved_items = db.query(WishItem).filter(
        WishItem.letter_id == letter.id,
        WishItem.status.in_(["pending", "approved"])
    ).all()
    
    child_age = None
    if child.birth_year:
        child_age = datetime.utcnow().year - child.birth_year
    
    reply_text, suggested_deed = gpt_service.generate_santa_reply(
        letter_text=letter.body_text,
        child_name=child.name,
        child_age=child_age,
        wish_items=[{"name": i.normalized_name or i.raw_text} for i in approved_items],
        denied_items=[{"name": i.normalized_name or i.raw_text, "reason": i.denial_reason} for i in denied_items],
        pending_deeds=[d.description for d in pending_deeds],
        completed_deeds=[d.description for d in completed_deeds],
        has_concerning_content=moderation_result.is_concerning
    )
    
    # Create reply
    santa_reply = SantaReply(
        letter_id=letter.id,
        body_text=reply_text,
        suggested_deed=suggested_deed,
        delivery_status="pending"
    )
    db.add(santa_reply)
    db.commit()
    db.refresh(santa_reply)
    
    # Create good deed if suggested
    if suggested_deed:
        new_deed = GoodDeed(
            child_id=child.id,
            description=suggested_deed,
            suggested_in_reply_id=santa_reply.id
        )
        db.add(new_deed)
    
    # Mark completed deeds as acknowledged
    for deed in completed_deeds:
        deed.acknowledged_in_reply_id = santa_reply.id
    
    # Update letter status
    letter.status = LetterStatus.PROCESSED.value
    letter.processed_at = datetime.utcnow()
    db.commit()
    
    logger.info(f"Letter {letter_id} processed, queueing reply")
    
    # Queue sending
    enqueue_job(db, "send_reply", {"reply_id": santa_reply.id})


def handle_send_reply(db: Session, payload: dict):
    """Send a Santa reply email."""
    reply_id = payload.get("reply_id")
    if not reply_id:
        raise ValueError("Missing reply_id in payload")
    
    logger.info(f"Sending reply {reply_id}")
    email_service = get_email_service()
    gpt_service = get_gpt_service()
    
    reply = db.query(SantaReply).filter(SantaReply.id == reply_id).first()
    if not reply:
        raise ValueError(f"Reply {reply_id} not found")
    
    letter = db.query(Letter).filter(Letter.id == reply.letter_id).first()
    child = db.query(Child).filter(Child.id == letter.child_id).first()
    
    if not letter or not child or not letter.from_email:
        raise ValueError(f"Missing data for reply {reply_id}")
    
    # Safety check before sending (if enabled)
    if settings.email_safety_check_enabled:
        is_safe, safety_reason = gpt_service.check_email_safety(
            email_content=reply.body_text,
            child_name=child.name,
            email_type="letter_reply"
        )
        
        if not is_safe:
            logger.error(f"SAFETY CHECK FAILED for reply {reply_id} to {child.name}: {safety_reason}")
            reply.delivery_status = "blocked"
            reply.delivery_error = f"Safety check failed: {safety_reason}"
            db.commit()
            return  # Do not send - blocked for safety
        
        logger.info(f"Safety check PASSED for reply {reply_id}")
    
    success = email_service.send_santa_reply(
        to_email=letter.from_email,
        to_name=child.name,
        subject=f"Re: {letter.subject or 'Your letter to Santa'}",
        body_text=reply.body_text,
        body_html=reply.body_html,
        in_reply_to=letter.message_id
    )
    
    if success:
        reply.delivery_status = "sent"
        reply.sent_at = datetime.utcnow()
        logger.info(f"Reply {reply_id} sent successfully")
        
        # Record sent email
        sent_email = SentEmail(
            child_id=child.id,
            email_type="letter_reply",
            subject=f"Re: {letter.subject or 'Your letter to Santa'}",
            body_text=reply.body_text,
            letter_id=letter.id,
            santa_reply_id=reply.id,
            delivery_status="sent"
        )
        db.add(sent_email)
    else:
        reply.delivery_status = "failed"
        reply.delivery_error = "Failed to send email"
        raise Exception("Failed to send email")
    
    db.commit()



def handle_send_deed_email(db: Session, payload: dict):
    """Send a Santa email about a new good deed."""
    deed_id = payload.get("deed_id")
    if not deed_id:
        raise ValueError("Missing deed_id in payload")
    
    logger.info(f"Sending deed notification for deed {deed_id}")
    
    deed = db.query(GoodDeed).filter(GoodDeed.id == deed_id).first()
    if not deed:
        raise ValueError(f"Deed {deed_id} not found")
    
    child = db.query(Child).filter(Child.id == deed.child_id).first()
    if not child:
        raise ValueError(f"Child {deed.child_id} not found")
    
    # Get child's last letter to find their email
    last_letter = db.query(Letter).filter(
        Letter.child_id == child.id
    ).order_by(Letter.received_at.desc()).first()
    
    if not last_letter or not last_letter.from_email:
        logger.warning(f"No email found for child {child.id}, cannot send deed notification")
        return
    
    # Generate email content
    gpt_service = get_gpt_service()
    child_age = None
    if child.birth_year:
        child_age = datetime.utcnow().year - child.birth_year
    
    email_body = gpt_service.generate_deed_email(
        child_name=child.name,
        child_age=child_age,
        deed_description=deed.description
    )
    
    # Safety check before sending (if enabled)
    if settings.email_safety_check_enabled:
        is_safe, safety_reason = gpt_service.check_email_safety(
            email_content=email_body,
            child_name=child.name,
            email_type="deed_email"
        )
        
        if not is_safe:
            logger.error(f"SAFETY CHECK FAILED for deed email {deed_id} to {child.name}: {safety_reason}")
            # Record blocked email
            sent_email = SentEmail(
                child_id=child.id,
                email_type="deed_suggestion",
                subject="A Special Message from Santa! 🎅",
                body_text=email_body,
                deed_id=deed.id,
                delivery_status="blocked"
            )
            db.add(sent_email)
            db.commit()
            return  # Do not send - blocked for safety
        
        logger.info(f"Safety check PASSED for deed email {deed_id}")
    
    # Send email
    email_service = get_email_service()
    success = email_service.send_santa_reply(
        to_email=last_letter.from_email,
        to_name=child.name,
        subject="A Special Message from Santa! 🎅",
        body_text=email_body
    )
    
    if success:
        logger.info(f"Deed notification sent to {child.name}")
        
        # Record sent email
        sent_email = SentEmail(
            child_id=child.id,
            email_type="deed_suggestion",
            subject="A Special Message from Santa! 🎅",
            body_text=email_body,
            deed_id=deed.id,
            delivery_status="sent"
        )
        db.add(sent_email)
        db.commit()
    else:
        raise Exception("Failed to send deed notification email")


def handle_send_deed_congrats(db: Session, payload: dict):
    """Send a congratulations email from Santa for completing a deed."""
    deed_id = payload.get("deed_id")
    if not deed_id:
        raise ValueError("Missing deed_id in payload")
    
    logger.info(f"Sending deed congratulations for deed {deed_id}")
    
    deed = db.query(GoodDeed).filter(GoodDeed.id == deed_id).first()
    if not deed:
        raise ValueError(f"Deed {deed_id} not found")
    
    child = db.query(Child).filter(Child.id == deed.child_id).first()
    if not child:
        raise ValueError(f"Child {deed.child_id} not found")
    
    # Get child's last letter to find their email
    last_letter = db.query(Letter).filter(
        Letter.child_id == child.id
    ).order_by(Letter.received_at.desc()).first()
    
    if not last_letter or not last_letter.from_email:
        logger.warning(f"No email found for child {child.id}, cannot send congrats")
        return
    
    # Generate congratulations email
    gpt_service = get_gpt_service()
    child_age = None
    if child.birth_year:
        child_age = datetime.utcnow().year - child.birth_year
    
    email_body = gpt_service.generate_deed_congrats_email(
        child_name=child.name,
        child_age=child_age,
        deed_description=deed.description,
        parent_note=deed.parent_note
    )
    
    # Safety check before sending (if enabled)
    if settings.email_safety_check_enabled:
        is_safe, safety_reason = gpt_service.check_email_safety(
            email_content=email_body,
            child_name=child.name,
            email_type="deed_congrats"
        )
        
        if not is_safe:
            logger.error(f"SAFETY CHECK FAILED for deed congrats {deed_id} to {child.name}: {safety_reason}")
            # Record blocked email
            sent_email = SentEmail(
                child_id=child.id,
                email_type="deed_congrats",
                subject="🎉 Santa is SO PROUD of You! 🎉",
                body_text=email_body,
                deed_id=deed.id,
                delivery_status="blocked"
            )
            db.add(sent_email)
            db.commit()
            return  # Do not send - blocked for safety
        
        logger.info(f"Safety check PASSED for deed congrats {deed_id}")
    
    # Send email
    email_service = get_email_service()
    success = email_service.send_santa_reply(
        to_email=last_letter.from_email,
        to_name=child.name,
        subject="🎉 Santa is SO PROUD of You! 🎉",
        body_text=email_body
    )
    
    if success:
        logger.info(f"Deed congratulations sent to {child.name}")
        
        # Record sent email
        sent_email = SentEmail(
            child_id=child.id,
            email_type="deed_congrats",
            subject="🎉 Santa is SO PROUD of You! 🎉",
            body_text=email_body,
            deed_id=deed.id,
            delivery_status="sent"
        )
        db.add(sent_email)
        db.commit()
    else:
        raise Exception("Failed to send deed congratulations email")


# Task handler registry
TASK_HANDLERS = {
    "fetch_emails": handle_fetch_emails,
    "process_letter": handle_process_letter,
    "send_reply": handle_send_reply,
    "send_deed_email": handle_send_deed_email,
    "send_deed_congrats": handle_send_deed_congrats,
}


def process_job(db: Session, job: Job):
    """Process a single job."""
    handler = TASK_HANDLERS.get(job.task_type)
    
    if not handler:
        logger.error(f"Unknown task type: {job.task_type}")
        complete_job(db, job, success=False, error=f"Unknown task type: {job.task_type}")
        return
    
    try:
        handler(db, job.payload or {})
        complete_job(db, job, success=True)
        logger.info(f"Job {job.id} ({job.task_type}) completed")
    except Exception as e:
        logger.error(f"Job {job.id} failed: {e}")
        complete_job(db, job, success=False, error=str(e))


def run_worker(poll_interval: int = 5):
    """Main worker loop."""
    logger.info("Starting worker...")
    
    while not shutdown_requested:
        db = get_db()
        try:
            job = claim_next_job(db)
            
            if job:
                logger.info(f"Processing job {job.id}: {job.task_type}")
                process_job(db, job)
            else:
                time.sleep(poll_interval)
        except Exception as e:
            logger.error(f"Worker error: {e}")
            time.sleep(poll_interval)
        finally:
            db.close()
    
    logger.info("Worker stopped")


def run_scheduler(fetch_interval: int = 60):
    """Scheduler that enqueues periodic tasks."""
    logger.info(f"Starting scheduler (fetch every {fetch_interval}s)...")
    
    while not shutdown_requested:
        db = get_db()
        try:
            # Check if there's already a pending fetch_emails job
            existing = db.query(Job).filter(
                Job.task_type == "fetch_emails",
                Job.status.in_([JobStatus.PENDING.value, JobStatus.PROCESSING.value])
            ).first()
            
            if not existing:
                enqueue_job(db, "fetch_emails", priority=1)
            
            db.close()
            time.sleep(fetch_interval)
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            db.close()
            time.sleep(fetch_interval)
    
    logger.info("Scheduler stopped")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Santa Wishlist Worker")
    parser.add_argument("mode", choices=["worker", "scheduler", "both"], 
                        help="Run mode: worker, scheduler, or both")
    parser.add_argument("--poll-interval", type=int, default=5,
                        help="Worker poll interval in seconds")
    parser.add_argument("--fetch-interval", type=int, default=60,
                        help="Email fetch interval in seconds")
    args = parser.parse_args()
    
    if args.mode == "worker":
        run_worker(args.poll_interval)
    elif args.mode == "scheduler":
        run_scheduler(args.fetch_interval)
    elif args.mode == "both":
        import threading
        
        scheduler_thread = threading.Thread(
            target=run_scheduler, 
            args=(args.fetch_interval,),
            daemon=True
        )
        scheduler_thread.start()
        
        run_worker(args.poll_interval)
