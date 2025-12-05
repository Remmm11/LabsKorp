from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
from database import SessionLocal

router = APIRouter(prefix="/customer_order", tags=["Элементы заказа (customer_order)"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.CustomerOrder, status_code=status.HTTP_201_CREATED)
def create_customer_order(customer_order: schemas.CustomerOrderCreate, db: Session = Depends(get_db)):

    return crud.create_customer_order(db=db, customer_order=customer_order)

@router.get("/{order_id}", response_model=schemas.CustomerOrder)
def read_customer_order(order_id: int, db: Session = Depends(get_db)):

    db_customer_order = crud.get_customer_order(db, order_id=order_id)

    if db_customer_order is None:
        raise HTTPException(status_code=404, detail="CustomerOrder not found")

    return db_customer_order

@router.get("/", response_model=List[schemas.CustomerOrder])
def read_customer_order(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):

    customer_order = crud.get_customer_orders(db, skip=skip, limit=limit)

    return customer_order

@router.put("/{order_id}", response_model=schemas.CustomerOrder)
def update_customer_order(order_id: int, customer_order: schemas.CustomerOrderCreate, db: Session = Depends(get_db)):

    db_customer_order = crud.get_customer_order(db, order_id=order_id)

    if db_customer_order is None:
        raise HTTPException(status_code=404, detail="CustomerOrder not found")

    return crud.update_customer_order(db=db, order_id=order_id, customer_order=customer_order)

@router.delete("/{order_id}", response_model=schemas.CustomerOrder)
def delete_customer_order(order_id: int, db: Session = Depends(get_db)):

    db_customer_order = crud.get_customer_order(db, order_id=order_id)

    if db_customer_order is None:
        raise HTTPException(status_code=404, detail="CustomerOrder not found")

    return crud.delete_customer_order(db=db, order_id=order_id)
