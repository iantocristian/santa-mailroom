"""
Language instruction templates for multi-language email generation.
"""


def get_language_instruction(language: str | None, email_type: str = "santa_email") -> str:
    """
    Get the language instruction for a specific email type.
    
    Args:
        language: Language code (e.g., "ro", "es", "fr") or None for English
        email_type: One of "santa_email", "deed_email", "deed_congrats"
    
    Returns:
        Language instruction string to append to the prompt, empty if English
    """
    if not language or language.lower() == "en":
        return ""
    
    lang = language.upper()
    
    if email_type == "santa_email":
        return f"""

⚠️ CRITICAL LANGUAGE REQUIREMENT ⚠️
Write the ENTIRE email in {lang}. This is MANDATORY.
- Translate ALL text including greetings, headings, body, closing, and signature
- The English examples above are for STYLING ONLY - translate them to {lang}
- "Dear [Name]" → translate to {lang}
- "Your Letter Arrived" → translate to {lang}
- "You're On the Nice List" → translate to {lang}
- "A Very Important Job For You" → translate to {lang}
- "Merry Christmas, little friend" → translate to {lang}
- "Love from the North Pole, Santa & The Elves" → translate to {lang}
- Use culturally appropriate expressions for {lang} speakers
- Only image CID references stay in English (e.g., cid:santa_sleigh)
DO NOT USE ANY ENGLISH TEXT IN THE EMAIL CONTENT!"""
    
    elif email_type == "deed_email":
        return f"""

⚠️ CRITICAL LANGUAGE REQUIREMENT ⚠️
Write the ENTIRE email in {lang}. This is MANDATORY.
- Translate ALL text including greeting, deed description, closing, signature
- The English examples above are for STYLING ONLY - translate them to {lang}
- "Dear [Name]" → translate to {lang}
- "Santa Has a Special Mission For You" → translate to {lang}
- "You can do it! I believe in you!" → translate to {lang}
- "With love and jingle bells, Santa" → translate to {lang}
- Only image CID references stay in English
DO NOT USE ANY ENGLISH TEXT IN THE EMAIL CONTENT!"""
    
    elif email_type == "deed_congrats":
        return f"""

⚠️ CRITICAL LANGUAGE REQUIREMENT ⚠️
Write the ENTIRE email in {lang}. This is MANDATORY.
- Translate ALL text including greeting, celebration, closing, signature
- The English examples above are for STYLING ONLY - translate them to {lang}
- "Dear [Name]" → translate to {lang}
- "YOU DID IT! AMAZING!" → translate to {lang}
- "You're definitely on the Nice List!" → translate to {lang}
- "Santa is SO PROUD of you!" → translate to {lang}
- "With proud jingle bells, Santa" → translate to {lang}
- Only image CID references stay in English
DO NOT USE ANY ENGLISH TEXT IN THE EMAIL CONTENT!"""
    
    return ""
