from fastapi import FastAPI, APIRouter, Path, Query, Response, status, HTTPException, Depends
from sqlalchemy import delete, func
from ..models import Product, StockOut, Warehouse, Stock, ProductWithStockOut
from sqlmodel import Session, select
from typing import Annotated
from ..db import get_session
from ..oauth2 import get_current_user
from sqlalchemy.orm import selectinload


router = APIRouter(tags=['Products']) 

@router.get('/products', response_model=list[Product])
async def get_products(session: Session=Depends(get_session)) ->list[Product]:
    products = session.exec(select(Product)).all()
    return products



@router.get('/products/{product_id}',response_model=ProductWithStockOut)
async def get_product_id(product_id: Annotated[int, Path(title="IKEA article number")],
                         session: Session=Depends(get_session)) -> ProductWithStockOut:
 
    product = session.exec(select(Product).where(Product.id==product.id).options(selectinload(Product.stock).selectinload(Stock.warehouse))).first
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The product with id {product_id} is not found")

    return ProductWithStockOut(
        id=product.id,
        name=product.name,
        category=product.category,
        price=product.price,
        series=product.series,
        stock=[StockOut(
            warehouse_id=Stock.warehouse_id,
            quantity=Stock.quantity
        )
        for stock in product.stock
        ]
    )
  

@router.post('/posducts')
async def add_new_products():
    pass

@router.put('products/{id}')
async def update_product_stock():
    pass

@router.delete('product/{id}')
async def delete_product():
    pass