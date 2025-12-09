"""
Notification service for creating and sending parent alerts.
"""
import logging
from typing import Optional
from sqlalchemy.orm import Session

from app.models import Notification, Family, Child, Letter

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for creating parent notifications."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_notification(
        self,
        family_id: int,
        notification_type: str,
        title: str,
        message: Optional[str] = None,
        related_letter_id: Optional[int] = None,
        related_child_id: Optional[int] = None
    ) -> Notification:
        """
        Create a new notification for a family.
        
        Args:
            family_id: The family to notify
            notification_type: Type of notification (new_letter, budget_alert, moderation_flag, deed_completed)
            title: Short title for the notification
            message: Optional longer message
            related_letter_id: Optional ID of related letter
            related_child_id: Optional ID of related child
            
        Returns:
            The created Notification
        """
        notification = Notification(
            family_id=family_id,
            type=notification_type,
            title=title,
            message=message,
            related_letter_id=related_letter_id,
            related_child_id=related_child_id
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        logger.info(f"Created notification: {notification_type} for family {family_id}")
        return notification
    
    def notify_new_letter(self, letter: Letter, child: Child) -> Notification:
        """Notify parent about a new letter from their child."""
        return self.create_notification(
            family_id=child.family_id,
            notification_type="new_letter",
            title=f"New letter from {child.name}!",
            message=f"{child.name} sent a new letter to Santa. Check it out in the dashboard!",
            related_letter_id=letter.id,
            related_child_id=child.id
        )
    
    def notify_budget_alert(
        self,
        family: Family,
        total_cost: float,
        threshold: float,
        child: Optional[Child] = None
    ) -> Notification:
        """Notify parent when budget threshold is exceeded."""
        child_context = f" for {child.name}" if child else ""
        return self.create_notification(
            family_id=family.id,
            notification_type="budget_alert",
            title=f"Budget Alert{child_context}",
            message=f"The estimated wishlist cost (${total_cost:.2f}) exceeds your budget alert threshold (${threshold:.2f}).",
            related_child_id=child.id if child else None
        )
    
    def notify_moderation_flag(
        self,
        letter: Letter,
        child: Child,
        flag_type: str,
        severity: str
    ) -> Notification:
        """Notify parent about concerning content in a letter."""
        severity_emoji = {"low": "⚠️", "medium": "🔶", "high": "🚨"}.get(severity, "⚠️")
        return self.create_notification(
            family_id=child.family_id,
            notification_type="moderation_flag",
            title=f"{severity_emoji} Content flag in {child.name}'s letter",
            message=f"A letter from {child.name} has been flagged for review ({flag_type}). Please check the moderation dashboard.",
            related_letter_id=letter.id,
            related_child_id=child.id
        )
    
    def notify_deed_completed(self, child: Child, deed_description: str) -> Notification:
        """Notify parent (confirmation) when a deed is marked complete."""
        return self.create_notification(
            family_id=child.family_id,
            notification_type="deed_completed",
            title=f"Good deed completed by {child.name}! ⭐",
            message=f"{child.name} completed: {deed_description}",
            related_child_id=child.id
        )


def get_notification_service(db: Session) -> NotificationService:
    """Get a notification service instance."""
    return NotificationService(db)
