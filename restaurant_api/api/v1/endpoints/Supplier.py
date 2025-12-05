from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
from database import SessionLocal

router = APIRouter(prefix="/supplier", tags=["Поставщик (supplier)"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.Supplier, status_code=status.HTTP_201_CREATED)
def create_supplier(supplier: schemas.SupplierCreate, db: Session = Depends(get_db)):

    return crud.create_supplier(db=db, supplier=supplier)

@router.get("/{supplier_id}", response_model=schemas.Supplier)
def read_supplier(supplier_id: int, db: Session = Depends(get_db)):

    db_supplier = crud.get_supplier(db, supplier_id=supplier_id)

    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Поставщик не найден")

    return db_supplier

@router.get("/", response_model=List[schemas.Supplier])
def read_supplier(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):

    supplier = crud.get_suppliers(db, skip=skip, limit=limit)

    return supplier

@router.put("/{supplier_id}", response_model=schemas.Supplier)
def update_supplier(supplier_id: int, supplier: schemas.SupplierCreate, db: Session = Depends(get_db)):

    db_supplier = crud.get_supplier(db, supplier_id=supplier_id)

    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Поставщик не найден")

    return crud.update_supplier(db=db, supplier_id=supplier_id, supplier=supplier)


@router.delete("/{supplier_id}", response_model=schemas.Supplier)
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):

    db_supplier = crud.get_supplier(db, supplier_id=supplier_id)

    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Поставщик не найден")

    return crud.delete_supplier(db=db, supplier_id=supplier_id)
