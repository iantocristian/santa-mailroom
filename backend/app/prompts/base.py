"""
Shared styling rules and constants for Santa email generation.
"""

# Emoji usage guide
EMOJI_GUIDE = """
EMOJI USAGE GUIDE (use these generously!):
🎅 Santa | 🎄 Christmas tree | ❄️ Snowflake | ⭐ Star | ✨ Sparkle
🦌 Reindeer | 🛷 Sleigh | 🎁 Present | ❤️ Heart | 🧝‍♂️🧝‍♀️ Elves
☃️ Snowman | 🍪 Cookie | 🥛 Milk | 🔔 Bell | 🌟 Glowing star
"""

# Celebration emojis for congrats emails
CELEBRATION_EMOJI_GUIDE = """
USE CELEBRATION EMOJIS: 🎉 ⭐ ❤️ ✨ 🎅 🎄 🌟 🏆 👏 🥳 💫
"""

# HTML structure rules for email compatibility
HTML_RULES = """
HTML STRUCTURE RULES:
1. Use table-based layout for email compatibility (no div, no CSS flexbox/grid)
2. Images must use src="cid:NAME" format (e.g., src="cid:santa_sleigh")
3. Use inline styles only (style="...")
4. Keep width max 600px for main content, center align
5. Wrap everything in a table with background-color: #FFF8DC and border: 1px solid #d4af37
6. Place images next to text in table cells for visual interest
"""

# Plain text formatting rules
PLAIN_TEXT_RULES = """
PLAIN TEXT VERSION:
- Use LOTS of emojis: 🎅 🎄 ❄️ 🎁 ⭐ 🦌 🛷 ❤️ ✨ ☃️ 🧝‍♂️🧝‍♀️
- Start each paragraph or section with emojis
- Make it warm, festive, and readable
"""

# Mandatory images for all Santa emails
MANDATORY_IMAGES = """
MANDATORY IMAGES (must include these):
- Header: Use cid:santa_sleigh as a banner image at the top (404x178)
- Footer: Use cid:elves_bell near the closing (258x193)
"""

# Styling rules for Santa emails
STYLING_RULES = """
CRITICAL STYLING RULES (make it visually rich with LOTS OF EMOJIS!):

1. GREETING (red, italic, with heart emoji):
   <td style="padding: 20px 30px; font-size: 24px; font-style: italic; color: #c00000;">
       Dear [Name], ❤️✨
   </td>

2. SECTION HEADINGS (use emojis liberally!):
   - "🎄 Your Letter Arrived! 🎄" or "❄️ News from the Workshop! ❄️"
   - "🦌 The Reindeer Are Ready! 🦌" or "⭐ You're On the Nice List! ⭐"
   - Style: color: #c00000; font-size: 20-22px; font-weight: bold;

3. GOOD DEED HEADING (red, italic, with star emojis):
   <h2 style="margin: 0; color: #c00000; font-family: Georgia, serif; font-size: 28px; font-style: italic; text-align: center;">
       ⭐ A Very Important Job For You! ⭐
   </h2>

4. CLOSING MESSAGE (red, bold, larger):
   <p style="font-size: 22px; color: #c00000; font-weight: bold;">
       Merry Christmas, little friend! ☃️❤️🎄
   </p>

5. SIGNATURE (brown, italic, elegant):
   <p style="font-size: 24px; font-style: italic; color: #5a3a22; line-height: 1.4;">
       Love from the North Pole,<br>
       Santa & The Elves 🎅🧝‍♂️🧝‍♀️🦌❤️
   </p>

6. BODY TEXT with emojis: 
   - Sprinkle emojis throughout paragraphs: ✨ ❄️ 🎁 ⭐ 🦌 🎄 ❤️ 🛷 ☃️ 🍪 🥛
   - End sentences with relevant emojis
   - font-size: 16-18px, line-height: 1.5-1.6, color: #5a3a22
"""

# Deed email styling
DEED_STYLING = """
STYLING (same as Santa replies):
1. GREETING: style="font-size: 24px; font-style: italic; color: #c00000;"
   "Dear [Name], ❤️✨"

2. DEED HEADING: style="color: #c00000; font-size: 28px; font-style: italic;"
   "⭐ Santa Has a Special Mission For You! ⭐"

3. CLOSING: style="font-size: 22px; color: #c00000; font-weight: bold;"
   "You can do it! I believe in you! 🌟❤️"

4. SIGNATURE: style="font-size: 24px; font-style: italic; color: #5a3a22;"
   "With love and jingle bells, Santa 🎅🔔✨"

5. USE EMOJIS EVERYWHERE: ⭐ ❤️ ✨ 🎅 🎄 🦌 🧝‍♂️ 🎁 ☃️ 🌟

HTML: Use table-based layout, max 600px width, background #FFF8DC, border: 1px solid #d4af37
"""

# Congrats email styling
CONGRATS_STYLING = """
STYLING (celebratory theme!):
1. GREETING: style="font-size: 24px; font-style: italic; color: #c00000;"
   "Dear [Name], 🌟❤️✨"

2. CELEBRATION HEADING: style="color: #c00000; font-size: 28px; font-style: italic;"
   "🎉⭐ YOU DID IT! AMAZING! ⭐🎉" or "🎉✨ WONDERFUL NEWS! ✨🎉"

3. NICE LIST MESSAGE: style="font-size: 20px; color: #c00000; font-weight: bold;"
   "⭐ You're definitely on the Nice List! ⭐" 

4. CLOSING: style="font-size: 22px; color: #c00000; font-weight: bold;"
   "Santa is SO PROUD of you! 🎅❤️🌟"

5. SIGNATURE: style="font-size: 24px; font-style: italic; color: #5a3a22;"
   "With proud jingle bells, Santa 🎅🔔✨❤️"

6. USE CELEBRATION EMOJIS: 🎉 ⭐ ❤️ ✨ 🎅 🎄 🌟 🏆 👏 🥳 💫

HTML: Use table-based layout, max 600px width, background #FFF8DC, border: 1px solid #d4af37
"""
