from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

import crud
import schemas
from database import SessionLocal

router = APIRouter(prefix="/employee", tags=["Сотрудники (employees)"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.Employee, status_code=status.HTTP_201_CREATED)
def create_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):

    return crud.create_employee(db=db, employee=employee)

@router.get("/{employee_id}", response_model=schemas.Employee)
def read_employee(employee_id: int, db: Session = Depends(get_db)):

    db_employee = crud.get_employee(db, employee_id=employee_id)

    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return db_employee

@router.get("/", response_model=List[schemas.Employee])
def read_employee(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):

    employee = crud.get_employees(db, skip=skip, limit=limit)

    return employee

@router.put("/{employee_id}", response_model=schemas.Employee)
def update_employee(employee_id: int, employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):

    db_employee = crud.get_employee(db, employee_id=employee_id)

    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return crud.update_employee(db=db, employee_id=employee_id, employee=employee)

@router.delete("/{employee_id}", response_model=schemas.Employee)
def delete_employee(employee_id: int, db: Session = Depends(get_db)):
    db_employee = crud.get_employee(db, employee_id=employee_id)

    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return crud.delete_employee(db=db, employee_id=employee_id)
