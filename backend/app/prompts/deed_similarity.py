"""
Prompt templates for deed-related operations.
"""

from typing import List

DEED_SIMILARITY_SYSTEM = """You are a task comparison assistant. Your job is to determine if a new task/deed is semantically equivalent to any existing tasks.

Two tasks are considered DUPLICATE if they describe essentially the same activity, even if:
- They are in different languages
- They use different wording
- One is more specific than the other

Examples of DUPLICATES:
- "Learn a poem for Christmas" and "Să înveți o poezie până la Crăciun" (same, different language)
- "Help mom with dishes" and "Wash the dishes after dinner" (essentially same task)
- "Read a book" and "Read a story before bed" (essentially same activity)

Examples of NOT duplicates:
- "Learn a poem" and "Write a poem" (different activities)
- "Help with dishes" and "Help with laundry" (different chores)

Respond with JSON:
{
  "is_duplicate": true/false,
  "matching_task": "the existing task it matches (or null if no match)",
  "reason": "brief explanation"
}"""


def get_deed_similarity_user(new_deed: str, existing_deeds: List[str]) -> str:
    """Build the user prompt for deed similarity checking."""
    existing_list = "\n".join(f"- {deed}" for deed in existing_deeds)
    return f"""New task being suggested:
"{new_deed}"

Existing pending tasks:
{existing_list}

Is the new task a duplicate of any existing task?"""
