"""
Prompt templates for product search service.
"""


def get_product_search_prompt(
    item_name: str,
    country: str,
    child_name: str | None = None,
    child_age: int | None = None
) -> str:
    """
    Build the product search prompt with optional child context.
    
    Args:
        item_name: The product to search for
        country: Country code for regional results
        child_name: Child's name (to infer gender)
        child_age: Child's age (for age-appropriate products)
        
    Returns:
        Complete prompt string for product search
    """
    # Build child context for better product selection
    child_context = ""
    if child_name or child_age:
        child_context = "\n\nChild context:"
        if child_name:
            child_context += f"\n- Name: {child_name} (infer likely gender from the name and {country} cultural context)"
        if child_age:
            child_context += f"\n- Age: {child_age} years old"
        child_context += "\n\nIMPORTANT: Select a product variant appropriate for this child (e.g., boys/girls version, age-appropriate features, correct size range)."
    
    return f"""Search for this gift item for a child and provide purchase information:
        
Product: {item_name}
Country: {country}{child_context}

Find:
1. The exact product name as sold by a major retailer
2. Current price in {country} currency
3. A URL to purchase from a major retailer (Amazon, Target, Walmart, etc.)
4. A brief parent-friendly description

Respond with ONLY valid JSON in this exact format:
{{
  "name": "full product name",
  "estimated_price": 29.99,
  "currency": "USD",
  "product_url": "https://...",
  "description": "brief description"
}}"""
