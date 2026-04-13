# main.py
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

# 🔍 Debug logging (helps see what's happening on Render)
print(f"🐍 Python: {sys.version}", flush=True)
print(f"📁 CWD: {os.getcwd()}", flush=True)
print(f"🔑 DATABASE_URL in env: {'DATABASE_URL' in os.environ}", flush=True)

# ✅ Lifespan: Run setup on startup, cleanup on shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events"""
    try:
        # Import here to avoid circular imports at module level
        from src.db_core.db import engine, Base
        
        print("🔌 Connecting to database...", flush=True)
        
        # Enable pgvector extension (safe to run multiple times)
        with engine.connect() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
            conn.commit()
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables ready!", flush=True)
        
    except Exception as e:
        print(f"⚠️ Database setup warning: {e}", flush=True)
        # Don't crash the app - let it start anyway
    
    yield  # ✅ App is now running and handling requests
    
    # Shutdown cleanup (if needed)
    print("👋 Shutting down...", flush=True)

# ✅ Create FastAPI app with lifespan
app = FastAPI(
    title="Piko Backend API",
    description="E-commerce backend with vector search",
    version="1.0.0",
    lifespan=lifespan
)

# ============================================================================
# IMPORTS (after app creation to avoid circular import issues)
# ============================================================================
from src.db_core.db import get_db
from src import crud
from src.search import search
from src.product import Productmodel
from src.image_uplod.image_upload import upload_image
from src.db_core.model import Productmodeldb
from src.category.auto_category import detect_category

# ============================================================================
# HEALTH CHECK (for Render monitoring)
# ============================================================================
@app.get("/health")
def health_check():
    """Simple endpoint to verify API is running"""
    return {
        "status": "ok",
        "message": "Piko Backend API is running!",
        "environment": os.getenv("RENDER", "local")
    }

# ============================================================================
# ➕ CREATE PRODUCT
# ============================================================================
@app.post("/add_new_products")
def create_product(
    name: str = Form(...),
    description: str = Form(...),
    category: str = Form(None),
    quantity:str =Form(...),
    mrp: float = Form(...),
    selling_price: float = Form(...),
    expiry_date: str = Form(...),
    stock: int = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Add a new product with image upload and auto-category detection"""
    
    # Auto detect category if not provided
    if not category or category.strip() == "":
        category = detect_category(name, description)

    # Upload image to Cloudinary
    upload_result = upload_image(file=image)
    image_url = upload_result["url"]

    # Create product in database
    product = crud.create_product(
        db, name, description, category,
        mrp,quantity, selling_price, expiry_date, stock, image_url
    )
    
    # Return product data WITHOUT embedding (clean response)
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "category": product.category,
        "quantity":product.quantity,
        "mrp": product.mrp,
        "selling_price": product.selling_price,
        "expiry_date": product.expiry_date,
        "stock": product.stock,
        "product_imge_url": product.product_imge_url,
        "is_bought": product.is_bought,
        "is_wishlist": product.is_wishlist,
        "created_at": product.created_at,
        # ❌ embedding excluded from response (but saved in DB!)
    }

# ============================================================================
# 📦 GET ALL PRODUCTS
# ============================================================================
@app.get("/get_all_products")
def get_all_products(db: Session = Depends(get_db)):
    """Fetch all products (excluding embeddings)"""
    products = db.query(Productmodeldb).all()
    return {
        "message": "all products fetched",
        "count": len(products),
        "products": [
            {k: v for k, v in p.__dict__.items() 
             if k != "embedding" and not k.startswith("_")}
            for p in products
        ]
    }

# ============================================================================
# 📦 GET ONE PRODUCT
# ============================================================================
@app.get("/get_one_product/{id}")
def get_product(id: int, db: Session = Depends(get_db)):
    """Fetch a single product by ID"""
    product = db.query(Productmodeldb).filter(Productmodeldb.id == id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "message": "product fetched",
        "product": {k: v for k, v in product.__dict__.items() 
                    if k != "embedding" and not k.startswith("_")}
    }

# ============================================================================
# ✏️ UPDATE PRODUCT
# ============================================================================
@app.put("/update_product/{id}")
def update_product(
    id: int,
    name: str = Form(None),
    description: str = Form(None),
    category: str = Form(None),
    quantity:str=Form(...),
    mrp: float = Form(None),
    selling_price: float = Form(None),
    expiry_date: str = Form(None),
    stock: int = Form(None),
    image: UploadFile = File(None),  # Optional image
    db: Session = Depends(get_db)
):
    """Update product fields (only provided fields are updated)"""
    product = db.query(Productmodeldb).filter(Productmodeldb.id == id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update only fields that are provided (not None)
    if name is not None: product.name = name
    if description is not None: product.description = description
    if category is not None: product.category = category
    if mrp is not None: product.mrp = mrp
    if quantity is not None: product.quantity = quantity
    if selling_price is not None: product.selling_price = selling_price
    if expiry_date is not None: product.expiry_date = expiry_date
    if stock is not None: product.stock = stock

    # Upload new image only if provided
    if image and image.filename:
        upload_result = upload_image(file=image)
        product.product_imge_url = upload_result["url"]

    db.commit()
    db.refresh(product)

    return {
        "message": "product updated",
        "product": {k: v for k, v in product.__dict__.items()
                    if k != "embedding" and not k.startswith("_")}
    }

# ============================================================================
# 🗑️ DELETE PRODUCT
# ============================================================================
@app.delete("/delete_product/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product by ID"""
    product = db.query(Productmodeldb).filter(Productmodeldb.id == product_id).first()
    
    if not product:
        return {"message": "product not found", "status": "error"}
    
    db.delete(product)
    db.commit()
    return {"message": "product deleted successfully", "status": "success"}

# ============================================================================
# ❤️ WISHLIST TOGGLE
# ============================================================================
@app.post("/wishlist/{id}")
def wishlist(id: int, db: Session = Depends(get_db)):
    """Toggle product wishlist status"""
    return crud.toggle_wishlist(db, id)

# ============================================================================
# 🛒 BUY PRODUCT
# ============================================================================
@app.post("/buy/{id}")
def buy(id: int, db: Session = Depends(get_db)):
    """Mark product as bought"""
    return crud.buy_product(db, id)

# ============================================================================
# 🔍 VECTOR SEARCH
# ============================================================================
@app.get("/search")
def search_api(q: str, db: Session = Depends(get_db)):
    """Semantic search using vector embeddings"""
    if not q or not q.strip():
        return {"error": "Query parameter 'q' is required"}
        
    results = search.search_products(db, q)

    return {
        "query": q,
        "count": len(results),
        "results": [
            {
                "name": r["name"],
                "description": r["description"],
                "category": r["category"],
                "stock": r["stock"],
                "price": r["selling_price"],
                "expiry": r["expiry_date"],
                "image": r["product_imge_url"]
            }
            for r in results
        ]
    }

# ============================================================================
# ROOT ENDPOINT
# ============================================================================
@app.get("/")
def root():
    """API root - shows available endpoints"""
    return {
        "message": "Welcome to Piko Backend API",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "POST /add_new_products": "Add a new product",
            "GET /get_all_products": "List all products",
            "GET /get_one_product/{id}": "Get product by ID",
            "PUT /update_product/{id}": "Update product",
            "DELETE /delete_product/{id}": "Delete product",
            "POST /wishlist/{id}": "Toggle wishlist",
            "POST /buy/{id}": "Mark as bought",
            "GET /search?q=...": "Semantic search"
        }
    }