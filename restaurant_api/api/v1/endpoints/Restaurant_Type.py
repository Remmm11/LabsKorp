from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
from database import SessionLocal

router = APIRouter(prefix="/restaurant_type", tags=["Справочник типов ресторанов (restaurant_type)"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.RestaurantType])
def read_restaurant_type(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):

    restaurant_type = crud.get_restaurant_type(db, skip=skip, limit=limit)

    return restaurant_type
