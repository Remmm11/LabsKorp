from sqlalchemy.orm import Session
import models
import schemas
import logging


logger = logging.getLogger("restaurant_api")


# RestaurantType CRUD
def get_restaurant_type(db: Session, skip: int = 0, limit: int = 100):
    logger.info(f"Получение списка ресторанов, пропуск={skip}, лимит={limit}")
    return db.query(models.DictionaryRestaurantType).order_by(models.DictionaryRestaurantType.id).offset(skip).limit(limit).all()

# EmployeePosition CRUD
def get_employee_position(db: Session, skip: int = 0, limit: int = 100):
    logger.info(f"Получение должности сотрудника, пропуск={skip}, лимит={limit}")
    return db.query(models.DictionaryEmployeePosition).order_by(models.DictionaryEmployeePosition.id).offset(skip).limit(limit).all()

# Restaurant CRUD
def get_restaurant(db: Session, restaurant_id: int):
    logger.info(f"Получение ресторана по ID: {restaurant_id}")
    return db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()


def get_restaurants(db: Session, skip: int = 0, limit: int = 100):
    logger.info(f"Получение списка ресторанов, пропуск={skip}, лимит={limit}")
    return db.query(models.Restaurant).order_by(models.Restaurant.id).offset(skip).limit(limit).all()


def create_restaurant(db: Session, restaurant: schemas.RestaurantCreate):
    logger.info(f"Создание ресторана: {restaurant.name}")
    db_restaurant = models.Restaurant(**restaurant.dict())
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    logger.info(f"Создан ресторан с ID: {db_restaurant.id}")
    return db_restaurant


def update_restaurant(db: Session, restaurant_id: int, restaurant: schemas.RestaurantCreate):
    logger.info(f"Обновление ресторана с ID: {restaurant_id}")
    db_restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    if db_restaurant:
        for key, value in restaurant.dict().items():
            setattr(db_restaurant, key, value)
        db.commit()
        db.refresh(db_restaurant)
        logger.info(f"Обновлен ресторан с ID: {restaurant_id}")
    else:
        logger.warning(f"Ресторан с ID: {restaurant_id} не найден")
    return db_restaurant


def delete_restaurant(db: Session, restaurant_id: int):
    logger.info(f"Удаление ресторана с ID: {restaurant_id}")
    db_restaurant = db.query(models.Restaurant).filter(models.Restaurant.id == restaurant_id).first()
    if db_restaurant:
        db.delete(db_restaurant)
        db.commit()
        logger.info(f"Удален ресторан с ID: {restaurant_id}")
    else:
        logger.warning(f"Ресторан с ID: {restaurant_id} не найден")
    return db_restaurant


# Employee CRUD
def get_employee(db: Session, employee_id: int):
    logger.info(f"Получение сотрудника по ID: {employee_id}")
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()


def get_employees(db: Session, skip: int = 0, limit: int = 100):
    logger.info(f"Получение списка сотрудников, пропуск={skip}, лимит={limit}")
    return db.query(models.Employee).order_by(models.Employee.id).offset(skip).limit(limit).all()


def create_employee(db: Session, employee: schemas.EmployeeCreate):
    logger.info(f"Создание сотрудника: {employee.first_name} {employee.last_name}")
    db_employee = models.Employee(**employee.dict())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    logger.info(f"Создан сотрудник с ID: {db_employee.id}")
    return db_employee


def update_employee(db: Session, employee_id: int, employee: schemas.EmployeeCreate):
    logger.info(f"Обновление сотрудника с ID: {employee_id}")
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if db_employee:
        for key, value in employee.dict().items():
            setattr(db_employee, key, value)
        db.commit()
        db.refresh(db_employee)
        logger.info(f"Обновлен сотрудник с ID: {employee_id}")
    else:
        logger.warning(f"Сотрудник с ID: {employee_id} не найден")
    return db_employee


def delete_employee(db: Session, employee_id: int):
    logger.info(f"Удаление сотрудника с ID: {employee_id}")
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()
    if db_employee:
        db.delete(db_employee)
        db.commit()
        logger.info(f"Удален сотрудник с ID: {employee_id}")
    else:
        logger.warning(f"Сотрудник с ID: {employee_id} не найден")
    return db_employee


# Menu CRUD
def get_menu(db: Session, menu_id: int):
    logger.info(f"Получение меню по ID: {menu_id}")
    return db.query(models.Menu).filter(models.Menu.id == menu_id).first()


def get_menus(db: Session, skip: int = 0, limit: int = 100):
    logger.info(f"Получение списка меню, пропуск={skip}, лимит={limit}")
    return db.query(models.Menu).order_by(models.Menu.id).offset(skip).limit(limit).all()


