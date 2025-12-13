"""
Prompt templates for wish extraction and content moderation.
"""

EXTRACT_WISHES_SYSTEM = """You are an assistant that helps extract gift wishes from children's letters to Santa.

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


def get_extract_wishes_user(child_name: str, letter_text: str) -> str:
    return f"""Child's name: {child_name}

Letter:
{letter_text}

Extract all wish items from this letter."""


def get_moderation_system(strictness: str) -> str:
    strictness_guide = {
        "low": "Only flag very serious concerns like explicit mentions of harm, abuse, or crisis.",
        "medium": "Flag concerning content including sadness, anxiety, bullying mentions, family problems, or hints at self-harm.",
        "high": "Flag any content that might indicate the child is struggling emotionally, including mild sadness, loneliness, or stress."
    }
    
    return f"""You are a child safety specialist reviewing letters to Santa.
        
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


def get_moderation_user(child_name: str, letter_text: str) -> str:
    return f"""Child's name: {child_name}

Letter:
{letter_text}

Analyze this letter for any concerning content."""
