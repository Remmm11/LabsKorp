from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, DECIMAL, Boolean, Text, Date
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


# Справочник типов ресторанов
class DictionaryRestaurantType(Base):
    __tablename__ = 'restaurant_types'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)

    # Связь с ресторанами
    restaurants = relationship("Restaurant", back_populates="restaurant_type")


# Справочник должностей сотрудников
class DictionaryEmployeePosition(Base):
    __tablename__ = 'employee_positions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(20), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    salary_min = Column(DECIMAL(10, 2))
    salary_max = Column(DECIMAL(10, 2))

    # Связь с сотрудниками
    employees = relationship("Employee", back_populates="position")


# Рестораны
class Restaurant(Base):
    __tablename__ = 'restaurants'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    address = Column(String(500), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    opening_date = Column(Date, nullable=False)
    seats_count = Column(Integer, nullable=False)
    restaurant_type_id = Column(Integer, ForeignKey('restaurant_types.id'), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи - ВАЖНО: используйте правильные имена классов
    restaurant_type = relationship("DictionaryRestaurantType", back_populates="restaurants")
    employees = relationship("Employee", back_populates="restaurant")
    menus = relationship("Menu", back_populates="restaurant")
    ingredient_supplies = relationship("IngredientSupply", back_populates="restaurant")
    customer_orders = relationship("CustomerOrder", back_populates="restaurant")


# Сотрудники
class Employee(Base):
    __tablename__ = 'employees'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    birth_date = Column(Date)
    hire_date = Column(Date, nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    position_id = Column(Integer, ForeignKey('employee_positions.id'), nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    salary = Column(DECIMAL(10, 2), nullable=False)
    passport_data = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    position = relationship("DictionaryEmployeePosition", back_populates="employees")
    restaurant = relationship("Restaurant", back_populates="employees")
    customer_orders = relationship("CustomerOrder", back_populates="employee")


# Меню
class Menu(Base):
    __tablename__ = 'menus'

    id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    name = Column(String(200), nullable=False)
    season = Column(String(50))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    restaurant = relationship("Restaurant", back_populates="menus")
    dishes = relationship("Dish", back_populates="menu")


# Блюда
class Dish(Base):
    __tablename__ = 'dishes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    menu_id = Column(Integer, ForeignKey('menus.id'), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(100), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    weight_grams = Column(Integer)
    cooking_time_minutes = Column(Integer)
    is_available = Column(Boolean, default=True)
    calories = Column(Integer)
    ingredients = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    menu = relationship("Menu", back_populates="dishes")
    customer_orders = relationship("CustomerOrder", back_populates="dish")


# Поставщики
class Supplier(Base):
    __tablename__ = 'suppliers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_name = Column(String(300), nullable=False)
    contact_person = Column(String(200))
    phone = Column(String(20), nullable=False)
    email = Column(String(100))
    address = Column(String(500))
    inn = Column(String(20))
    contract_number = Column(String(100))
    contract_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    ingredient_supplies = relationship("IngredientSupply", back_populates="supplier")


# Поставки ингредиентов
class IngredientSupply(Base):
    __tablename__ = 'ingredient_supplies'

    id = Column(Integer, primary_key=True, autoincrement=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=False)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    supply_date = Column(Date, nullable=False)
    invoice_number = Column(String(100), nullable=False)
    total_amount = Column(DECIMAL(12, 2), nullable=False)
    delivery_status = Column(String(20), default='ожидает')
    payment_status = Column(String(20), default='не оплачено')
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    supplier = relationship("Supplier", back_populates="ingredient_supplies")
    restaurant = relationship("Restaurant", back_populates="ingredient_supplies")


# Заказы клиентов
class CustomerOrder(Base):
    __tablename__ = 'customer_orders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_id = Column(Integer, ForeignKey('restaurants.id'), nullable=False)
    table_number = Column(String(20), nullable=False)
    customer_name = Column(String(200))
    customer_phone = Column(String(20))
    dish_id = Column(Integer, ForeignKey('dishes.id'), nullable=False)
    quantity = Column(Integer, default=1, nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    order_status = Column(String(20), default='принят')
    payment_method = Column(String(20), default='наличные')
    order_time = Column(DateTime, default=datetime.utcnow)
    employee_id = Column(Integer, ForeignKey('employees.id'))

    # Связи
    restaurant = relationship("Restaurant", back_populates="customer_orders")
    dish = relationship("Dish", back_populates="customer_orders")
    employee = relationship("Employee", back_populates="customer_orders")