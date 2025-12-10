"""
Image catalog for Santa email templates.
Contains metadata about available images for GPT to select from when generating emails.
"""
import os
from typing import List, Dict
from dataclasses import dataclass

# Path to images directory
IMAGES_DIR = os.path.join(os.path.dirname(__file__), "img")


@dataclass
class EmailImage:
    """An image available for inclusion in Santa emails."""
    filename: str
    cid: str  # Content-ID for email embedding
    width: int
    height: int
    description: str  # For GPT to understand what the image shows
    use_for: List[str]  # Suggested use cases


# All available images with metadata
AVAILABLE_IMAGES: List[EmailImage] = [
    # Characters
    EmailImage(
        filename="ms_and_mr_santa-230x241.png",
        cid="santa_mrs",
        width=230, height=241,
        description="Mr. and Mrs. Santa Claus together, warm and friendly",
        use_for=["greeting", "closing", "christmas_wish"]
    ),
    EmailImage(
        filename="elf_announcing_139x215.png",
        cid="elf_announcing",
        width=139, height=215,
        description="An elf making an exciting announcement",
        use_for=["exciting_news", "special_message", "deed_announcement"]
    ),
    EmailImage(
        filename="elf_with_letter_121x165.png",
        cid="elf_letter",
        width=121, height=165,
        description="An elf happily holding a child's letter",
        use_for=["letter_received", "wishlist_mention", "opening"]
    ),
    EmailImage(
        filename="elf_with_many_letters_130x167.png",
        cid="elf_many_letters",
        width=130, height=167,
        description="An elf carrying a big stack of letters from children",
        use_for=["busy_workshop", "many_wishes", "popular_santa"]
    ),
    EmailImage(
        filename="elves_with_bell_258x193.png",
        cid="elves_bell",
        width=258, height=193,
        description="Group of elves celebrating with a bell",
        use_for=["celebration", "good_news", "deed_complete", "christmas_cheer"]
    ),
    EmailImage(
        filename="abominable_snowman_160x224.png",
        cid="snowman_friend",
        width=160, height=224,
        description="A friendly abominable snowman, cute and playful",
        use_for=["winter_fun", "north_pole_friend", "playful_moment"]
    ),
    
    # Santa's Transport
    EmailImage(
        filename="santa_sleigh_404x178.png",
        cid="santa_sleigh",
        width=404, height=178,
        description="Santa flying through the sky in his sleigh with reindeer",
        use_for=["christmas_eve", "magic", "flying", "closing", "header"]
    ),
    
    # Good List
    EmailImage(
        filename="nice_list_green_138x140.png",
        cid="nice_list_green",
        width=138, height=140,
        description="Santa's nice list scroll with green decoration",
        use_for=["good_behavior", "nice_list", "praise"]
    ),
    EmailImage(
        filename="nice_list_red_137x138.png",
        cid="nice_list_red",
        width=137, height=138,
        description="Santa's nice list scroll with red decoration",
        use_for=["good_behavior", "nice_list", "praise"]
    ),
    
    # Christmas Scenes
    EmailImage(
        filename="christmas_tree_196x291.png",
        cid="christmas_tree",
        width=196, height=291,
        description="A beautifully decorated Christmas tree with ornaments and star",
        use_for=["christmas_spirit", "decoration", "presents_under_tree"]
    ),
    EmailImage(
        filename="gingerbread_house_213x206.png",
        cid="gingerbread_house",
        width=213, height=206,
        description="A magical gingerbread house covered in candy",
        use_for=["treats", "christmas_magic", "north_pole"]
    ),
    EmailImage(
        filename="dreaming_208x197.png",
        cid="dreaming",
        width=208, height=197,
        description="A child peacefully dreaming of Christmas",
        use_for=["christmas_eve", "sleep", "dreams", "closing"]
    ),
    EmailImage(
        filename="cup_of_cocoa_109x100.png",
        cid="cocoa",
        width=109, height=100,
        description="A warm cup of hot cocoa with marshmallows",
        use_for=["cozy", "warm_wishes", "winter"]
    ),
    
    # Decorative Elements
    EmailImage(
        filename="bells_103x91.png",
        cid="bells",
        width=103, height=91,
        description="Jingle bells with a red bow",
        use_for=["decoration", "jingle", "christmas_cheer"]
    ),
    EmailImage(
        filename="bell_59x67.png",
        cid="bell_small",
        width=59, height=67,
        description="A single golden bell",
        use_for=["decoration", "accent"]
    ),
    EmailImage(
        filename="bell_r_56x75.png",
        cid="bell_small_r",
        width=56, height=75,
        description="A single golden bell (variant)",
        use_for=["decoration", "accent"]
    ),
    EmailImage(
        filename="candy_cane_v_45x84.png",
        cid="candy_cane",
        width=45, height=84,
        description="A red and white striped candy cane",
        use_for=["decoration", "treats", "christmas_cheer"]
    ),
    EmailImage(
        filename="candy_cane_v_r_55x97.png",
        cid="candy_cane_r",
        width=55, height=97,
        description="A red and white striped candy cane (variant)",
        use_for=["decoration", "treats", "christmas_cheer"]
    ),
    EmailImage(
        filename="candy_horizontal_102x57.png",
        cid="candy_horizontal",
        width=102, height=57,
        description="A horizontal candy cane decoration",
        use_for=["divider", "decoration"]
    ),
    EmailImage(
        filename="gingerbread_l_140x92.png",
        cid="gingerbread_large",
        width=140, height=92,
        description="A happy gingerbread man cookie",
        use_for=["treats", "fun", "christmas_baking"]
    ),
    EmailImage(
        filename="gingerbread_s_54x66.png",
        cid="gingerbread_small",
        width=54, height=66,
        description="A small gingerbread man cookie",
        use_for=["decoration", "accent"]
    ),
    EmailImage(
        filename="star_30x29.png",
        cid="star_small",
        width=30, height=29,
        description="A small golden star",
        use_for=["decoration", "magic", "accent"]
    ),
    EmailImage(
        filename="star_42x36.png",
        cid="star_medium",
        width=42, height=36,
        description="A glowing golden star",
        use_for=["decoration", "magic", "special"]
    ),
]


