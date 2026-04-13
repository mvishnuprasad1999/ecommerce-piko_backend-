from src.search.embeddings import get_embedding
from src.db_core.model import Productmodeldb


from src.search.embeddings import get_embedding
from src.db_core.model import Productmodeldb


# ➕ CREATE PRODUCT

# def create_product(db, data):
#     text = f"{data.name} {data.description} {data.category}"
#     embedding = get_embedding(text)

#     product = Productmodeldb(
#         **data.dict(exclude={"id", "created_at"}),
#         embedding=embedding
#     )

#     db.add(product)
#     db.commit()
#     db.refresh(product)

#     return product

def create_product(db, name, description, category, mrp,quantity, selling_price, expiry_date, stock, image_url):
    text = f"{name} {description} {category}"
    embedding = get_embedding(text)

    product = Productmodeldb(
        name=name,
        description=description,
        category=category,
        quantity=quantity,
        mrp=mrp,
        selling_price=selling_price,
        expiry_date=expiry_date,
        stock=stock,
        product_imge_url=image_url,
        embedding=embedding
    )

    db.add(product)
    db.commit()
    db.refresh(product)
    return product

# ❤️ TOGGLE WISHLIST
def toggle_wishlist(db, id):
    product = db.query(Productmodeldb).get(id)

    if not product:
        return {"error": "Product not found"}

    product.is_wishlist = not product.is_wishlist

    db.commit()
    db.refresh(product)

    return product


# 🛒 BUY PRODUCT
def buy_product(db, id):
    product = db.query(Productmodeldb).get(id)

    if not product:
        return {"error": "Product not found"}

    if product.stock <= 0:   # ✅ fixed (was quantity ❌)
        return {"error": "Out of stock"}

    product.stock -= 1       # ✅ fixed

    if product.stock == 0:
        product.is_bought = True

    db.commit()
    db.refresh(product)

    return product