def create_menu(db: Session, menu: schemas.MenuCreate):
    logger.info(f"Создание меню: {menu.name}")
    db_menu = models.Menu(**menu.dict())
    db.add(db_menu)
    db.commit()
    db.refresh(db_menu)
    logger.info(f"Создано меню с ID: {db_menu.id}")
    return db_menu


def update_menu(db: Session, menu_id: int, menu: schemas.MenuCreate):
    logger.info(f"Обновление меню с ID: {menu_id}")
    db_menu = db.query(models.Menu).filter(models.Menu.id == menu_id).first()
    if db_menu:
        for key, value in menu.dict().items():
            setattr(db_menu, key, value)
        db.commit()
        db.refresh(db_menu)
        logger.info(f"Обновлено меню с ID: {menu_id}")
    else:
        logger.warning(f"Меню с ID: {menu_id} не найдено")
    return db_menu


def delete_menu(db: Session, menu_id: int):
    logger.info(f"Удаление меню с ID: {menu_id}")
    db_menu = db.query(models.Menu).filter(models.Menu.id == menu_id).first()
    if db_menu:
        db.delete(db_menu)
        db.commit()
        logger.info(f"Удалено меню с ID: {menu_id}")
    else:
        logger.warning(f"Меню с ID: {menu_id} не найдено")
    return db_menu


# Dish CRUD
def get_dish(db: Session, dish_id: int):
    logger.info(f"Получение блюда по ID: {dish_id}")
    return db.query(models.Dish).filter(models.Dish.id == dish_id).first()


def get_dishes(db: Session, skip: int = 0, limit: int = 100):
    logger.info(f"Получение списка блюд, пропуск={skip}, лимит={limit}")
    return db.query(models.Dish).order_by(models.Dish.id).offset(skip).limit(limit).all()


def create_dish(db: Session, dish: schemas.DishCreate):
    logger.info(f"Создание блюда: {dish.name}")
    db_dish = models.Dish(**dish.dict())
    db.add(db_dish)
    db.commit()
    db.refresh(db_dish)
    logger.info(f"Создано блюдо с ID: {db_dish.id}")
    return db_dish


def update_dish(db: Session, dish_id: int, dish: schemas.DishCreate):
    logger.info(f"Обновление блюда с ID: {dish_id}")
    db_dish = db.query(models.Dish).filter(models.Dish.id == dish_id).first()
    if db_dish:
        for key, value in dish.dict().items():
            setattr(db_dish, key, value)
        db.commit()
        db.refresh(db_dish)
        logger.info(f"Обновлено блюдо с ID: {dish_id}")
    else:
        logger.warning(f"Блюдо с ID: {dish_id} не найдено")
    return db_dish


def delete_dish(db: Session, dish_id: int):
    logger.info(f"Удаление блюда с ID: {dish_id}")
    db_dish = db.query(models.Dish).filter(models.Dish.id == dish_id).first()
    if db_dish:
        db.delete(db_dish)
        db.commit()
        logger.info(f"Удалено блюдо с ID: {dish_id}")
    else:
        logger.warning(f"Блюдо с ID: {dish_id} не найдено")
    return db_dish


# Supplier CRUD
def get_supplier(db: Session, supplier_id: int):
    logger.info(f"Получение поставщика по ID: {supplier_id}")
    return db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()


def get_suppliers(db: Session, skip: int = 0, limit: int = 100):
    logger.info(f"Получение списка поставщиков, пропуск={skip}, лимит={limit}")
    return db.query(models.Supplier).order_by(models.Supplier.id).offset(skip).limit(limit).all()


def create_supplier(db: Session, supplier: schemas.SupplierCreate):
    logger.info(f"Создание поставщика: {supplier.company_name}")
    db_supplier = models.Supplier(**supplier.dict())
    db.add(db_supplier)
    db.commit()
    db.refresh(db_supplier)
    logger.info(f"Создан поставщик с ID: {db_supplier.id}")
    return db_supplier


def update_supplier(db: Session, supplier_id: int, supplier: schemas.SupplierCreate):
    logger.info(f"Обновление поставщика с ID: {supplier_id}")
    db_supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if db_supplier:
        for key, value in supplier.dict().items():
            setattr(db_supplier, key, value)
        db.commit()
        db.refresh(db_supplier)
        logger.info(f"Обновлен поставщик с ID: {supplier_id}")
    else:
        logger.warning(f"Поставщик с ID: {supplier_id} не найден")
    return db_supplier


