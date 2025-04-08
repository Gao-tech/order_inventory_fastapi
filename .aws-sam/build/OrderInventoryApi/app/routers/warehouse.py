from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlmodel import Session
from app.models import Warehouse, WarehouseCreate, WarehouseRead
from app.db import get_session


router = APIRouter(tags=["Warehouses"])

@router.post("/warehouses/init", response_model=list[WarehouseRead])
async def init_warehouse(warehouses_data: list[WarehouseCreate],  # Accept list of warehouses
                        session: Session = Depends(get_session)
):
    created_warehouses = []

    for wh_data in warehouses_data:
        # Check if warehouse exists
        existing = session.exec(
            select(Warehouse).where(Warehouse.warehouse_id == wh_data.warehouse_id)
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Warehouse exists.")
        
        if not existing:
            new_wh = Warehouse(
                warehouse_id=wh_data.warehouse_id,
                name=wh_data.name,
                allows_self_service=wh_data.allows_self_service,
                served_zipcodes=wh_data.served_zipcodes
            )
            session.add(new_wh)
            created_warehouses.append(new_wh)
    
    session.commit()
    
    # Refresh and return created warehouses
    for wh in created_warehouses:
        session.refresh(wh)
    
    return created_warehouses
