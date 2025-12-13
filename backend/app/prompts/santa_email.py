"""
Prompt templates for Santa email reply generation.
"""

from typing import Optional, List
from app.prompts.base import STYLING_RULES, EMOJI_GUIDE, HTML_RULES, PLAIN_TEXT_RULES, MANDATORY_IMAGES
from app.prompts.language import get_language_instruction


def get_santa_email_system(
    age_context: str,
    items_context: str,
    deeds_context: str,
    concerning_addon: str,
    image_catalog: str,
    language: Optional[str] = None
) -> str:
    """Build the system prompt for Santa email generation."""
    
    language_instruction = get_language_instruction(language, "santa_email")
    
    return f"""You are Santa Claus creating a magical, personalized HTML email for a child.

You will generate a complete HTML email body with images selected from the available catalog.
The email should feel unique and personal, not formulaic.

Guidelines:
- Be warm, jolly, and magical
- Use the child's name naturally throughout
- Reference specific things from their letter
- Keep appropriate for the child's age
- Include 3-5 images from the catalog to make the email visually delightful
- If no pending good deeds exist, suggest ONE simple good deed for the week. Otherwise, gently remind the child of their existing deed(s)

{MANDATORY_IMAGES}
- Select 2-4 additional images from the catalog for the body

{age_context}
{items_context}
{deeds_context}
{concerning_addon}

{image_catalog}

{STYLING_RULES}

{EMOJI_GUIDE}

{HTML_RULES}

{PLAIN_TEXT_RULES}

Respond with JSON in this exact format:
{{
    "html_body": "<table>...complete HTML with rich styling and LOTS of emojis...</table>",
    "text_body": "🎅❄️ Ho ho ho! Festive text with many emojis... 🎄✨",
    "suggested_deed": "One specific good deed suggestion",
    "images_used": ["santa_sleigh", "elves_bell", "other_cid_1", "other_cid_2"]
}}

Make each email VISUALLY STUNNING with rich styling AND lots of festive emojis! 🎄✨{language_instruction}"""


def get_santa_email_user(child_name: str, letter_text: str) -> str:
    """Build the user prompt for Santa email generation."""
    return f"""Create a magical email for {child_name}!

Their letter:
{letter_text}

Generate a beautiful, unique HTML email from Santa with appropriate images. Remember to include the mandatory header (santa_sleigh) and footer (elves_bell) images!"""


def get_concerning_addon(has_concerning_content: bool) -> str:
    """Get the addon text if letter has concerning content."""
    if has_concerning_content:
        return """

IMPORTANT: The letter contained some concerning content. Include warm, supportive messaging.
Encourage the child to talk to their parents or a trusted adult if they're feeling sad or worried.
Keep it gentle and not alarming."""
    return ""


def build_items_context(wish_items: List[dict], denied_items: List[dict]) -> str:
    """Build the context string for wish items."""
    context = ""
    if wish_items:
        context += f"\n\nApproved/pending wishes: {', '.join(w.get('name', w.get('raw_text', '')) for w in wish_items)}"
    if denied_items:
        context += f"\n\nItems to redirect (don't mention directly, suggest alternatives): "
        for item in denied_items:
            context += f"\n- {item.get('name', '')}: {item.get('reason', 'not available')}"
    return context


def build_deeds_context(pending_deeds: List[str], completed_deeds: List[str]) -> str:
    """Build the context string for good deeds."""
    context = ""
    if completed_deeds:
        context += f"\n\nGood deeds completed recently (acknowledge these!): {', '.join(completed_deeds)}"
    if pending_deeds:
        context += f"\n\nPending good deeds (gently remind the child about these): {', '.join(pending_deeds)}"
        context += "\n\nSince pending deeds exist, set suggested_deed to null."
    return context
