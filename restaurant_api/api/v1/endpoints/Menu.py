from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
from database import SessionLocal

router = APIRouter(prefix="/menu", tags=["Меню (menu)"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.Menu, status_code=status.HTTP_201_CREATED)
def create_menu(menu: schemas.MenuCreate, db: Session = Depends(get_db)):

    return crud.create_menu(db=db, menu=menu)

@router.get("/{menu_id}", response_model=schemas.Menu)
def read_menu(menu_id: int, db: Session = Depends(get_db)):

    db_menu = crud.get_menu(db, menu_id=menu_id)

    if db_menu is None:
        raise HTTPException(status_code=404, detail="Menu not found")

    return db_menu

@router.get("/", response_model=List[schemas.Menu])
def read_menu(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):

    menu = crud.get_menus(db, skip=skip, limit=limit)

    return menu

@router.put("/{menu_id}", response_model=schemas.Menu)
def update_menu(menu_id: int, menu: schemas.MenuCreate, db: Session = Depends(get_db)):

    db_menu = crud.get_menu(db, menu_id=menu_id)

    if db_menu is None:
        raise HTTPException(status_code=404, detail="Menu not found")

    return crud.update_menu(db=db, menu_id=menu_id, menu=menu)

@router.delete("/{menu_id}", response_model=schemas.Menu)
def delete_menu(menu_id: int, db: Session = Depends(get_db)):

    db_menu = crud.get_menu(db, menu_id=menu_id)

    if db_menu is None:
        raise HTTPException(status_code=404, detail="Menu not found")

    return crud.delete_menu(db=db, menu_id=menu_id)
