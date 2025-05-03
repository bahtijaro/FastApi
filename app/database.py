"""
Конфигурация базы данных и настройка модели для приложения FastAPI
"""
from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

# Конфиг "движка" база данных
engine = create_async_engine("sqlite+aiosqlite:///app/books.db")
new_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    """
    Сеанс работы с базой данных
    """
    async with new_session() as session:
        yield session

# Экземпляр сессии sqlalchemy
SessionDep = Annotated[AsyncSession, Depends(get_session)]

class Base(DeclarativeBase):
    """Базовый класс для модели базы данных"""
    # pylint: disable=too-few-public-methods,unnecessary-pass
    pass
