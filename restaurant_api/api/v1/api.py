from fastapi import APIRouter

from api.v1.endpoints import (
    Restaurant_Type,
    Employee_Position,
    restaurant,
    Employee,
    Menu,
    Dish,
    Supplier,
    Ingredient_Supply,
    Customer_Order,
    etl
)

api_router = APIRouter()

api_router.include_router(Restaurant_Type.router)
api_router.include_router(Employee_Position.router)
api_router.include_router(restaurant.router)
api_router.include_router(Employee.router)
api_router.include_router(Menu.router)
api_router.include_router(Dish.router)
api_router.include_router(Supplier.router)
api_router.include_router(Ingredient_Supply.router)
api_router.include_router(Customer_Order.router)
api_router.include_router(etl.router)