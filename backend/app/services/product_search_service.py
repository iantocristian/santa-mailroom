"""
Product search service using OpenAI Responses API with web search.
Uses the built-in web_search tool for real-time product discovery.
"""
import json
import logging
from typing import Optional
from dataclasses import dataclass

from openai import OpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class ProductSearchResult:
    """Result of product search."""
    name: str
    estimated_price: Optional[float] = None
    currency: str = "USD"
    product_url: Optional[str] = None
    image_url: Optional[str] = None
    description: Optional[str] = None


class ProductSearchService:
    """
    Product search using OpenAI Responses API with web_search tool.
    
    This uses the new Responses API which has built-in web search capability.
    """
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
    
    def search(self, item_name: str, country: str = "US") -> Optional[ProductSearchResult]:
        """
        Search for a product using web search.
        
        Args:
            item_name: The product to search for
            country: Country code for regional results
            
        Returns:
            ProductSearchResult or None if not found
        """
        if not self.client:
            logger.warning("OpenAI API key not configured")
            return None
        
        prompt = f"""Search for this gift item for a child and provide purchase information:
        
Product: {item_name}
Country: {country}

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

        try:
            # Use Responses API with web_search tool
            response = self.client.responses.create(
                model="gpt-4o",
                input=prompt,
                tools=[{
                    "type": "web_search",
                    "search_context_size": "medium"
                }]
            )
            
            # Extract text content from response
            content = ""
            for item in response.output:
                if item.type == "message":
                    for block in item.content:
                        if hasattr(block, 'text'):
                            content += block.text
            
            # Parse JSON from response
            # Try to find JSON in the response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                data = json.loads(json_str)
                
                return ProductSearchResult(
                    name=data.get("name", item_name),
                    estimated_price=data.get("estimated_price"),
                    currency=data.get("currency", "USD"),
                    product_url=data.get("product_url"),
                    image_url=data.get("image_url"),
                    description=data.get("description")
                )
            else:
                logger.warning(f"Could not parse JSON from response: {content[:200]}")
                return None
            
        except Exception as e:
            logger.error(f"Error searching for product '{item_name}': {e}")
            return None


# Singleton instance
_product_search_service: Optional[ProductSearchService] = None


def get_product_search_service() -> ProductSearchService:
    """Get the product search service singleton."""
    global _product_search_service
    if _product_search_service is None:
        _product_search_service = ProductSearchService()
    return _product_search_service
