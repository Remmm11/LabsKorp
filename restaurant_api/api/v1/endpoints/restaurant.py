from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
from database import SessionLocal

router = APIRouter(prefix="/restaurants", tags=["Рестораны (restaurants)"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.Restaurant, status_code=status.HTTP_201_CREATED)
def create_restaurant(restaurant: schemas.RestaurantCreate, db: Session = Depends(get_db)):

    return crud.create_restaurant(db=db, restaurant=restaurant)

@router.get("/{restaurant_id}", response_model=schemas.Restaurant)
def read_restaurant(restaurant_id: int, db: Session = Depends(get_db)):

    db_restaurant = crud.get_restaurant(db, restaurant_id=restaurant_id)

    if db_restaurant is None:
        raise HTTPException(status_code=404, detail="Ресторан не найден")

    return db_restaurant

@router.get("/", response_model=List[schemas.Restaurant])
def read_restaurant(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):

    restaurant = crud.get_restaurants(db, skip=skip, limit=limit)

    return restaurant

@router.put("/{restaurant_id}", response_model=schemas.Restaurant)
def update_restaurant(restaurant_id: int, restaurant: schemas.RestaurantCreate, db: Session = Depends(get_db)):

    db_restaurant = crud.get_restaurant(db, restaurant_id=restaurant_id)

    if db_restaurant is None:
        raise HTTPException(status_code=404, detail="Ресторан не найден")

    return crud.update_restaurant(db=db, restaurant_id=restaurant_id, restaurant=restaurant)

@router.delete("/{restaurant_id}", response_model=schemas.Restaurant)
def delete_restaurant(restaurant_id: int, db: Session = Depends(get_db)):

    db_restaurant = crud.get_restaurant(db, restaurant_id=restaurant_id)

    if db_restaurant is None:
        raise HTTPException(status_code=404, detail="Ресторан не найден")

    return crud.delete_restaurant(db=db, restaurant_id=restaurant_id)
