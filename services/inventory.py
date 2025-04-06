# Check stock
def check_stock(product_id: str, warehouse: Warehouse) -> int:
    stock = session.get(Stock, (product_id, warehouse))
    return stock.quantity if stock else 0

# Deduct stock
def update_stock(product_id: str, warehouse: Warehouse, quantity: int):
    stock = session.get(Stock, (product_id, warehouse)) or Stock(
        product_id=product_id, 
        warehouse=warehouse, 
        quantity=0
    )
    stock.quantity -= quantity
    session.add(stock)