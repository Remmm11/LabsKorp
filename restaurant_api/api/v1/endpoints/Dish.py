from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
from database import SessionLocal

router = APIRouter(prefix="/dishes", tags=["Блюда (dishes)"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.Dish, status_code=status.HTTP_201_CREATED)
def create_dish(dish: schemas.DishCreate, db: Session = Depends(get_db)):

    return crud.create_dish(db=db, dish=dish)

@router.get("/{dish_id}", response_model=schemas.Dish)
def read_dish(dish_id: int, db: Session = Depends(get_db)):

    db_dish = crud.get_dish(db, dish_id=dish_id)

    if db_dish is None:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")

    return db_dish

@router.get("/", response_model=List[schemas.Dish])
def read_dish(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):

    dish = crud.get_dishes(db, skip=skip, limit=limit)

    return dish

@router.put("/{dish_id}", response_model=schemas.Dish)
def update_dish(dish_id: int, dish: schemas.DishCreate, db: Session = Depends(get_db)):

    db_dish = crud.get_dish(db, dish_id=dish_id)

    if db_dish is None:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")

    return crud.update_dish(db=db, dish_id=dish_id, dish=dish)

@router.delete("/{dish_id}", response_model=schemas.Dish)
def delete_dish(dish_id: int, db: Session = Depends(get_db)):

    db_dish = crud.get_dish(db, dish_id=dish_id)

    if db_dish is None:
        raise HTTPException(status_code=404, detail="Блюдо не найдено")

    return crud.delete_dish(db=db, dish_id=dish_id)
