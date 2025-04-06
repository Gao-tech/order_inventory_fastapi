import datetime
from enum import Enum
import re
from typing import Annotated, Optional
import uuid
from pydantic import BaseModel, EmailStr, field_validator, model_validator
from pydantic.types import conint
from sqlalchemy import JSON, UUID, Column, Index
from sqlmodel import Field, SQLModel, Relationship
from geopy.distance import geodesic
from pydantic.types import conint

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
    SABOVIK = "SÄBÖVIK"
    VIMLE = "VIMLE"
    SKANSNAS = "SKANSNÄS"

class WarehouseAddress(int, Enum):
    HOVDINGEVAGEN = "Hövdingevägen (55.55225871167352, 12.985213183922493)"    # Malmö
    MARKNADSVAGEN = "Marknadsvägen (56.092430690778045, 12.76271609744993)"    # Helsingbor
    HANDELSVAGEN = "Handelsvägen （56.55169461274043, 14.157970024464651）"  # Älmhult

class Warehouse(SQLModel, table=True):
    id: str = Field(primary_key=True)  # e.g., "malmo", "helsingborg"
    name: str
    allows_self_service: bool = False  # Can users pick up here?
    served_zipcodes: list[str] = Field(default=[], sa_column=Column(JSON))  # ["21109", "21216"]

class Stock(SQLModel, table=True):
    product_id: str = Field(foreign_key="product.id", primary_key=True)
    quantity: int = Field(default=0)
    warehouse_id: str = Field(foreign_key="warehouse.id", primary_key=True)

    warehouse: Optional[Warehouse] = Relationship()  # Composite primary key
    product: Optional['Product'] = Relationship(back_populates="stock")

class Product(SQLModel, table=True):
    id: str = Field(primary_key=True, description="IKEA article number")  # 40309870
    name: str
    category: Category
    price: float
    series: Optional[Series] = None

    stock: list['Stock'] = Relationship(back_populates="product")

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

class ShippingRule(SQLModel, table=True):
    from_warehouse: Warehouse = Field(primary_key=True)
    to_zipcode_group: str = Field(primary_key=True)  # "Malmö", "Helsingborg", "Älmhult"
    cost: int


class Order(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_zipcode: str
    delivery_method: DeliveryMethod
    cost: int  # 50, 400, or 800
    created_at: datetime = Field(default_factory=datetime.now)
    arrival_date: datetime
    items: list["OrderItem"] = Relationship(back_populates="order")
    

class OrderItem(SQLModel, table=True):
    order_id: UUID = Field(foreign_key="order.id", primary_key=True)
    product_id: str = Field(foreign_key="product.id", primary_key=True)
    quantity: int
    # Relationships
    order: Optional[Order] = Relationship(back_populates="items")