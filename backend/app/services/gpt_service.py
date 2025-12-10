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
        image_catalog: str = ""
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

        system_prompt = f"""You are Santa Claus creating a magical, personalized HTML email for a child.

You will generate a complete HTML email body with images selected from the available catalog.
The email should feel unique and personal, not formulaic.

Guidelines:
- Be warm, jolly, and magical
- Use the child's name naturally throughout
- Reference specific things from their letter
- Keep appropriate for the child's age
- Include 3-5 images from the catalog to make the email visually delightful
- Suggest ONE simple good deed for the week

MANDATORY IMAGES (must include these):
- Header: Use cid:santa_sleigh as a banner image at the top (404x178)
- Footer: Use cid:elves_bell near the closing (258x193)
- Select 2-4 additional images from the catalog for the body

{age_context}
{items_context}
{deeds_context}
{concerning_addon}

{image_catalog}

CRITICAL HTML STRUCTURE RULES:
1. Use table-based layout for email compatibility (no div, no CSS flexbox/grid)
2. Images must use src="cid:NAME" format (e.g., src="cid:santa_sleigh")
3. Use inline styles only (style="...")
4. Keep width max 600px for main content, center align
5. Use Georgia or serif fonts
6. Colors: #c00000 (Santa red), #5a3a22 (warm brown), #FFF8DC (cream background)
7. Wrap everything in a table with background-color: #FFF8DC and border: 1px solid #d4af37

PLAIN TEXT VERSION:
- Include festive emojis: 🎅 🎄 ❄️ 🎁 ⭐ 🦌 🛷 ❤️ ✨
- Make it warm and readable without HTML
- Keep the same magical content

Respond with JSON in this exact format:
{{
    "html_body": "<table>...complete HTML email content with mandatory header/footer images...</table>",
    "text_body": "🎅 Ho ho ho! Plain text version with emojis... 🎄",
    "suggested_deed": "One specific good deed suggestion",
    "images_used": ["santa_sleigh", "elves_bell", "other_cid_1", "other_cid_2"]
}}

Make each email unique and magical! Vary the structure, image placement, and writing style."""

        user_prompt = f"""Create a magical email for {child_name}!

Their letter:
{letter_text}

Generate a beautiful, unique HTML email from Santa with appropriate images. Remember to include the mandatory header (santa_sleigh) and footer (elves_bell) images!"""

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

🎁 Keep being the wonderful person you are! 🎁

With love from the North Pole,
🎅 Santa Claus & The Elves 🧝‍♂️🧝‍♀️

❤️ Merry Christmas! ❤️"""

        # Static HTML with mandatory images
        html_body = f"""<table border="0" cellpadding="0" cellspacing="0" width="600" style="background-color: #FFF8DC; border: 1px solid #d4af37; font-family: Georgia, 'Times New Roman', serif; color: #5a3a22;">
    <tr>
        <td align="center" style="padding: 0;">
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
            <p style="font-weight: bold; color: #c00000;">Keep being the wonderful person you are! 🎁</p>
        </td>
    </tr>
    <tr>
        <td align="center" style="padding: 20px;">
            <img src="cid:elves_bell" width="258" height="193" alt="Elves celebrating" style="display: block;" />
        </td>
    </tr>
    <tr>
        <td align="center" style="padding: 20px 30px; font-size: 20px; font-style: italic; color: #c00000;">
            With love from the North Pole,<br/>
            <span style="font-size: 28px;">🎅 Santa Claus</span>
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
    
    def generate_deed_congrats_email(
        self,
        child_name: str,
        child_age: Optional[int],
        deed_description: str,
        parent_note: Optional[str] = None
    ) -> str:
        """
        Generate a congratulations email from Santa for completing a good deed.
        
        Args:
            child_name: Child's first name
            child_age: Child's age (if known)
            deed_description: The good deed that was completed
            parent_note: Optional parent's note about how it went
            
        Returns:
            Email body text
        """
        age_context = f"The child is approximately {child_age} years old." if child_age else "Age unknown."
        
        note_context = ""
        if parent_note:
            note_context = f"\n\nNote from parent about how it went: {parent_note}"
        
        system_prompt = f"""You are Santa Claus, writing a short, celebratory email to a child who just completed a good deed!

Guidelines:
- Be VERY excited and proud!
- Use the child's name naturally
- Keep it SHORT - 2-3 paragraphs max
- Specifically mention what they did
- Make them feel special and proud
- End with encouragement to keep being kind

{age_context}"""

        user_prompt = f"""Child's name: {child_name}

Good deed they completed: {deed_description}{note_context}

Write a SHORT, celebratory email from Santa congratulating them!"""

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
            logger.error(f"Error generating congrats email: {e}")
            return f"Ho ho ho, {child_name}!\n\n🎉 WONDERFUL NEWS! 🎉\n\nSanta just heard that you completed your good deed: {deed_description}\n\nI am SO PROUD of you! This is exactly the kind of kindness that makes Christmas magic real. You've made Santa's heart very happy today!\n\nKeep being the amazing person you are!\n\nWith extra jingle bells,\n🎅 Santa Claus"
    
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
        email_type_descriptions = {
            "letter_reply": "a reply from Santa to a child's letter",
            "deed_email": "Santa encouraging a child to do a good deed",
            "deed_congrats": "Santa congratulating a child for completing a good deed"
        }
        
        type_desc = email_type_descriptions.get(email_type, "an email from Santa to a child")
        
        system_prompt = f"""You are a child safety content moderator. Your job is to verify that AI-generated emails are safe and appropriate for children.

You are reviewing {type_desc}.

Check for these safety issues:
1. INAPPROPRIATE LANGUAGE: Profanity, slurs, adult language, crude humor
2. ADULT THEMES: Violence, sexuality, drugs, alcohol, gambling, scary content
3. HARMFUL CONTENT: Bullying, discrimination, self-harm references, dangerous activities
4. MANIPULATION: Pressure tactics, guilt-tripping, inappropriate requests
5. PRIVACY CONCERNS: Requests for personal information, addresses, phone numbers
6. OFF-TOPIC: Content that doesn't match the expected email type (e.g., not about Christmas/Santa)
7. TONE ISSUES: Scary, threatening, overly negative, or discouraging tone

This email is for a child named {child_name}.

Respond with JSON in this exact format:
{{
  "is_safe": true/false,
  "issues_found": ["list of specific issues found, empty if safe"],
  "severity": "none" | "low" | "medium" | "high",
  "recommendation": "APPROVE" | "BLOCK",
  "explanation": "Brief explanation of your decision"
}}

Be strict but reasonable. Santa emails should be warm, encouraging, magical, and age-appropriate."""

        user_prompt = f"""Please review this email that will be sent to a child:

---
{email_content}
---

Is this email safe and appropriate for the child {child_name}?"""

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
