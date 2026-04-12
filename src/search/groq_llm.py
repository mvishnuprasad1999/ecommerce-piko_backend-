import json
from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def parse_query(query: str):
    prompt = f"""You are an AI search engine for a grocery/supermarket app like Amazon or Flipkart.
Understand the user query deeply and extract search filters.

User Query: "{query}"

CRITICAL RULES:
1. NEVER change brand names (Milma, Britannia, Amul, KFC, etc.)
2. Fix only common spelling mistakes
3. For ambiguous stock/price queries, interpret smartly:
   - "stock 30" → exact or around 30 → use max_stock=30, min_stock=30
   - "stock less than 30" → max_stock=30
   - "stock more than 30" → min_stock=30  
   - "stock around 30" → min_stock=20, max_stock=40
   - "low stock" → max_stock=50
   - "high stock" → min_stock=100
   - "price 25" → exact price → min_price=20, max_price=30 (range around it)
   - "under 100" / "below 100" / "less than 100" → max_price=100
   - "above 100" / "more than 100" → min_price=100
   - "around 100" → min_price=80, max_price=120
   - "cheap" → max_price=50
   - "expensive" / "premium" → min_price=100
   - "expiring soon" → expiry_days=7
   - "expiring today" → expiry_days=1
   - "expiring this week" → expiry_days=7
   - "expiring this month" → expiry_days=30
   - "fresh" → expiry_days=30

Category mapping (EXACT names):
- milk, curd, butter, cheese, paneer, dairy → "Dairy"
- biscuit, chips, namkeen, chocolate, candy, cookies, wafer, snack → "Snacks"
- juice, water, soda, tea, coffee, drink, beverage → "Beverages"
- rice, wheat, flour, dal, pulses, grain → "Grains"
- oil, ghee, sunflower, coconut oil, cooking oil, frying oil → "Cooking"
- soap, shampoo, detergent → "Personal Care"
- tomato, potato, onion, vegetable → "Vegetables"
- apple, banana, mango, orange, fruit → "Fruits"

Return ONLY valid JSON no explanation:
{{"keywords": "...", "category": null, "max_price": null, "min_price": null, "min_stock": null, "max_stock": null, "expiry_days": null}}

Examples:
- "stock 30" → {{"keywords": "", "category": null, "max_price": null, "min_price": null, "min_stock": 30, "max_stock": 30, "expiry_days": null}}
- "low stock products" → {{"keywords": "", "category": null, "max_price": null, "min_price": null, "min_stock": null, "max_stock": 50, "expiry_days": null}}
- "high stock snacks" → {{"keywords": "snacks", "category": "Snacks", "max_price": null, "min_price": null, "min_stock": 100, "max_stock": null, "expiry_days": null}}
- "cheap milk" → {{"keywords": "milk", "category": "Dairy", "max_price": 50, "min_price": null, "min_stock": null, "max_stock": null, "expiry_days": null}}
- "premium snacks" → {{"keywords": "snacks", "category": "Snacks", "max_price": null, "min_price": 100, "min_stock": null, "max_stock": null, "expiry_days": null}}
- "products under price 100" → {{"keywords": "", "category": null, "max_price": 100, "min_price": null, "min_stock": null, "max_stock": null, "expiry_days": null}}
- "price 25" → {{"keywords": "", "category": null, "max_price": 30, "min_price": 20, "min_stock": null, "max_stock": null, "expiry_days": null}}
- "around 50 rupees" → {{"keywords": "", "category": null, "max_price": 60, "min_price": 40, "min_stock": null, "max_stock": null, "expiry_days": null}}
- "milk" → {{"keywords": "milk", "category": "Dairy", "max_price": null, "min_price": null, "min_stock": null, "max_stock": null, "expiry_days": null}}
- "Milma Full Cream Milk" → {{"keywords": "Milma Full Cream Milk", "category": "Dairy", "max_price": null, "min_price": null, "min_stock": null, "max_stock": null, "expiry_days": null}}
- "snacks under 30" → {{"keywords": "snacks biscuit chips", "category": "Snacks", "max_price": 30, "min_price": null, "min_stock": null, "max_stock": null, "expiry_days": null}}
- "dairy products" → {{"keywords": "milk curd butter cheese", "category": "Dairy", "max_price": null, "min_price": null, "min_stock": null, "max_stock": null, "expiry_days": null}}
- "cooking oil" → {{"keywords": "cooking oil sunflower", "category": "Oils", "max_price": null, "min_price": null, "min_stock": null, "max_stock": null, "expiry_days": null}}
- "milk stock more than 100" → {{"keywords": "milk", "category": "Dairy", "max_price": null, "min_price": null, "min_stock": 100, "max_stock": null, "expiry_days": null}}
- "stock less than 50" → {{"keywords": "", "category": null, "max_price": null, "min_price": null, "min_stock": null, "max_stock": 50, "expiry_days": null}}
- "price between 20 and 100" → {{"keywords": "", "category": null, "max_price": 100, "min_price": 20, "min_stock": null, "max_stock": null, "expiry_days": null}}
- "biscuits expiring soon" → {{"keywords": "biscuits cookies", "category": "Snacks", "max_price": null, "min_price": null, "min_stock": null, "max_stock": null, "expiry_days": 7}}
- "fresh milk" → {{"keywords": "milk", "category": "Dairy", "max_price": null, "min_price": null, "min_stock": null, "max_stock": null, "expiry_days": 30}}
- "expiring today" → {{"keywords": "", "category": null, "max_price": null, "min_price": null, "min_stock": null, "max_stock": null, "expiry_days": 1}}
- "Good Day cashew biscuit" → {{"keywords": "Good Day cashew biscuit", "category": "Snacks", "max_price": null, "min_price": null, "min_stock": null, "max_stock": null, "expiry_days": null}}
- "biscut" → {{"keywords": "biscuit cookies", "category": "Snacks", "max_price": null, "min_price": null, "min_stock": null, "max_stock": null, "expiry_days": null}}
- "healthy morning drink" → {{"keywords": "milk tea coffee beverage", "category": "Beverages", "max_price": null, "min_price": null, "min_stock": null, "max_stock": null, "expiry_days": null}}
- "something sweet" → {{"keywords": "chocolate candy sweet biscuit", "category": "Snacks", "max_price": null, "min_price": null, "min_stock": null, "max_stock": null, "expiry_days": null}}
- "best oil for cooking" → {{"keywords": "cooking oil sunflower coconut", "category": "Oils", "max_price": null, "min_price": null, "min_stock": null, "max_stock": null, "expiry_days": null}}"""

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    content = res.choices[0].message.content.strip()

    if content.startswith("```"):
        content = content.split("```")[1]
        if content.startswith("json"):
            content = content[4:]
        content = content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "keywords": query.strip(),
            "category": None,
            "max_price": None,
            "min_price": None,
            "min_stock": None,
            "max_stock": None,
            "expiry_days": None
        }