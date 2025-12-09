"""
Celery tasks for email processing pipeline.
"""
import logging
from datetime import datetime
from typing import Optional

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import (
    Child, Letter, WishItem, SantaReply, ModerationFlag, GoodDeed,
    LetterStatus
)
from app.services.email_service import get_email_service, EmailService
from app.services.gpt_service import get_gpt_service, GPTService
from app.services.notification_service import get_notification_service

logger = logging.getLogger(__name__)


def get_db():
    """Get a database session for tasks."""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


@celery_app.task(bind=True, max_retries=3)
def fetch_emails_task(self):
    """
    Periodic task to fetch new emails from the inbox.
    Matches sender emails to registered children and queues processing.
    """
    logger.info("Starting email fetch task")
    
    db = get_db()
    email_service = get_email_service()
    
    try:
        # Fetch emails
        emails = email_service.fetch_new_emails(delete_after_fetch=False)
        logger.info(f"Fetched {len(emails)} emails")
        
        for email_msg in emails:
            # Check if already processed (by message_id)
            existing = db.query(Letter).filter(
                Letter.message_id == email_msg.message_id
            ).first()
            
            if existing:
                logger.debug(f"Skipping already processed email: {email_msg.message_id}")
                continue
            
            # Hash the sender email and look up the child
            sender_hash = EmailService.hash_email(email_msg.from_email)
            child = db.query(Child).filter(Child.email_hash == sender_hash).first()
            
            if not child:
                logger.info(f"Email from unregistered address: {email_msg.from_email[:20]}...")
                # TODO: Could add to moderation queue for unknown senders
                continue
            
            # Determine the Christmas year
            now = datetime.utcnow()
            # If it's after October, it's for this year's Christmas
            # Otherwise, it might be a late letter for last year's
            year = now.year if now.month >= 10 else now.year
            
            # Create the letter record
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
            
            logger.info(f"Created letter {letter.id} from child {child.name}")
            
            # Notify parent
            notification_service = get_notification_service(db)
            notification_service.notify_new_letter(letter, child)
            
            # Queue processing task
            process_letter_task.delay(letter.id)
        
        db.close()
        return {"processed": len(emails)}
        
    except Exception as e:
        db.close()
        logger.error(f"Error in fetch_emails_task: {e}")
        raise self.retry(exc=e, countdown=60)


@celery_app.task(bind=True, max_retries=3)
def process_letter_task(self, letter_id: int):
    """
    Process a single letter:
    1. Extract wish items
    2. Run content moderation
    3. Search for products
    4. Generate Santa's reply
    """
    logger.info(f"Processing letter {letter_id}")
    
    db = get_db()
    gpt_service = get_gpt_service()
    
    try:
        # Get the letter and child
        letter = db.query(Letter).filter(Letter.id == letter_id).first()
        if not letter:
            logger.error(f"Letter {letter_id} not found")
            db.close()
            return
        
        child = db.query(Child).filter(Child.id == letter.child_id).first()
        if not child:
            logger.error(f"Child {letter.child_id} not found")
            db.close()
            return
        
        family = child.family
        
        # Update status
        letter.status = LetterStatus.PROCESSING.value
        db.commit()
        
        # 1. Extract wish items
        logger.info(f"Extracting wish items from letter {letter_id}")
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
        
        # 2. Run content moderation
        logger.info(f"Running content moderation on letter {letter_id}")
        strictness = family.moderation_strictness if family else "medium"
        moderation_result = gpt_service.classify_content(
            letter.body_text,
            child.name,
            strictness=strictness
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
            
            # Notify parent about the flag
            notification_service.notify_moderation_flag(
                letter,
                child,
                flag.flag_type,
                flag.severity
            )
        
        # 3. Search for products (for each extracted item)
        logger.info(f"Searching for products from letter {letter_id}")
        wish_items = db.query(WishItem).filter(WishItem.letter_id == letter.id).all()
        
        for wish_item in wish_items:
            if wish_item.normalized_name:
                country = child.country or "US"
                product = gpt_service.search_product(wish_item.normalized_name, country)
                
                if product:
                    wish_item.estimated_price = product.estimated_price
                    wish_item.currency = product.currency
                    wish_item.product_url = product.product_url
                    wish_item.product_image_url = product.image_url
                    wish_item.product_description = product.description
                    db.commit()
        
        # 4. Get context for reply generation
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
        
        # Calculate child's age
        child_age = None
        if child.birth_year:
            child_age = datetime.utcnow().year - child.birth_year
        
        # 5. Generate Santa's reply
        logger.info(f"Generating Santa reply for letter {letter_id}")
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
        
        # Create the reply record
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
        
        logger.info(f"Letter {letter_id} processed successfully")
        
        # Queue sending the reply
        send_reply_task.delay(santa_reply.id)
        
        db.close()
        return {"status": "processed", "letter_id": letter_id}
        
    except Exception as e:
        if letter:
            letter.status = LetterStatus.FAILED.value
            letter.error_message = str(e)
            db.commit()
        db.close()
        logger.error(f"Error processing letter {letter_id}: {e}")
        raise self.retry(exc=e, countdown=300)  # Retry after 5 minutes


@celery_app.task(bind=True, max_retries=3)
def send_reply_task(self, reply_id: int):
    """
    Send a Santa reply email.
    """
    logger.info(f"Sending reply {reply_id}")
    
    db = get_db()
    email_service = get_email_service()
    
    try:
        # Get the reply and related data
        reply = db.query(SantaReply).filter(SantaReply.id == reply_id).first()
        if not reply:
            logger.error(f"Reply {reply_id} not found")
            db.close()
            return
        
        letter = db.query(Letter).filter(Letter.id == reply.letter_id).first()
        child = db.query(Child).filter(Child.id == letter.child_id).first()
        
        if not letter or not child or not letter.from_email:
            logger.error(f"Missing data for reply {reply_id}")
            db.close()
            return
        
        # TODO: Generate HTML from template
        # For now, use plain text
        
        # Send the email
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
        else:
            reply.delivery_status = "failed"
            reply.delivery_error = "Failed to send email"
        
        db.commit()
        db.close()
        
        return {"status": reply.delivery_status, "reply_id": reply_id}
        
    except Exception as e:
        if reply:
            reply.delivery_status = "failed"
            reply.delivery_error = str(e)
            db.commit()
        db.close()
        logger.error(f"Error sending reply {reply_id}: {e}")
        raise self.retry(exc=e, countdown=300)
