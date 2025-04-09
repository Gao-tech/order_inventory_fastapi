import datetime
from enum import Enum
import re
from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr, field_validator
from pydantic.types import conint
from sqlalchemy import JSON, UUID, Column, Index
from sqlmodel import Field, SQLModel, Relationship


class Warehouse(str, Enum):
    MALMO = "Malmö (55.6094, 12.9847)"
    HELSINGBORG = "Helsingborg (56.0465, 12.6945)"
    ALMHULT = "Älmhult (56.5517, 14.1580)"

class Category(str, Enum):
    BEDS_MATTRESSES = "Beds & Mattresses"
    SOFAS_ARMCHAIRS = "Sofas & Armchairs"
    DINING_FURNITURE = "Dining Furniture"
    TEXTILES = "Textiles"


class Series(str, Enum):
    SABOVIK = "säbövik"
    VIMLE = "vimle"
    SKANSNAS = "skansnäs"

class WarehouseAddress(str, Enum):
    HOVDINGEVAGEN = "Hövdingevägen (55.55225871167352, 12.985213183922493)"    # Malmö
    MARKNADSVAGEN = "Marknadsvägen (56.092430690778045, 12.76271609744993)"    # Helsingbor
    HANDELSVAGEN = "Handelsvägen （56.55169461274043, 14.157970024464651）"  # Älmhult

class Warehouse(SQLModel, table=True):
    warehouse_id: str = Field(primary_key=True)  # Renamed from "id"
    name: str
    allows_self_service: bool = False
    served_zipcodes: list[str] = Field(default=[], sa_column=Column(JSON))
    stocks: list["Stock"] = Relationship(back_populates="warehouse")

class WarehouseCreate(SQLModel):
    warehouse_id: str
    name: str
    allows_self_service: bool
    served_zipcodes: list[str]
    
class WarehouseRead(SQLModel):
    id: Optional[str] = None
    name: str
    allows_self_service: bool
    served_zipcodes: list[str]

    class Config:  # SQLModel/Pydantic v1 syntax
        orm_mode = True  # Critical for ORM->Pydantic conversion

class Stock(SQLModel, table=True):
    product_id: str = Field(foreign_key="product.id", primary_key=True)
    warehouse_id: str = Field(foreign_key="warehouse.warehouse_id", primary_key=True)
    quantity: int = Field(default=0)
    product: Optional['Product'] = Relationship(back_populates="stock")
    warehouse: Optional[Warehouse] = Relationship(back_populates="stocks")  # Correct back-populates

class Product(SQLModel, table=True):
    id: str = Field(primary_key=True, description="IKEA article number")  # 40309870
    name: str
    category: Category
    price: float
    series: Optional[Series] = None
    stock: list['Stock'] = Relationship(back_populates="product")
    order_items: Optional['OrderItem'] = Relationship(back_populates="product") # lookup: which orders contain this product

class StockOut(SQLModel):  # show on the website
    warehouse_id: str
    quantity: int

class ProductWithStockOut(SQLModel):
    id: str
    name: str
    category: Category
    price: float
    series: Optional[Series]
    stock: list[StockOut]

class DeliveryMethod(str, Enum):
    SELF_PICKUP = "self_pickup"      # 50 SEK (fixed)
    CURBSIDE = "curbside"            # 400 SEK (fixed)
    INDOOR_DELIVERY = "indoor"       # 800 SEK (fixed)

class Zipcode(str, Enum): # zip code within the range of deliver,here three are all in Malmö 21109 = "55.6094° N, 12.9847° E"
    zipcode: int
    longitude: int      # "55.6015° N, 13.0315° E"
    latitude: int       #"55.5656° N, 13.0443° E"

class UserBase(SQLModel):
    fname: str = Field(nullable=False, min_length=1, max_length=50)
    lname: str = Field(nullable=False, min_length=1, max_length=50)
    email: EmailStr = Field(unique=True)
    
    @field_validator("fname", "lname", mode="before")
    def validate_name(cls, value):
        if not re.match(r"[A-Za-z]", value):
            raise ValueError("Name can only contain letters")
        return value.title()  # Auto-format to title case
    
class UserCreate(UserBase):
    password: str = Field(nullable=False)

class UserShow(UserBase):
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))

class User(UserBase, table=True): # reserved when querying, use "user"
    id: int = Field(default=None, primary_key=True)
    password: str = Field(nullable=False)
    role: str = Field(default="user")

    
class Order(SQLModel, table=True):
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_zipcode: str
    delivery_method: DeliveryMethod
    cost: int
    total_price: float  # Total product costs
    created_at: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    arrival_date: datetime.datetime
    warehouse_id: Optional[str]
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", nullable=True)
    items: list["OrderItem"] = Relationship(back_populates="order")

    class Config:
        arbitrary_types_allowed = True

class OrderItem(SQLModel, table=True):
    order_id: str = Field(foreign_key="order.uuid", primary_key=True)
    product_id: str = Field(foreign_key="product.id", primary_key=True)
    quantity: int
    price_at_order: float

    order: Optional[Order] = Relationship(back_populates="items")
    product: Optional[Product] = Relationship(back_populates="order_items")
    
    class Config:
        arbitrary_types_allowed = True

class OrderItemCreate(SQLModel):
    product_id: str
    quantity: int

class OrderCreate(SQLModel):
    user_zipcode: str
    delivery_method: DeliveryMethod
    warehouse_id: str
    items: list[OrderItem]

class OrderOut(SQLModel): # Response model
    uuid: str
    user_zipcode: str
    delivery_method: DeliveryMethod
    cost: int
    total_price: float
    created_at: datetime.datetime
    arrival_date: datetime.datetime
    warehouse_id: Optional[str]
    items: list[OrderItemCreate]
    class Config:
       orm_mode = True

class UserLogin(SQLModel):
    email: EmailStr
    password: str

class Token(SQLModel):
    access_token : str
    token_type: str

class TokenData(BaseModel):
    id: int | None = None
