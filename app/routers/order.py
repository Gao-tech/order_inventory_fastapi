import datetime
from fastapi import FastAPI, APIRouter, Path, Query, Response, status, HTTPException, Depends
# from sqlalchemy import delete, func
from ..models import DeliveryMethod, Order, OrderCreate, OrderItem, OrderOut, Stock, User, Product
from sqlmodel import Session, select
from typing import Annotated, Optional
from ..db import get_session
from ..oauth2 import get_current_user
from sqlalchemy.orm import selectinload

router = APIRouter(tags=['Order']) 

#centralized delivery from the same region and loggin user to make order is optional
def calculate_arrival_date(created_at: datetime.datetime) -> datetime:
    return created_at + datetime.timedelta(days=3)

@router.post("/orders", response_model=OrderOut)
def create_order(order_data: OrderCreate,
                 current_user: Optional[User] = Depends(get_current_user),
                 session: Session = Depends(get_session)) -> Order:
    


    # Calculate total product price
    total = 0.0
    items_to_save = []
    
    for item in order_data.items:
        # Get product price
        product = session.get(Product, item.product_id)
        if not product:
            raise HTTPException(404, f"Product {item.product_id} not found")
    
    # Search item in stock
        stock = session.exec(
            select(Stock).where(
                (Stock.product_id == item.product_id) & 
                (Stock.warehouse_id == order_data.warehouse_id))).first()
    
        if not stock or stock.quantity < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for product {item.product_id} in warehouse {order_data.warehouse_id}")
        
        total += product.price * item.quantity
        items_to_save.append(item)

    def calculate_cost(method: DeliveryMethod) -> int:
        match method:
            case DeliveryMethod.SELF_PICKUP:
                return 50
            case DeliveryMethod.CURBSIDE:
                return 400
            case DeliveryMethod.INDOOR_DELIVERY:
                return 800

    # Generate timestamps
    created_at = datetime.datetime.now()  # Local naive datetime
    arrival_date = calculate_arrival_date(created_at)  # Pass created_at explicitly

    # Create order with timestamps
    new_order = Order(
        user_zipcode=order_data.user_zipcode,
        delivery_method=order_data.delivery_method,
        cost=calculate_cost(order_data.delivery_method),
        total_price=total,
        created_at=created_at,  # Add this field
        arrival_date=arrival_date,
        warehouse_id=order_data.warehouse_id,
        user_id=current_user.id if current_user else None  #make guest user and login user both can make order
    )
    session.add(new_order)
    session.flush()  # Ensure the new_order.uuid is generated and persisted in DB

    # Create order items
    for item in order_data.items:
        order_item = OrderItem(
            order_id=new_order.uuid,  
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_order=product.price
        )
        session.add(order_item)    

    # Reduce stock quantities
    for item in order_data.items:
        stock = session.exec(
            select(Stock).where(
                (Stock.product_id == item.product_id) & 
                (Stock.warehouse_id == order_data.warehouse_id)
            )
        ).first()
        if stock:
            stock.quantity -= item.quantity
            session.add(stock)

    session.commit() 
    return new_order


#login user get all its own orders
@router.get("/orders", response_model=list[OrderOut])
def create_order(
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_current_user)  # Optional dependency
):
    orders = session.exec(select(Order).where(Order.user_id == current_user.id)).all()
    
    if not orders:
        raise HTTPException(status_code=404, detail="No orders found")
    
    return orders