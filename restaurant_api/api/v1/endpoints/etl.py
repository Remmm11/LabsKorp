from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import logging
import tempfile

from database import SessionLocal
from etl_pipeline import ETLPipeline

router = APIRouter(prefix="/etl", tags=["ETL процессы"])


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload-file", summary="Загрузка и обработка файла")
async def upload_file(
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
    """
    Загрузка файла и запуск ETL процесса
    """
    try:
        # Проверка формата файла
        allowed_extensions = {'.csv', '.xls', '.xlsx'}
        file_extension = os.path.splitext(file.filename)[1].lower()

        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"Неподдерживаемый формат файла. Разрешенные форматы: {', '.join(allowed_extensions)}"
            )

        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Запуск ETL процесса
            pipeline = ETLPipeline(temp_file_path)
            validation_errors, load_stats = pipeline.run()

            return {
                "Имя файла": file.filename,
                "Статус": "success",
                "Текст": "Файл успешно обработан",
                "Ошибки валидации": validation_errors,
                "Статистика загрузки": load_stats
            }

        finally:
            # Удаляем временный файл
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        logging.error(f"Ошибка при обработке файла: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке файла: {str(e)}"
        )