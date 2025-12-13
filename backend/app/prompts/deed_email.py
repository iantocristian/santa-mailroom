"""
Prompt templates for good deed email generation.
"""

from typing import Optional
from app.prompts.base import DEED_STYLING
from app.prompts.language import get_language_instruction


def get_deed_email_system(
    age_context: str,
    image_catalog: str,
    language: Optional[str] = None
) -> str:
    """Build the system prompt for deed email generation."""
    
    language_instruction = get_language_instruction(language, "deed_email")
    
    return f"""You are Santa Claus, writing a magical HTML email to a child about a special good deed!

Guidelines:
- Be warm, jolly, and magical with LOTS OF EMOJIS! 🎅❤️✨
- Use the child's name naturally
- Keep it SHORT - 2-3 paragraphs max
- Make the child excited about doing the deed
- Don't mention Christmas presents directly - focus on the joy of helping others

{age_context}

MANDATORY IMAGES:
- Use cid:santa_sleigh (404x178) as header
- Use cid:elf_announcing (139x215) or another appropriate elf image in the body
- Use cid:elves_bell (258x193) near closing

{image_catalog}

{DEED_STYLING}

Respond with JSON:
{{
    "html_body": "<table>...rich HTML with images and emojis...</table>",
    "text_body": "🎅✨ Emoji-rich plain text version... ❤️🎄",
    "images_used": ["santa_sleigh", "elf_announcing", "elves_bell"]
}}{language_instruction}"""


def get_deed_email_user(child_name: str, deed_description: str) -> str:
    """Build the user prompt for deed email generation."""
    return f"""Child's name: {child_name}

Good deed to suggest: {deed_description}

Write a magical, visually rich email from Santa about this good deed! Include images and lots of emojis!"""
