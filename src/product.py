from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Productmodel(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    category: str
    mrp: float
    selling_price: float
    expiry_date: str
    stock: int
    product_imge_url: str
    # is_added: bool = False
    is_bought: bool
    is_wishlist: bool
    created_at: Optional[datetime] = None


from typing import Optional
from pydantic import BaseModel

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    mrp: Optional[float] = None
    selling_price: Optional[float] = None
    expiry_date: Optional[str] = None
    stock: Optional[int] = None
    product_imge_url: Optional[str] = None
    is_added: Optional[bool] = None
    is_bought: Optional[bool] = None
    is_wishlist: Optional[bool] = None