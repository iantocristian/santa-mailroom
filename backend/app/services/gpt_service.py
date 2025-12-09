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
        system_prompt = """You are an assistant that helps extract gift wishes from children's letters to Santa.

Extract all gift requests, wishes, or items the child mentions wanting. For each item:
1. Extract the exact text as mentioned
2. Normalize it to a searchable product name
3. Categorize it (toys, books, clothes, electronics, games, sports, crafts, pets, experiences, other)

Be thorough - children often mention wishes casually or indirectly.

Respond with JSON in this format:
{
  "items": [
    {
      "raw_text": "exact text from letter",
      "normalized_name": "searchable product name",
      "category": "category"
    }
  ]
}

If no wishes are found, return {"items": []}"""

        user_prompt = f"""Child's name: {child_name}

Letter:
{letter_text}

Extract all wish items from this letter."""

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
        strictness_guide = {
            "low": "Only flag very serious concerns like explicit mentions of harm, abuse, or crisis.",
            "medium": "Flag concerning content including sadness, anxiety, bullying mentions, family problems, or hints at self-harm.",
            "high": "Flag any content that might indicate the child is struggling emotionally, including mild sadness, loneliness, or stress."
        }
        
        system_prompt = f"""You are a child safety specialist reviewing letters to Santa.
        
Your job is to identify any concerning content that parents should be aware of.
Strictness level: {strictness}
{strictness_guide.get(strictness, strictness_guide["medium"])}

Categories to check:
- self_harm: Any hints at self-harm or suicidal ideation
- abuse: Signs of physical, emotional, or neglect
- bullying: Being bullied or bullying others
- sad: General sadness, depression, loneliness
- anxious: Anxiety, worry, fear
- family_issues: Divorce, fighting, loss, stress at home
- violence: Concerning interest in violence

For each concern found, provide:
- type: category from above
- severity: low, medium, or high
- excerpt: the concerning text
- confidence: 0.0-1.0 how confident you are
- explanation: brief explanation of why this is concerning

Respond with JSON:
{{
  "is_concerning": boolean,
  "flags": [
    {{
      "type": "category",
      "severity": "level",
      "excerpt": "text",
      "confidence": 0.0-1.0,
      "explanation": "why this is concerning"
    }}
  ]
}}"""

        user_prompt = f"""Child's name: {child_name}

Letter:
{letter_text}

Analyze this letter for any concerning content."""

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
    
    def generate_deed_email(
        self,
        child_name: str,
        child_age: Optional[int],
        deed_description: str
    ) -> str:
        """
        Generate a special email from Santa about a new good deed.
        
        Args:
            child_name: Child's first name
            child_age: Child's age (if known)
            deed_description: The good deed to do
            
        Returns:
            Email body text
        """
        age_context = f"The child is approximately {child_age} years old." if child_age else "Age unknown."
        
        system_prompt = f"""You are Santa Claus, writing a short, magical email to a child about a special good deed you'd like them to do.

Guidelines:
- Be warm, jolly, and magical
- Use the child's name naturally
- Keep it SHORT - 2-3 paragraphs max
- Make the child excited about doing the deed
- Don't mention Christmas presents directly - focus on the joy of helping others
- End with encouragement

{age_context}"""

        user_prompt = f"""Child's name: {child_name}

Good deed to suggest: {deed_description}

Write a short, magical email from Santa about this good deed!"""

        try:
            response = self._chat(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model=self.model
            )
            return response
            
        except Exception as e:
            logger.error(f"Error generating deed email: {e}")
            return f"Ho ho ho, {child_name}!\n\nSanta has a very special request for you! I'd love it if you could: {deed_description}\n\nThis would make Santa so proud! Remember, every act of kindness makes the world a little brighter.\n\nWith love,\n🎅 Santa Claus"


# Singleton instance
_gpt_service: Optional[GPTService] = None


def get_gpt_service() -> GPTService:
    """Get the GPT service singleton."""
    global _gpt_service
    if _gpt_service is None:
        _gpt_service = GPTService()
    return _gpt_service
