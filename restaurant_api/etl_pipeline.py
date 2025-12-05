import pandas as pd
from sqlalchemy.orm import Session
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from decimal import Decimal
import re

from database import SessionLocal
import models
import schemas

logger = logging.getLogger("restaurant_api")


class ETLPipeline:
    def __init__(self, file_path: str, entity_type: Optional[str] = None):
        self.file_path = file_path
        self.db: Session = SessionLocal()
        self.data: Optional[pd.DataFrame] = None
        self.entity_type = entity_type
        self.validation_errors: List[Dict] = []
        self.load_stats: Dict[str, Any] = {
            'total_records': 0,
            'successful': 0,
            'failed': 0,
            'errors': []
        }

    def extract(self) -> pd.DataFrame:
        """Извлечение данных из файла"""
        logger.info(f"Начало извлечения данных из {self.file_path}")
        try:
            if self.file_path.endswith(('.xls', '.xlsx')):
                self.data = pd.read_excel(self.file_path, dtype=str)
            elif self.file_path.endswith('.csv'):
                self.data = pd.read_csv(self.file_path, dtype=str, encoding='utf-8')
            else:
                raise ValueError("Неподдерживаемый формат файла")

            # Замена пустых значений на NaN
            empty_values = ['nan', 'null', 'none', '', 'н/д', '-', '–', '—']
            self.data = self.data.replace(empty_values, pd.NA)

            # Определение типа сущности по столбцам
            self._detect_entity_type()

            logger.info(f"Успешно извлечено {len(self.data)} строк типа '{self.entity_type}'")
            return self.data
        except Exception as e:
            logger.error(f"Ошибка извлечения: {e}")
            raise

    def _detect_entity_type(self):
        """Определение типа сущности по столбцам"""
        if self.entity_type:
            return

        columns = set(self.data.columns)

        if 'company_name' in columns and 'inn' in columns:
            self.entity_type = 'supplier'
        elif 'first_name' in columns and 'last_name' in columns:
            self.entity_type = 'employee'
        elif 'table_number' in columns and 'customer_name' in columns:
            self.entity_type = 'customer_order'
        elif 'invoice_number' in columns and 'supply_date' in columns:
            self.entity_type = 'ingredient_supply'
        elif 'name' in columns and 'category' in columns:
            self.entity_type = 'dish'
        elif 'name' in columns and 'season' in columns:
            self.entity_type = 'menu'
        elif 'name' in columns and 'address' in columns and 'seats_count' in columns:
            self.entity_type = 'restaurant'
        else:
            self.entity_type = 'unknown'

    def validate(self) -> Dict[str, List[str]]:
        """Валидация данных"""
        logger.info("Начало валидации данных")

        errors = {
            'missing_values': [],
            'invalid_emails': [],
            'invalid_phones': [],
            'invalid_dates': [],
            'invalid_numbers': []
        }

        # Общая проверка на пустые значения для обязательных полей
        if self.entity_type == 'restaurant':
            required_fields = ['name', 'address', 'opening_date', 'seats_count']
            for field in required_fields:
                if field in self.data.columns:
                    missing = self.data[field].isna()
                    if missing.any():
                        rows_with_missing = self.data[missing].index.tolist()
                        errors['missing_values'].append(
                            f"{field}: {missing.sum()} пропущенных значений в строках {rows_with_missing}")

        # Проверка email
        if 'email' in self.data.columns:
            valid_rows = self.data['email'].notna()
            valid_emails = self.data.loc[valid_rows, 'email']

            def is_valid_email(email):
                email = str(email).strip()
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                return bool(re.match(pattern, email))

            invalid_mask = ~valid_emails.astype(str).apply(is_valid_email)
            invalid_emails = valid_emails[invalid_mask]

            if len(invalid_emails) > 0:
                errors['invalid_emails'].append(f"Найдено {len(invalid_emails)} некорректных email")

        # Проверка телефона
        if 'phone' in self.data.columns:
            valid_rows = self.data['phone'].notna()
            valid_phones = self.data.loc[valid_rows, 'phone']

            def is_valid_phone(phone):
                phone = str(phone).strip()
                digits = re.sub(r'\D', '', phone)
                return len(digits) >= 10 and len(digits) <= 15

            invalid_mask = ~valid_phones.astype(str).apply(is_valid_phone)
            invalid_phones = valid_phones[invalid_mask]

            if len(invalid_phones) > 0:
                errors['invalid_phones'].append(f"Найдено {len(invalid_phones)} некорректных телефонов")

        # Проверка дат
        date_columns = [col for col in self.data.columns if 'date' in col.lower()]
        for col in date_columns:
            if col in self.data.columns:
                valid_rows = self.data[col].notna()
                valid_dates = self.data.loc[valid_rows, col]

                invalid_mask = ~valid_dates.astype(str).apply(lambda x: self._is_valid_date(str(x)))
                invalid_dates = valid_dates[invalid_mask]

                if len(invalid_dates) > 0:
                    errors['invalid_dates'].append(f"{col}: {len(invalid_dates)} некорректных дат")

        # Проверка числовых полей
        numeric_fields = ['seats_count']
        for field in numeric_fields:
            if field in self.data.columns:
                valid_rows = self.data[field].notna()
                valid_values = self.data.loc[valid_rows, field]

                def is_positive_number(x):
                    try:
                        num = float(str(x))
                        return num > 0
                    except:
                        return False

                invalid_mask = ~valid_values.astype(str).apply(is_positive_number)
                invalid_values = valid_values[invalid_mask]

                if len(invalid_values) > 0:
                    errors['invalid_numbers'].append(
                        f"{field}: {len(invalid_values)} некорректных значений (должны быть положительными числами)")

        logger.info(
            f"Валидация завершена. Найдено ошибок: {len(errors['missing_values']) + len(errors['invalid_emails']) + len(errors['invalid_phones']) + len(errors['invalid_dates']) + len(errors['invalid_numbers'])}")
        return errors

    def _is_valid_date(self, date_str: str) -> bool:
        """Проверка валидности даты"""
        try:
            pd.to_datetime(date_str, errors='raise')
            return True
        except:
            return False

    def transform(self) -> pd.DataFrame:
        """Трансформация данных с бизнес-логикой"""
        logger.info("Начало трансформации данных")

        # Создаем копию данных для трансформации
        transformed_data = self.data.copy()

        # Очистка текстовых данных
        text_columns = transformed_data.select_dtypes(include=['object']).columns
        for col in text_columns:
            # Заменяем строковые 'nan' и пустые строки на настоящие NaN
            transformed_data[col] = transformed_data[col].replace(['nan', ''], pd.NA)
            # Убираем пробелы только у валидных строк
            mask = transformed_data[col].notna()
            transformed_data.loc[mask, col] = transformed_data.loc[mask, col].astype(str).str.strip()

        # Обработка дат
        date_columns = [col for col in transformed_data.columns if 'date' in col.lower()]
        for col in date_columns:
            transformed_data[col] = pd.to_datetime(transformed_data[col], errors='coerce')

        # Обработка числовых полей
        numeric_fields = ['seats_count', 'restaurant_type_id']
        for field in numeric_fields:
            if field in transformed_data.columns:
                if field in ['seats_count', 'restaurant_type_id']:
                    # Integer поля
                    transformed_data[field] = pd.to_numeric(transformed_data[field], errors='coerce')

        # Преобразование булевых полей
        bool_fields = ['is_active']
        for field in bool_fields:
            if field in transformed_data.columns:
                transformed_data[field] = transformed_data[field].apply(
                    lambda x: self._parse_bool(x) if pd.notna(x) else None
                )

        # Заменяем все оставшиеся NaN на None
        transformed_data = transformed_data.where(pd.notnull(transformed_data), None)

        self.data = transformed_data
        logger.info("Трансформация завершена")
        return transformed_data

    def _parse_bool(self, value: str) -> Optional[bool]:
        """Парсинг булевого значения"""
        value = str(value).lower().strip()
        true_values = ['true', 'да', 'yes', '1', 'on', '✓', '+']
        false_values = ['false', 'нет', 'no', '0', 'off', '✗', '-']

        if value in true_values:
            return True
        elif value in false_values:
            return False
        else:
            return None

    def _load_restaurants(self) -> int:
        """Загрузка ресторанов"""
        added_count = 0

        for index, row in self.data.iterrows():
            try:
                # Проверяем обязательные поля
                if row['name'] is None or row['address'] is None or row['opening_date'] is None or row[
                    'seats_count'] is None:
                    self.load_stats['errors'].append({
                        'record': self._clean_record_for_json(row),
                        'error': f'Отсутствуют обязательные поля в строке {index}'
                    })
                    continue

                # Проверяем количество мест
                try:
                    seats_count = int(row['seats_count'])
                    if seats_count <= 0:
                        self.load_stats['errors'].append({
                            'record': self._clean_record_for_json(row),
                            'error': f'Некорректное количество мест ({row["seats_count"]}) в строке {index}'
                        })
                        continue
                except (ValueError, TypeError):
                    self.load_stats['errors'].append({
                        'record': self._clean_record_for_json(row),
                        'error': f'Некорректное количество мест ({row["seats_count"]}) в строке {index}'
                    })
                    continue

                # Проверка существования
                existing = self.db.query(models.Restaurant).filter(
                    models.Restaurant.name == str(row['name']),
                    models.Restaurant.address == str(row['address'])
                ).first()

                if existing:
                    logger.warning(f"Ресторан уже существует: {row['name']}")
                    self.load_stats['errors'].append({
                        'record': self._clean_record_for_json(row),
                        'error': f'Ресторан уже существует в строке {index}'
                    })
                    continue

                # Преобразуем дату
                opening_date = None
                try:
                    if isinstance(row['opening_date'], pd.Timestamp):
                        opening_date = row['opening_date'].date()
                    elif isinstance(row['opening_date'], datetime):
                        opening_date = row['opening_date'].date()
                    elif isinstance(row['opening_date'], str):
                        opening_date = datetime.strptime(row['opening_date'], '%Y-%m-%d').date()
                except Exception as e:
                    self.load_stats['errors'].append({
                        'record': self._clean_record_for_json(row),
                        'error': f'Некорректная дата открытия ({row["opening_date"]}) в строке {index}: {str(e)}'
                    })
                    continue

                # Преобразуем boolean
                is_active = True
                if row['is_active'] is not None:
                    if str(row['is_active']).lower().strip() in ['true', 'да', 'yes', '1', 'on', '✓', '✅', '+']:
                        is_active = True
                    elif str(row['is_active']).lower().strip() in ['false', 'нет', 'no', '0', 'off', '✗', '❌', '-']:
                        is_active = False
                    else:
                        self.load_stats['errors'].append({
                            'record': self._clean_record_for_json(row),
                            'error': f'Некорректное значение is_active ({row["is_active"]}) в строке {index}'
                        })
                        continue

                # Преобразуем тип ресторана
                restaurant_type_id = 1
                try:
                    if row['restaurant_type_id'] is not None:
                        restaurant_type_id = int(row['restaurant_type_id'])
                except (ValueError, TypeError):
                    self.load_stats['errors'].append({
                        'record': self._clean_record_for_json(row),
                        'error': f'Некорректный тип ресторана ({row["restaurant_type_id"]}) в строке {index}'
                    })
                    continue

                restaurant_data = {
                    'name': str(row['name']),
                    'address': str(row['address']),
                    'phone': str(row['phone']) if row['phone'] is not None else None,
                    'email': str(row['email']) if row['email'] is not None else None,
                    'opening_date': opening_date,
                    'seats_count': seats_count,
                    'restaurant_type_id': restaurant_type_id,
                    'is_active': is_active
                }

                restaurant = models.Restaurant(**restaurant_data)
                self.db.add(restaurant)
                self.db.commit()
                added_count += 1

            except Exception as e:
                self.db.rollback()
                self.load_stats['errors'].append({
                    'record': self._clean_record_for_json(row),
                    'error': f'Ошибка при обработке строки {index}: {str(e)}'
                })
                continue

        return added_count

    def _clean_record_for_json(self, row):
        """Очистка записи для JSON сериализации"""
        cleaned = {}
        for key, value in row.items():
            if pd.isna(value):
                cleaned[key] = None
            elif isinstance(value, pd.Timestamp):
                cleaned[key] = str(value)
            else:
                cleaned[key] = str(value) if value is not None else None
        return cleaned

    def load(self) -> Dict[str, Any]:
        """Загрузка данных в БД"""
        logger.info("Начало загрузки данных")

        if self.data is None:
            raise ValueError("Нет данных для загрузки")

        self.load_stats = {
            'total_records': len(self.data),
            'successful': 0,
            'failed': 0,
            'errors': []
        }

        try:
            if self.entity_type == 'restaurant':
                added_count = self._load_restaurants()
            else:
                raise ValueError(f"Неизвестный тип сущности: {self.entity_type}")

            self.load_stats['successful'] = added_count
            self.load_stats['failed'] = self.load_stats['total_records'] - added_count

            logger.info(f"Загрузка данных завершена. Добавлено {added_count} записей")

            # Очищаем errors для JSON
            cleaned_errors = []
            for error in self.load_stats['errors']:
                cleaned_error = {
                    'record': self._clean_error_record_for_json(error['record']),
                    'error': error['error']
                }
                cleaned_errors.append(cleaned_error)

            self.load_stats['errors'] = cleaned_errors

            return self.load_stats

        except Exception as e:
            logger.error(f"Ошибка загрузки: {e}")
            self.db.rollback()
            raise
        finally:
            self.db.close()

    def _clean_error_record_for_json(self, record):
        """Очистка записи ошибки для JSON сериализации"""
        if isinstance(record, dict):
            cleaned = {}
            for key, value in record.items():
                if pd.isna(value):
                    cleaned[key] = None
                elif isinstance(value, pd.Timestamp):
                    cleaned[key] = str(value)
                else:
                    cleaned[key] = str(value) if value is not None else None
            return cleaned
        return record

    def run(self) -> tuple:
        """Запуск полного ETL процесса"""
        self.extract()
        self.transform()
        validation_errors = self.validate()
        load_stats = self.load()

        # Очищаем validation_errors для JSON
        cleaned_validation_errors = {}
        for key, value in validation_errors.items():
            if isinstance(value, list):
                cleaned_validation_errors[key] = [str(v) for v in value]
            else:
                cleaned_validation_errors[key] = str(value)

        return cleaned_validation_errors, load_stats