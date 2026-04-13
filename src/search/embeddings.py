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
    api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/sentence-transformers/all-MiniLM-L6-v2"
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN', '')}"}
    
    response = httpx.post(api_url, json={"inputs": text}, timeout=30)
    result = response.json()
    
    if isinstance(result, list) and isinstance(result[0], list):
        return result[0]
    return result