from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def detect_category(name: str, description: str) -> str:
    prompt = f"""You are a grocery store product categorizer.
Given a product name and description, return ONLY the category name, nothing else.

Product Name: "{name}"
Description: "{description}"

Return ONE category from this list only:
Dairy, Snacks, Beverages, Grains, Oils, Personal Care, Vegetables, Fruits, Frozen Foods, Bakery, Meat, Seafood, Condiments, Cleaning, Baby Care, Pet Care, Stationery, Electronics, Medicines, Other

Return ONLY the category name, no explanation, no punctuation."""

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    category = res.choices[0].message.content.strip()
    print(f"Auto category detected: {category}")
    return category