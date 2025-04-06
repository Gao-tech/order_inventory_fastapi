from fastapi import FastAPI


@app.post("/orders")
async def create_order(order_data: OrderCreate, user: User = Depends(get_current_user)):
    # 1. Find nearest warehouse with stock
    warehouse = get_nearest_warehouse(order_data.zipcode)
    
    # 2. Check stock for all items
    for item in order_data.items:
        if check_stock(item.product_id, warehouse) < item.quantity:
            raise HTTPException(400, f"Out of stock for {item.product_id}")
    
    # 3. Create order record
    order = Order(
        user_id=user.id,
        delivery_method=order_data.delivery_method,
        zipcode=order_data.zipcode
    )
    
    # 4. Deduct stock
    for item in order_data.items:
        update_stock(item.product_id, warehouse, item.quantity)
    
    return order