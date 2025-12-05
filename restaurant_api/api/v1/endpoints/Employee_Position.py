from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

import crud
import schemas
from database import SessionLocal

router = APIRouter(prefix="/employee_position", tags=["Справочник должностей сотрудников (employee_position)"])

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=List[schemas.EmployeePosition])
def read_employee_position(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):

    employee_position = crud.get_employee_position(db, skip=skip, limit=limit)

    return employee_position
