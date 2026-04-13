# from sentence_transformers import SentenceTransformer

# model = SentenceTransformer("all-MiniLM-L6-v2")

# def get_embedding(text: str):
#     return model.encode(text).tolist()


# from sentence_transformers import SentenceTransformer

# model = None  # ✅ don't load at startup

# def get_model():
#     global model
#     if model is None:
#         print("⏳ Loading embedding model...", flush=True)
#         model = SentenceTransformer("all-MiniLM-L6-v2")
#         print("✅ Embedding model loaded!", flush=True)
#     return model

# def get_embedding(text: str):
#     return get_model().encode(text).tolist()  # ✅ loads only when first search is made


import os
import httpx


def get_embedding(text: str) -> list:
    token = os.getenv('HF_TOKEN', '')
    print(f"HF_TOKEN length: {len(token)}", flush=True)
    print(f"HF_TOKEN starts with: {token[:10]}", flush=True)
    
    api_url = "https://router.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = httpx.post(api_url, json={"inputs": text}, headers=headers, timeout=30)
    
    print(f"HF Status: {response.status_code}", flush=True)
    
    if response.status_code != 200:
        raise Exception(f"HuggingFace API error {response.status_code}: {response.text[:100]}")
    
    result = response.json()
    
    if isinstance(result, list) and len(result) > 0:
        if isinstance(result[0], list):
            return result[0]
        return result
    
    raise Exception(f"Unexpected response format: {result}")