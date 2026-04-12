

# main.py
from fastapi import FastAPI, Depends, UploadFile, File,Form,HTTPException
from sqlalchemy.orm import Session
from src.db_core.db import Base, engine, get_db
from src import crud
from src.search import search

from src.product import Productmodel
from src.image_uplod.image_upload import upload_image
from src.db_core.model import Productmodeldb

Base.metadata.create_all(bind=engine)

app = FastAPI()

# ➕ CREATE PRODUCT

# @app.post("/add_new_products", response_model=Productmodel)
# def create_product(data: Productmodel, db: Session = Depends(get_db)):
#     return crud.create_product(db, data)
from fastapi import UploadFile, File, Form

from src.category.auto_category import detect_category

# @app.post("/add_new_products", response_model=None)
# def create_product(
#     name: str = Form(...),
#     description: str = Form(...),
#     category: str = Form(None),  # Now optional!
#     mrp: float = Form(...),
#     selling_price: float = Form(...),
#     expiry_date: str = Form(...),
#     stock: int = Form(...),
#     image: UploadFile = File(...),
#     db: Session = Depends(get_db)
# ):
#     # Auto detect category if not provided
#     if not category or category.strip() == "":
#         category = detect_category(name, description)

#     upload_result = upload_image(file=image)
#     image_url = upload_result["url"]

#     return crud.create_product(
#         db, name, description, category,
#         mrp, selling_price, expiry_date, stock, image_url
#     )

# from sqlalchemy.orm import Session
# from fastapi import Depends, Form, File, UploadFile
# from src.db_core.db import get_db
# import crud

@app.post("/add_new_products")
def create_product(
    name: str = Form(...),
    description: str = Form(...),
    category: str = Form(None),
    mrp: float = Form(...),
    selling_price: float = Form(...),
    expiry_date: str = Form(...),
    stock: int = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Auto detect category if not provided
    if not category or category.strip() == "":
        category = detect_category(name, description)

    upload_result = upload_image(file=image)
    image_url = upload_result["url"]

    product = crud.create_product(
        db, name, description, category,
        mrp, selling_price, expiry_date, stock, image_url
    )
    
    # ✅ Return product data WITHOUT embedding
    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "category": product.category,
        "mrp": product.mrp,
        "selling_price": product.selling_price,
        "expiry_date": product.expiry_date,
        "stock": product.stock,
        "product_imge_url": product.product_imge_url,
        "is_bought": product.is_bought,
        "is_wishlist": product.is_wishlist,
        "created_at": product.created_at,
        # ❌ embedding is NOT included here (but still saved in DB!)
    }
# 📦 GET ALL


@app.get("/get_all_products")
def get_all_products(db: Session = Depends(get_db)):
    products = db.query(Productmodeldb).all()
    return {
        "message": "all products fetched",
        "products": [
            {k: v for k, v in p.__dict__.items() 
             if k != "embedding" and not k.startswith("_")}
            for p in products
        ]
    }

@app.get("/get_one_product/{id}")
def get_product(id: int, db: Session = Depends(get_db)):
    product = db.query(Productmodeldb).filter(Productmodeldb.id == id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return {
        "message": "product fetched",
        "product": {k: v for k, v in product.__dict__.items() 
                    if k != "embedding" and not k.startswith("_")}
    }

@app.put("/update_product/{id}")
def update_product(
    id: int,
    name: str = Form(None),
    description: str = Form(None),
    category: str = Form(None),
    mrp: float = Form(None),
    selling_price: float = Form(None),
    expiry_date: str = Form(None),
    stock: int = Form(None),
    image: UploadFile = File(None),  # Optional image
    db: Session = Depends(get_db)
):
    product = db.query(Productmodeldb).filter(Productmodeldb.id == id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update only fields that are provided
    if name: product.name = name
    if description: product.description = description
    if category: product.category = category
    if mrp: product.mrp = mrp
    if selling_price: product.selling_price = selling_price
    if expiry_date: product.expiry_date = expiry_date
    if stock: product.stock = stock

    # Upload new image only if provided
    if image:
        upload_result = upload_image(file=image)
        product.product_imge_url = upload_result["url"]

    db.commit()
    db.refresh(product)

    return {
        "message": "product updated",
        "product": {k: v for k, v in product.__dict__.items()
                    if k != "embedding" and not k.startswith("_")}
    }

@app.delete("/delete_product/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Productmodeldb).filter(Productmodeldb.id == product_id).first()
    if not product:
        return {"message": "product not found"}
    db.delete(product)
    db.commit()
    return {"status": "product deleted successfully"}




# ❤️ WISHLIST
@app.post("/wishlist/{id}")
def wishlist(id: int, db: Session = Depends(get_db)):
    return crud.toggle_wishlist(db, id)

# 🛒 BUY
@app.post("/buy/{id}")
def buy(id: int, db: Session = Depends(get_db)):
    return crud.buy_product(db, id)

# 🔍 SEARCH
@app.get("/search")
def search_api(q: str, db: Session = Depends(get_db)):
    results = search.search_products(db, q)

    return [
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