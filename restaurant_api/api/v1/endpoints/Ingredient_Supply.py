from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
from database import SessionLocal

router = APIRouter(prefix="/ingredient_supply", tags=["Поставка ингредиентов (ingredient_supply)"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.IngredientSupply, status_code=status.HTTP_201_CREATED)
def create_ingredient_supply(ingredient_supply: schemas.IngredientSupplyCreate, db: Session = Depends(get_db)):

    return crud.create_ingredient_supply(db=db, ingredient_supply=ingredient_supply)

@router.get("/{ingredient_supply_id}", response_model=schemas.IngredientSupply)
def read_ingredient_supply(supply_id: int, db: Session = Depends(get_db)):

    db_ingredient_supply = crud.get_ingredient_supply(db, supply_id=supply_id)

    if db_ingredient_supply is None:
        raise HTTPException(status_code=404, detail="IngredientSupply not found")

    return db_ingredient_supply

@router.get("/", response_model=List[schemas.IngredientSupply])
def read_ingredient_supply(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):

    ingredient_supply = crud.get_ingredient_supplies(db, skip=skip, limit=limit)

    return ingredient_supply

@router.put("/{ingredient_supply_id}", response_model=schemas.IngredientSupply)
def update_ingredient_supply(supply_id: int, ingredient_supply: schemas.IngredientSupplyCreate, db: Session = Depends(get_db)):

    db_ingredient_supply = crud.get_ingredient_supply(db,supply_id=supply_id)

    if db_ingredient_supply is None:
        raise HTTPException(status_code=404, detail="IngredientSupply not found")

    return crud.update_ingredient_supply(db=db, supply_id=supply_id, ingredient_supply=ingredient_supply)

@router.delete("/{ingredient_supply_id}", response_model=schemas.IngredientSupply)
def delete_ingredient_supply(supply_id: int, db: Session = Depends(get_db)):

    db_ingredient_supply = crud.get_ingredient_supply(db, supply_id=supply_id)

    if db_ingredient_supply is None:
        raise HTTPException(status_code=404, detail="IngredientSupply not found")

    return crud.delete_ingredient_supply(db=db, supply_id=supply_id)