def get_image_catalog() -> List[EmailImage]:
    """Get all available images."""
    return AVAILABLE_IMAGES


def get_image_by_cid(cid: str) -> EmailImage | None:
    """Get an image by its Content-ID."""
    for img in AVAILABLE_IMAGES:
        if img.cid == cid:
            return img
    return None


def get_image_path(cid: str) -> str | None:
    """Get the full filesystem path for an image by CID."""
    img = get_image_by_cid(cid)
    if img:
        return os.path.join(IMAGES_DIR, img.filename)
    return None


def get_catalog_for_gpt() -> str:
    """
    Generate a formatted catalog description for GPT to understand available images.
    Used in the prompt for rich email generation.
    """
    lines = ["Available images (use src=\"cid:NAME\" to include):"]
    lines.append("")
    
    for img in AVAILABLE_IMAGES:
        uses = ", ".join(img.use_for)
        lines.append(f"- cid:{img.cid} ({img.width}x{img.height}): {img.description}")
        lines.append(f"  Best for: {uses}")
    
    return "\n".join(lines)


# Mandatory images that must appear in every email
MANDATORY_IMAGES = {
    "header": "santa_sleigh",  # Always show Santa's sleigh at top
    "footer": "elves_bell"     # Always show celebrating elves at bottom
}


def get_mandatory_images() -> dict:
    """Get the mandatory image CIDs for header and footer."""
    return MANDATORY_IMAGES.copy()


def ensure_mandatory_images(images_used: list) -> list:
    """Ensure mandatory images are included in the list."""
    result = list(images_used)
    for position, cid in MANDATORY_IMAGES.items():
        if cid not in result:
            result.append(cid)
    return result

