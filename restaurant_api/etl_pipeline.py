import pandas as pd
from sqlalchemy.orm import Session
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from database import SessionLocal
import models

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
            'invalid_emails': []
        }

        # Общая проверка на пустые значения для обязательных полей
        if self.entity_type == 'restaurant':
            required_fields = ['name', 'address', 'phone', 'email', 'opening_date', 'seats_count', 'restaurant_type_id']
            for field in required_fields:
                if field in self.data.columns:
                    missing = self.data[field].isna()
                    if missing.any():
                        rows_with_missing = self.data[missing].index.tolist()
                        errors['missing_values'].append(f"{field}: {missing.sum()} пропущенных значений")

        # Проверка email
        if 'contact_email' in self.data.columns:
            # Фильтруем только непустые значения для проверки email
            valid_rows = self.data['contact_email'].notna()
            valid_emails = self.data.loc[valid_rows, 'email']

            # Строгая проверка email
            def is_valid_email(email):
                email = str(email).strip()
                if '@' not in email or email.count('@') != 1:
                    return False
                local_part, domain_part = email.split('@')
                if not local_part or not domain_part:
                    return False
                if '.' not in domain_part or domain_part.startswith('.') or domain_part.endswith('.'):
                    return False
                return True

            invalid_mask = ~valid_emails.astype(str).apply(is_valid_email)
            invalid_emails = valid_emails[invalid_mask]

            if len(invalid_emails) > 0:
                errors['invalid_emails'].append(f"Найдено {len(invalid_emails)} некорректных email")

            # Проверка дубликатов email
            if len(valid_emails) > 0:
                duplicates = valid_emails[valid_emails.duplicated(keep=False)]
                if len(duplicates) > 0:
                    errors['duplicate_emails'].append(f"Найдено {len(duplicates)} дубликатов email")

        return errors


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
        valid_data = self.data.copy()

        # Определяем обязательные поля для ресторана
        required_columns = ['name', 'address', 'opening_date', 'seats_count', 'restaurant_type_id']

        # Фильтрация по обязательным полям - удаляем строки, где нет обязательных данных
        for col in required_columns:
            if col in valid_data.columns:
                valid_data = valid_data.dropna(subset=[col])

        # Фильтрация по валидным email (если email присутствует)
        if 'email' in valid_data.columns:
            # Локальная функция проверки email
            def is_valid_email(email):
                if pd.isna(email):
                    return False
                email = str(email).strip()
                if '@' not in email or email.count('@') != 1:
                    return False
                local_part, domain_part = email.split('@')
                if not local_part or not domain_part:
                    return False
                if '.' not in domain_part or domain_part.startswith('.') or domain_part.endswith('.'):
                    return False
                return True

            # Фильтруем только строки с валидными email (если email указан)
            email_mask = valid_data['email'].apply(lambda x: is_valid_email(x) if pd.notna(x) else True)
            valid_data = valid_data[email_mask]

        # Преобразуем даты
        if 'opening_date' in valid_data.columns:
            valid_data['opening_date'] = pd.to_datetime(valid_data['opening_date'], errors='coerce')
            # Удаляем строки с некорректными датами
            valid_data = valid_data.dropna(subset=['opening_date'])

        # Преобразуем числовые поля
        if 'seats_count' in valid_data.columns:
            valid_data['seats_count'] = pd.to_numeric(valid_data['seats_count'], errors='coerce')
            # Удаляем строки с некорректными числами или отрицательными значениями
            valid_data = valid_data.dropna(subset=['seats_count'])
            valid_data = valid_data[valid_data['seats_count'] > 0]

        if 'restaurant_type_id' in valid_data.columns:
            valid_data['restaurant_type_id'] = pd.to_numeric(valid_data['restaurant_type_id'], errors='coerce')
            valid_data = valid_data.dropna(subset=['restaurant_type_id'])

        # Преобразуем булево поле is_active
        if 'is_active' in valid_data.columns:
            def parse_bool_value(value):
                if pd.isna(value):
                    return True  # По умолчанию True, если не указано
                value_str = str(value).lower().strip()
                true_values = ['true', 'да', 'yes', '1', 'on', '✓', '+']
                false_values = ['false', 'нет', 'no', '0', 'off', '✗', '-']

                if value_str in true_values:
                    return True
                elif value_str in false_values:
                    return False
                else:
                    return True  # По умолчанию True

            valid_data['is_active'] = valid_data['is_active'].apply(parse_bool_value)

        # Удаление дубликатов по name и address
        valid_data = valid_data.drop_duplicates(subset=['name', 'address'], keep='first')

        # Загрузка
        added_count = 0
        for _, row in valid_data.iterrows():
            name = str(row['name']).strip()
            address = str(row['address']).strip()

            # Проверяем существование ресторана по имени и адресу
            existing = self.db.query(models.Restaurant).filter(
                models.Restaurant.name == name,
                models.Restaurant.address == address
            ).first()

            if not existing:
                # Подготавливаем данные для создания ресторана
                restaurant_data = {
                    'name': name,
                    'address': address,
                    'phone': str(row.get('phone', '')) if pd.notna(row.get('phone')) else None,
                    'email': str(row.get('email', '')) if pd.notna(row.get('email')) else None,
                    'opening_date': row['opening_date'].date() if hasattr(row['opening_date'], 'date') else row[
                        'opening_date'],
                    'seats_count': int(row['seats_count']),
                    'restaurant_type_id': int(row['restaurant_type_id']),
                    'is_active': row.get('is_active', True)
                }

                try:
                    restaurant = models.Restaurant(**restaurant_data)
                    self.db.add(restaurant)
                    added_count += 1
                except Exception as e:
                    self.load_stats['errors'].append({
                        'record': self._clean_record_for_json(row),
                        'error': f'Ошибка при добавлении ресторана: {str(e)}'
                    })

        try:
            self.db.commit()
            logger.info(f"Добавлено {added_count} ресторанов")
        except Exception as e:
            self.db.rollback()
            self.load_stats['errors'].append({
                'record': 'Bulk commit',
                'error': f'Ошибка при сохранении ресторанов в БД: {str(e)}'
            })

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