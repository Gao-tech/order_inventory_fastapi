from fastapi import FastAPI, APIRouter, Path, Query, Response, status, HTTPException, Depends
from sqlalchemy import delete, func
from ..models import Product, StockOut, User, Warehouse, Stock, ProductWithStockOut
from sqlmodel import Session, select
from typing import Annotated
from ..db import get_session
from ..oauth2 import get_admin
from sqlalchemy.orm import selectinload


router = APIRouter(tags=['Products']) 


@router.get('/products', response_model=list[Product])
async def get_products(session: Session=Depends(get_session)) ->list[Product]:
    products = session.exec(select(Product)).all()
    return products


@router.get('/products/{product_id}',response_model=ProductWithStockOut)
async def get_product_id(product_id: Annotated[str, Path(title="IKEA article number")],
                         session: Session=Depends(get_session)) -> ProductWithStockOut:
 
    product = session.exec(select(Product).where(Product.id==product_id)
                           .options(selectinload(Product.stock).selectinload(Stock.warehouse))).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The product with id {product_id} is not found")

    return ProductWithStockOut(
        id=product.id,
        name=product.name,
        category=product.category,
        price=product.price,
        series=product.series,
        stock=[StockOut(
            warehouse_id=stock.warehouse_id,
            quantity=stock.quantity
        )
        for stock in product.stock
        ]
    )

  
#only loggin admin can post product:  haven't added
@router.post('/products', status_code=status.HTTP_201_CREATED, response_model=ProductWithStockOut)
async def create_product(
    product_data: ProductWithStockOut,
    session: Session = Depends(get_session)
) -> ProductWithStockOut:
    
    # Check for existing product
    existing_product = session.exec(select(Product).where(Product.id == product_data.id)).first()
    if existing_product:
        raise HTTPException(status_code=400, detail="Product already exists, please update it")

    # Create Product
    new_product = Product(
        id=product_data.id,
        name=product_data.name,
        category=product_data.category,
        price=product_data.price,
        series=product_data.series
    )
    session.add(new_product)
    
    # Create Stock entries
    for stock_item in product_data.stock:
        stock = Stock(
            product_id=product_data.id,
            warehouse_id=stock_item.warehouse_id,
            quantity=stock_item.quantity
        )
        session.add(stock)
    
    session.commit()
    session.refresh(new_product)
    
    return new_product


#only loggin admin can update product:  haven't done
@router.put('products/{product_id}')
async def update_product_stock():
    pass

#only loggin admin can delete product:  haven't done
@router.delete('product/{product_id}')
async def delete_product():
    pass