def delete_supplier(db: Session, supplier_id: int):
    logger.info(f"Удаление поставщика с ID: {supplier_id}")
    db_supplier = db.query(models.Supplier).filter(models.Supplier.id == supplier_id).first()
    if db_supplier:
        db.delete(db_supplier)
        db.commit()
        logger.info(f"Удален поставщик с ID: {supplier_id}")
    else:
        logger.warning(f"Поставщик с ID: {supplier_id} не найден")
    return db_supplier


# Ingredient Supply CRUD
def get_ingredient_supply(db: Session, supply_id: int):
    logger.info(f"Получение поставки по ID: {supply_id}")
    return db.query(models.IngredientSupply).filter(models.IngredientSupply.id == supply_id).first()


def get_ingredient_supplies(db: Session, skip: int = 0, limit: int = 100):
    logger.info(f"Получение списка поставок, пропуск={skip}, лимит={limit}")
    return db.query(models.IngredientSupply).order_by(models.IngredientSupply.id).offset(skip).limit(limit).all()


def create_ingredient_supply(db: Session, ingredient_supply: schemas.IngredientSupplyCreate):
    logger.info(f"Создание поставки с накладной: {ingredient_supply.invoice_number}")
    db_ingredient_supply = models.IngredientSupply(**ingredient_supply.dict())
    db.add(db_ingredient_supply)
    db.commit()
    db.refresh(db_ingredient_supply)
    logger.info(f"Создана поставка с ID: {db_ingredient_supply.id}")
    return db_ingredient_supply


def update_ingredient_supply(db: Session, supply_id: int, ingredient_supply: schemas.IngredientSupplyCreate):
    logger.info(f"Обновление поставки с ID: {supply_id}")
    db_ingredient_supply = db.query(models.IngredientSupply).filter(models.IngredientSupply.id == supply_id).first()
    if db_ingredient_supply:
        for key, value in ingredient_supply.dict().items():
            setattr(db_ingredient_supply, key, value)
        db.commit()
        db.refresh(db_ingredient_supply)
        logger.info(f"Обновлена поставка с ID: {supply_id}")
    else:
        logger.warning(f"Поставка с ID: {supply_id} не найдена")
    return db_ingredient_supply


def delete_ingredient_supply(db: Session, supply_id: int):
    logger.info(f"Удаление поставки с ID: {supply_id}")
    db_ingredient_supply = db.query(models.IngredientSupply).filter(models.IngredientSupply.id == supply_id).first()
    if db_ingredient_supply:
        db.delete(db_ingredient_supply)
        db.commit()
        logger.info(f"Удалена поставка с ID: {supply_id}")
    else:
        logger.warning(f"Поставка с ID: {supply_id} не найдена")
    return db_ingredient_supply


# Customer Order CRUD
def get_customer_order(db: Session, order_id: int):
    logger.info(f"Получение заказа по ID: {order_id}")
    return db.query(models.CustomerOrder).filter(models.CustomerOrder.id == order_id).first()


def get_customer_orders(db: Session, skip: int = 0, limit: int = 100):
    logger.info(f"Получение списка заказов, пропуск={skip}, лимит={limit}")
    return db.query(models.CustomerOrder).order_by(models.CustomerOrder.id).offset(skip).limit(limit).all()


def create_customer_order(db: Session, customer_order: schemas.CustomerOrderCreate):
    logger.info(f"Создание заказа на столик: {customer_order.table_number}")
    db_customer_order = models.CustomerOrder(**customer_order.dict())
    db.add(db_customer_order)
    db.commit()
    db.refresh(db_customer_order)
    logger.info(f"Создан заказ с ID: {db_customer_order.id}")
    return db_customer_order


def update_customer_order(db: Session, order_id: int, customer_order: schemas.CustomerOrderCreate):
    logger.info(f"Обновление заказа с ID: {order_id}")
    db_customer_order = db.query(models.CustomerOrder).filter(models.CustomerOrder.id == order_id).first()
    if db_customer_order:
        for key, value in customer_order.dict().items():
            setattr(db_customer_order, key, value)
        db.commit()
        db.refresh(db_customer_order)
        logger.info(f"Обновлен заказ с ID: {order_id}")
    else:
        logger.warning(f"Заказ с ID: {order_id} не найден")
    return db_customer_order


def delete_customer_order(db: Session, order_id: int):
    logger.info(f"Удаление заказа с ID: {order_id}")
    db_customer_order = db.query(models.CustomerOrder).filter(models.CustomerOrder.id == order_id).first()
    if db_customer_order:
        db.delete(db_customer_order)
        db.commit()
        logger.info(f"Удален заказ с ID: {order_id}")
    else:
        logger.warning(f"Заказ с ID: {order_id} не найден")
    return db_customer_order
