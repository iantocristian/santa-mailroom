"""
GPT service for processing letters and generating Santa replies.
Uses OpenAI API for:
- Extracting wish items from letters
- Content moderation/classification
- Generating personalized Santa replies
"""
import json
import logging
from typing import List, Optional
from dataclasses import dataclass, field

from openai import OpenAI

from app.config import get_settings
from app.prompts import extraction, santa_email, deed_email, deed_congrats, safety

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ExtractedWishItem:
    """An extracted wish item from a letter."""
    raw_text: str
    normalized_name: Optional[str] = None
    category: Optional[str] = None  # toys, books, clothes, electronics, games, sports, etc.


@dataclass
class ModerationResult:
    """Result of content moderation check."""
    is_concerning: bool
    flags: List[dict] = field(default_factory=list)  # [{type, severity, excerpt, confidence, explanation}]



class GPTService:
    """GPT-powered processing for Santa's mailroom."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
        self.model = settings.gpt_model
        self.extraction_model = settings.gpt_extraction_model
        self.safety_model = settings.gpt_safety_model
    
    def _chat(self, messages: List[dict], model: Optional[str] = None, response_format: Optional[dict] = None) -> str:
        """Make a chat completion request."""
        if not self.client:
            raise ValueError("OpenAI API key not configured")
        
        kwargs = {
            "model": model or self.model,
            "messages": messages,
        }
        if response_format:
            kwargs["response_format"] = response_format
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    def extract_wish_items(self, letter_text: str, child_name: str) -> List[ExtractedWishItem]:
        """
        Extract wish list items from a letter.
        
        Args:
            letter_text: The body of the child's letter
            child_name: The child's name for context
            
        Returns:
            List of extracted wish items
        """
        system_prompt = extraction.EXTRACT_WISHES_SYSTEM
        user_prompt = extraction.get_extract_wishes_user(child_name, letter_text)

        try:
            response = self._chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.extraction_model,
                response_format={"type": "json_object"}
            )
            
            data = json.loads(response)
            items = []
            for item in data.get("items", []):
                items.append(ExtractedWishItem(
                    raw_text=item.get("raw_text", ""),
                    normalized_name=item.get("normalized_name"),
                    category=item.get("category")
                ))
            return items
            
        except Exception as e:
            logger.error(f"Error extracting wish items: {e}")
            return []
    
    def classify_content(self, letter_text: str, child_name: str, strictness: str = "medium") -> ModerationResult:
        """
        Check letter content for concerning material.
        
        Args:
            letter_text: The body of the child's letter
            child_name: The child's name
            strictness: low, medium, or high
            
        Returns:
            ModerationResult with any flags
        """
        system_prompt = extraction.get_moderation_system(strictness)
        user_prompt = extraction.get_moderation_user(child_name, letter_text)

        try:
            response = self._chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.extraction_model,
                response_format={"type": "json_object"}
            )
            
            data = json.loads(response)
            return ModerationResult(
                is_concerning=data.get("is_concerning", False),
                flags=data.get("flags", [])
            )
            
        except Exception as e:
            logger.error(f"Error classifying content: {e}")
            return ModerationResult(is_concerning=False, flags=[])
    
    def generate_santa_reply(
        self,
        letter_text: str,
        child_name: str,
        child_age: Optional[int],
        wish_items: List[dict],
        denied_items: List[dict],
        pending_deeds: List[str],
        completed_deeds: List[str],
        has_concerning_content: bool = False,
        conversation_examples: Optional[List[dict]] = None
    ) -> tuple[str, Optional[str]]:
        """
        Generate a personalized reply from Santa.
        
        Args:
            letter_text: The child's letter
            child_name: Child's first name
            child_age: Child's age (if known)
            wish_items: List of approved/pending wish items
            denied_items: List of denied items with reasons
            pending_deeds: Incomplete good deeds
            completed_deeds: Recently completed good deeds
            has_concerning_content: If True, include supportive messaging
            conversation_examples: Optional examples for tone
            
        Returns:
            Tuple of (reply_text, suggested_deed)
        """
        
        age_context = f"The child is approximately {child_age} years old." if child_age else "Age unknown."
        
        # Build context about items
        items_context = ""
        if wish_items:
            items_context += f"\n\nApproved/pending wishes: {', '.join(w.get('name', w.get('raw_text', '')) for w in wish_items)}"
        if denied_items:
            items_context += f"\n\nItems to redirect (don't mention directly, suggest alternatives): "
            for item in denied_items:
                items_context += f"\n- {item.get('name', '')}: {item.get('reason', 'not available')}"
        
        # Build deeds context
        deeds_context = ""
        if completed_deeds:
            deeds_context += f"\n\nGood deeds completed recently (acknowledge these!): {', '.join(completed_deeds)}"
        if pending_deeds:
            deeds_context += f"\n\nPending good deeds (gently encourage): {', '.join(pending_deeds)}"
        
        concerning_addon = ""
        if has_concerning_content:
            concerning_addon = """

