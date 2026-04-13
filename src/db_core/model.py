from sqlalchemy import Column,Integer,String,Float,DATE,Boolean,TIMESTAMP
from src.db_core.db import Base
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector  
class Productmodeldb(Base):
    __tablename__="products"
    id=Column(Integer,primary_key=True,index=True)
    name=Column(String)
    description=Column(String)
    quantity=Column(String)
    brand = Column(String, nullable=True)
    category=Column(String)
    mrp=Column(Float)
    selling_price=Column(Float)
    expiry_date=Column(String)
    stock=Column(Integer)
    product_imge_url=Column(String)
    is_bought = Column(Boolean, default=False)
    is_wishlist = Column(Boolean, default=False)
    created_at=Column(TIMESTAMP,server_default=func.now())
    embedding = Column(Vector(384))