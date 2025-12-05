from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional
from decimal import Decimal


# Restaurant Type schemas
class RestaurantTypeBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None


class RestaurantTypeCreate(RestaurantTypeBase):
    pass


class RestaurantType(RestaurantTypeBase):
    id: int

    class Config:
        from_attributes = True


# Employee Position schemas
class EmployeePositionBase(BaseModel):
    code: str
    name: str
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None


class EmployeePositionCreate(EmployeePositionBase):
    pass


class EmployeePosition(EmployeePositionBase):
    id: int

    class Config:
        from_attributes = True


# Restaurant schemas
class RestaurantBase(BaseModel):
    name: str
    address: str
    phone: Optional[str] = None
    email: Optional[str] = None
    opening_date: date
    seats_count: int
    restaurant_type_id: int
    is_active: bool = True


class RestaurantCreate(RestaurantBase):
    pass


class Restaurant(RestaurantBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Employee schemas
class EmployeeBase(BaseModel):
    first_name: str
    last_name: str
    birth_date: Optional[date] = None
    hire_date: date
    phone: Optional[str] = None
    email: Optional[str] = None
    position_id: int
    restaurant_id: int
    salary: Decimal
    passport_data: Optional[str] = None


class EmployeeCreate(EmployeeBase):
    pass


class Employee(EmployeeBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Menu schemas
class MenuBase(BaseModel):
    name: str
    season: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    is_active: bool = True


class MenuCreate(MenuBase):
    restaurant_id: int


class Menu(MenuBase):
    id: int
    restaurant_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Dish schemas
class DishBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    price: Decimal
    weight_grams: Optional[int] = None
    cooking_time_minutes: Optional[int] = None
    calories: Optional[int] = None
    ingredients: Optional[str] = None
    is_available: bool = True


class DishCreate(DishBase):
    menu_id: int


class Dish(DishBase):
    id: int
    menu_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Supplier schemas
class SupplierBase(BaseModel):
    company_name: str
    contact_person: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    inn: str
    contract_number: str
    contract_date: date
    is_active: bool = True


class SupplierCreate(SupplierBase):
    pass


class Supplier(SupplierBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Ingredient Supply schemas
class IngredientSupplyBase(BaseModel):
    supply_date: date
    invoice_number: str
    total_amount: Decimal
    delivery_status: str = "ожидает"
    payment_status: str = "не оплачено"


class IngredientSupplyCreate(IngredientSupplyBase):
    supplier_id: int
    restaurant_id: int


class IngredientSupply(IngredientSupplyBase):
    id: int
    supplier_id: int
    restaurant_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# Customer Order schemas
class CustomerOrderBase(BaseModel):
    table_number: str
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    dish_id: int
    quantity: int = 1
    total_amount: Decimal
    order_status: str = "принят"
    payment_method: str = "наличные"


class CustomerOrderCreate(CustomerOrderBase):
    restaurant_id: int
    employee_id: Optional[int] = None


class CustomerOrder(CustomerOrderBase):
    id: int
    restaurant_id: int
    employee_id: Optional[int] = None
    order_time: datetime

    class Config:
        from_attributes = True