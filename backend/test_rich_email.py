"""
Quick test script for rich Santa email generation.
Run: python test_rich_email.py
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.gpt_service import get_gpt_service
from app.email_templates.image_catalog import get_catalog_for_gpt, get_image_path

def test_rich_email():
    """Generate a test email and save to file for preview."""
    
    gpt_service = get_gpt_service()
    
    # Sample letter
    child_name = "Emma"
    letter_text = """
    Dear Santa,
    
    My name is Emma and I am 7 years old. This year I have been very good!
    I helped my mom with dishes and was nice to my little brother (most of the time).
    
    For Christmas I would like:
    - A unicorn stuffed animal
    - Art supplies for drawing
    - Books about animals
    
    I will leave you cookies and milk!
    
    Love,
    Emma
    """
    
    print("🎅 Generating rich Santa email...")
    print(f"   Child: {child_name}")
    print(f"   Using GPT to compose unique email with images...\n")
    
    # Generate rich email
    result = gpt_service.generate_rich_santa_email(
        letter_text=letter_text,
        child_name=child_name,
        child_age=7,
        wish_items=[{"name": "unicorn stuffed animal"}, {"name": "art supplies"}, {"name": "animal books"}],
        denied_items=[],
        pending_deeds=[],
        completed_deeds=[],
        has_concerning_content=False,
        image_catalog=get_catalog_for_gpt()
    )
    
    print("✅ Email generated!")
    print(f"   Images used: {result['images_used']}")
    print(f"   Suggested deed: {result['suggested_deed']}")
    
    # Save HTML to file for preview
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    html_path = os.path.join(output_dir, "santa_email.html")
    txt_path = os.path.join(output_dir, "santa_email.txt")
    
    # Create full HTML with placeholder images (for browser preview)
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Santa Email Preview</title>
    <style>
        body {{ background: #f4f4f4; padding: 20px; font-family: Georgia, serif; }}
        .preview-note {{ background: #ffe0e0; padding: 10px; margin-bottom: 20px; border-radius: 5px; }}
    </style>
</head>
<body>
    <div class="preview-note">
        <strong>🎅 Preview Mode</strong><br>
        Images shown below use placeholder references. In real emails, they're embedded via CID.<br>
        Images used: {', '.join(result['images_used'])}
    </div>
    {result['html_body'].replace('cid:', 'app/email_templates/img/').replace('santa_sleigh', 'santa_sleigh_404x178.png').replace('elves_bell', 'elves_with_bell_258x193.png').replace('elf_letter', 'elf_with_letter_121x165.png').replace('nice_list_green', 'nice_list_green_138x140.png').replace('christmas_tree', 'christmas_tree_196x291.png').replace('dreaming', 'dreaming_208x197.png').replace('cocoa', 'cup_of_cocoa_109x100.png')}
</body>
</html>"""
    
    with open(html_path, "w") as f:
        f.write(full_html)
    
    with open(txt_path, "w") as f:
        f.write(result['text_body'])
    
    print(f"\n📄 Files saved:")
    print(f"   HTML: {html_path}")
    print(f"   TXT:  {txt_path}")
    print(f"\n🌐 Open in browser: file://{os.path.abspath(html_path)}")
    
    # Also print the plain text version
    print("\n" + "="*60)
    print("PLAIN TEXT VERSION:")
    print("="*60)
    print(result['text_body'])

if __name__ == "__main__":
    test_rich_email()
