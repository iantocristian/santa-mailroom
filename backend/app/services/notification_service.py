"""
Notification service for creating and sending parent alerts.
"""
import json
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
        title_key: str,
        title_params: Optional[dict] = None,
        message_key: Optional[str] = None,
        message_params: Optional[dict] = None,
        related_letter_id: Optional[int] = None,
        related_child_id: Optional[int] = None
    ) -> Notification:
        """
        Create a new notification for a family using i18n translation keys.
        
        Args:
            family_id: The family to notify
            notification_type: Type of notification (new_letter, budget_alert, moderation_flag, deed_completed)
            title_key: i18n translation key for the title
            title_params: Optional parameters to interpolate into the title
            message_key: Optional i18n translation key for the message
            message_params: Optional parameters to interpolate into the message
            related_letter_id: Optional ID of related letter
            related_child_id: Optional ID of related child
            
        Returns:
            The created Notification
        """
        notification = Notification(
            family_id=family_id,
            type=notification_type,
            title_key=title_key,
            title_params=json.dumps(title_params) if title_params else None,
            message_key=message_key,
            message_params=json.dumps(message_params) if message_params else None,
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
            title_key="notification.newLetter.title",
            title_params={"name": child.name},
            message_key="notification.newLetter.message",
            message_params={"name": child.name},
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
        params = {
            "totalCost": f"${total_cost:.2f}",
            "threshold": f"${threshold:.2f}"
        }
        if child:
            params["name"] = child.name
            
        return self.create_notification(
            family_id=family.id,
            notification_type="budget_alert",
            title_key="notification.budgetAlert.titleWithChild" if child else "notification.budgetAlert.title",
            title_params=params if child else None,
            message_key="notification.budgetAlert.message",
            message_params=params,
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
            title_key="notification.moderationFlag.title",
            title_params={"emoji": severity_emoji, "name": child.name},
            message_key="notification.moderationFlag.message",
            message_params={"name": child.name, "flagType": flag_type},
            related_letter_id=letter.id,
            related_child_id=child.id
        )
    
    def notify_deed_completed(self, child: Child, deed_description: str) -> Notification:
        """Notify parent (confirmation) when a deed is marked complete."""
        return self.create_notification(
            family_id=child.family_id,
            notification_type="deed_completed",
            title_key="notification.deedCompleted.title",
            title_params={"name": child.name},
            message_key="notification.deedCompleted.message",
            message_params={"name": child.name, "deed": deed_description},
            related_child_id=child.id
        )


def get_notification_service(db: Session) -> NotificationService:
    """Get a notification service instance."""
    return NotificationService(db)
