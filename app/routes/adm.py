"""
Модуль управления базой данных. Эндпоинт для пересоздания базы данных.
"""

from fastapi import APIRouter
from app.database import engine, Base

router = APIRouter(tags=["Database"])

###############################
#Создание базы данных по книгам
###############################
@router.post(
    "/setup-database",
    summary="Создание базы данных книг",
    description="Внимание!!! Данный запрос удаляет все данные и создает структуру заново!!!"
    # tags=["Книги (POST-запросы)"]
    )
async def setup_database():
    """Удаляет все таблицы в базе и создает их заново."""
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    return {"message": "База данных успешно создана!!!"}