IMPORTANT: The letter contained some concerning content. Include warm, supportive messaging.
Encourage the child to talk to their parents or a trusted adult if they're feeling sad or worried.
Keep it gentle and not alarming."""

        system_prompt = f"""You are Santa Claus, writing a warm, magical reply to a child's letter.

Guidelines:
- Be warm, jolly, and magical
- Use the child's name naturally
- Reference specific things from their letter to show you read it
- Keep appropriate for the child's age
- Include Christmas magic and wonder
- Suggest ONE simple good deed for the week (be specific and achievable)
- Keep the letter to 3-4 paragraphs

{age_context}
{items_context}
{deeds_context}
{concerning_addon}

At the end of your response, add a line break and then:
GOOD_DEED: [your suggested deed]

The good deed should be something specific and achievable like:
- "Help set the table for dinner this week"
- "Draw a picture for someone you love"
- "Give a friend a compliment"
- "Help a parent with a chore without being asked\""""

        user_prompt = f"""Child's name: {child_name}

Their letter:
{letter_text}

Write a magical reply from Santa!"""

        try:
            response = self._chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model
            )
            
            # Parse out the good deed suggestion
            reply_text = response
            suggested_deed = None
            
            if "GOOD_DEED:" in response:
                parts = response.split("GOOD_DEED:")
                reply_text = parts[0].strip()
                suggested_deed = parts[1].strip() if len(parts) > 1 else None
            
            return reply_text, suggested_deed
            
        except Exception as e:
            logger.error(f"Error generating Santa reply: {e}")
            return f"Ho ho ho, dear {child_name}! Santa received your wonderful letter and was so happy to hear from you! Keep being good and remember that the magic of Christmas is all about love and kindness. 🎅", None
    
    def generate_rich_santa_email(
        self,
        letter_text: str,
        child_name: str,
        child_age: Optional[int],
        wish_items: List[dict],
        denied_items: List[dict],
        pending_deeds: List[str],
        completed_deeds: List[str],
        has_concerning_content: bool = False,
        image_catalog: str = "",
        language: Optional[str] = None
    ) -> dict:
        """
        Generate a complete rich HTML email from Santa with dynamic image selection.
        
        Args:
            letter_text: The child's letter
            child_name: Child's first name
            child_age: Child's age (if known)
            wish_items: List of approved/pending wish items
            denied_items: List of denied items with reasons
            pending_deeds: Incomplete good deeds
            completed_deeds: Recently completed good deeds
            has_concerning_content: If True, include supportive messaging
            image_catalog: Formatted string of available images for GPT
            
        Returns:
            Dict with keys: html_body, text_body, suggested_deed, images_used
        """
        
        age_context = f"The child is approximately {child_age} years old." if child_age else "Age unknown."
        items_context = santa_email.build_items_context(wish_items, denied_items)
        deeds_context = santa_email.build_deeds_context(pending_deeds, completed_deeds)
        concerning_addon = santa_email.get_concerning_addon(has_concerning_content)
        
        system_prompt = santa_email.get_santa_email_system(
            age_context=age_context,
            items_context=items_context,
            deeds_context=deeds_context,
            concerning_addon=concerning_addon,
            image_catalog=image_catalog,
            language=language
        )
        user_prompt = santa_email.get_santa_email_user(child_name, letter_text)

        try:
            response = self._chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                response_format={"type": "json_object"}
            )
            
            data = json.loads(response)
            
            # Ensure mandatory images are included
            images = data.get("images_used", [])
            if "santa_sleigh" not in images:
                images.append("santa_sleigh")
            if "elves_bell" not in images:
                images.append("elves_bell")
            
            return {
                "html_body": data.get("html_body", ""),
                "text_body": data.get("text_body", f"🎅 Ho ho ho, dear {child_name}! Santa received your letter! 🎄"),
                "suggested_deed": data.get("suggested_deed"),
                "images_used": images
            }
            
        except Exception as e:
            logger.error(f"Error generating rich Santa email: {e}")
            # Fallback to static template
            return self._generate_fallback_email(child_name, letter_text)
    
    def _generate_fallback_email(self, child_name: str, letter_text: str) -> dict:
        """Generate a static fallback email when GPT fails."""
        
        # Plain text with emojis
        text_body = f"""🎅 Ho Ho Ho, dear {child_name}! 🎄

❄️ Your wonderful letter has arrived at the North Pole! ❄️

I was so happy to read what you wrote. My elves and I are working hard in our workshop, and the reindeer are practicing their flying for the big night! 🦌✨

Remember to be kind to others and spread joy wherever you go. That's the true magic of Christmas! ⭐

⭐ A Very Important Job For You! ⭐
Do something kind for someone today! It could be helping a family member, sharing with a friend, or giving someone a compliment. These little acts of kindness make Santa's heart so happy! 🎁

❤️ Merry Christmas, little friend! ❤️

With love from the North Pole,
🎅 Santa Claus & The Elves 🧝‍♂️🧝‍♀️"""

        # Static HTML with mandatory images and rich styling
        html_body = f"""<table border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #FFF8DC; border: 1px solid #d4af37; font-family: Georgia, 'Times New Roman', serif; color: #5a3a22;">
    <tr>
        <td align="center" style="padding: 10px 0;">
            <img src="cid:santa_sleigh" width="404" height="178" alt="Santa's Sleigh" style="display: block;" />
        </td>
    </tr>
    <tr>
        <td align="left" style="padding: 20px 30px; font-size: 24px; font-style: italic; color: #c00000;">
            Dear {child_name}, ❤️
        </td>
    </tr>
    <tr>
        <td align="left" style="padding: 10px 30px; font-size: 16px; line-height: 1.6;">
            <p>Your wonderful letter has arrived at the North Pole! ❄️</p>
            <p>I was so happy to read what you wrote. My elves and I are working hard in our workshop, and the reindeer are practicing their flying for the big night! 🦌✨</p>
            <p>Remember to be kind to others and spread joy wherever you go. That's the true magic of Christmas! ⭐</p>
        </td>
    </tr>
    <tr>
        <td align="center" style="padding: 20px 30px;">
            <h2 style="margin: 0; color: #c00000; font-family: Georgia, serif; font-size: 28px; font-style: italic; text-align: center;">
                ⭐ A Very Important Job For You! ⭐
            </h2>
        </td>
    </tr>
    <tr>
        <td align="left" style="padding: 10px 30px 20px 30px; font-size: 18px; line-height: 1.5;">
            Do something kind for someone today! It could be helping a family member, sharing with a friend, or giving someone a compliment. These little acts of kindness make Santa's heart so happy! 🎁
        </td>
    </tr>
    <tr>
        <td align="center" style="padding: 20px;">
            <img src="cid:elves_bell" width="258" height="193" alt="Elves celebrating" style="display: block;" />
        </td>
    </tr>
    <tr>
        <td align="center" style="padding: 10px 30px;">
            <p style="font-size: 22px; color: #c00000; font-weight: bold; margin-bottom: 15px;">
                Merry Christmas, little friend! ☃️❤️
            </p>
            <p style="font-size: 24px; font-style: italic; color: #5a3a22; line-height: 1.4; margin: 0;">
                Love from the North Pole,<br>
                Santa & The Elves 🎅🧝‍♂️🧝‍♀️
            </p>
        </td>
    </tr>
</table>"""

        return {
            "html_body": html_body,
            "text_body": text_body,
            "suggested_deed": "Do something kind for someone today!",
            "images_used": ["santa_sleigh", "elves_bell"]
        }
    
    def generate_deed_email(
        self,
        child_name: str,
        child_age: Optional[int],
        deed_description: str,
        language: Optional[str] = None
    ) -> dict:
        """
        Generate a special rich HTML email from Santa about a new good deed.
        
        Args:
            child_name: Child's first name
            child_age: Child's age (if known)
            deed_description: The good deed to do
            
        Returns:
            Dict with html_body, text_body, images_used
        """
        from app.email_templates.image_catalog import get_catalog_for_gpt
        
        age_context = f"The child is approximately {child_age} years old." if child_age else "Age unknown."
        image_catalog = get_catalog_for_gpt()
        
        system_prompt = deed_email.get_deed_email_system(
            age_context=age_context,
            image_catalog=image_catalog,
            language=language
        )
        user_prompt = deed_email.get_deed_email_user(child_name, deed_description)

        try:
            response = self._chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                response_format={"type": "json_object"}
            )
            
            import json
            data = json.loads(response)
            
            # Ensure mandatory images
            images = data.get("images_used", [])
            if "santa_sleigh" not in images:
                images.append("santa_sleigh")
            if "elves_bell" not in images:
                images.append("elves_bell")
            
            return {
                "html_body": data.get("html_body", ""),
                "text_body": data.get("text_body", f"🎅 Ho ho ho, {child_name}! Santa has a special mission for you! ✨"),
                "images_used": images
            }
            
        except Exception as e:
            logger.error(f"Error generating deed email: {e}")
            return {
                "html_body": "",
                "text_body": f"🎅❤️ Ho ho ho, {child_name}! ❤️🎅\n\n⭐ Santa has a very special mission for you! ⭐\n\n{deed_description}\n\n✨ This would make Santa so proud! Remember, every act of kindness makes the world a little brighter and spreads Christmas magic! 🎄❤️\n\n🌟 You can do it! I believe in you! 🌟\n\nWith love and jingle bells,\n🎅 Santa Claus 🔔✨",
                "images_used": ["santa_sleigh", "elves_bell"]
            }
    
    def generate_deed_congrats_email(
        self,
        child_name: str,
        child_age: Optional[int],
        deed_description: str,
        parent_note: Optional[str] = None,
        language: Optional[str] = None
    ) -> dict:
        """
        Generate a rich HTML congratulations email from Santa for completing a good deed.
        
        Args:
            child_name: Child's first name
            child_age: Child's age (if known)
            deed_description: The good deed that was completed
            parent_note: Optional parent's note about how it went
            
        Returns:
            Dict with html_body, text_body, images_used
        """
        from app.email_templates.image_catalog import get_catalog_for_gpt
        
        age_context = f"The child is approximately {child_age} years old." if child_age else "Age unknown."
        image_catalog = get_catalog_for_gpt()
        
        system_prompt = deed_congrats.get_deed_congrats_system(
            age_context=age_context,
            image_catalog=image_catalog,
            language=language
        )
        user_prompt = deed_congrats.get_deed_congrats_user(child_name, deed_description, parent_note)

        try:
            response = self._chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model,
                response_format={"type": "json_object"}
            )
            
            import json
            data = json.loads(response)
            
            # Ensure mandatory images
            images = data.get("images_used", [])
            if "santa_sleigh" not in images:
                images.append("santa_sleigh")
            if "elves_bell" not in images:
                images.append("elves_bell")
            
            return {
                "html_body": data.get("html_body", ""),
                "text_body": data.get("text_body", f"🎉 Ho ho ho, {child_name}! You did it! 🌟"),
                "images_used": images
            }
            
        except Exception as e:
            logger.error(f"Error generating congrats email: {e}")
            return {
                "html_body": "",
                "text_body": f"🎅🎉 Ho ho ho, {child_name}! 🎉🎅\n\n⭐✨ WONDERFUL NEWS! ✨⭐\n\nSanta just heard that you completed your good deed: {deed_description}\n\n🌟 I am SO PROUD of you! 🌟\n\nThis is exactly the kind of kindness that makes Christmas magic real! You've made Santa's heart very happy today! ❤️🎄\n\n⭐ You're definitely on the Nice List! ⭐\n\nKeep being the amazing person you are! 🎁✨\n\nWith proud jingle bells,\n🎅 Santa Claus 🔔❤️✨",
                "images_used": ["santa_sleigh", "elves_bell"]
            }
    
    def check_email_safety(
        self,
        email_content: str,
        child_name: str,
        email_type: str  # letter_reply, deed_email, deed_congrats
    ) -> tuple[bool, Optional[str]]:
        """
        Check if AI-generated email content is safe for children.
        Uses a separate GPT model for defense-in-depth safety checking.
        
        Args:
            email_content: The AI-generated email text to verify
            child_name: The child's name (for context)
            email_type: Type of email - letter_reply, deed_email, or deed_congrats
            
        Returns:
            Tuple of (is_safe: bool, reason_if_unsafe: Optional[str])
        """
        system_prompt = safety.get_safety_check_system(email_type, child_name)
        user_prompt = safety.get_safety_check_user(email_content, child_name)

        try:
            response = self._chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.safety_model,
                response_format={"type": "json_object"}
            )
            
            data = json.loads(response)
            is_safe = data.get("is_safe", False) and data.get("recommendation") == "APPROVE"
            
            if not is_safe:
                issues = data.get("issues_found", [])
                explanation = data.get("explanation", "Safety check failed")
                severity = data.get("severity", "unknown")
                reason = f"[{severity.upper()}] {explanation}"
                if issues:
                    reason += f" Issues: {', '.join(issues)}"
                return False, reason
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error in email safety check: {e}")
            # On error, fail closed (block the email) for safety
            return False, f"Safety check system error: {str(e)}"


# Singleton instance
_gpt_service: Optional[GPTService] = None


def get_gpt_service() -> GPTService:
    """Get the GPT service singleton."""
    global _gpt_service
    if _gpt_service is None:
        _gpt_service = GPTService()
    return _gpt_service
