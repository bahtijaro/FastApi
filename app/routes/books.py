"""
Модуль роутов - по книгам.
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database import SessionDep
from app.models import BookModel, ReviewModel
from app.schemas import BookAddSchema, BookSchema, BookUpdateSchema

router = APIRouter(prefix="/books", tags=["Books"])

############################
#Добавление новых книг в базу данных
############################
@router.post(
    "",
    summary="Добавление новых книг в базу данных",
    description="При выполнении данного запроса новая книга будет добавлена в базу данных.",
    # tags=["Книги (POST-запросы)"],
    )

async def add_book(data: BookAddSchema, session: SessionDep):
    """Добавляет новую книгу в базу данных.
        +проверка на повтор книги, которая уже есть в базе.
    """
    exist_book = await session.execute(
        select(BookModel)
        .where(BookModel.title == data.title)
        .where(BookModel.author == data.author)
    )
    if exist_book.scalar():
        raise HTTPException(
            400, f"Книга{data.title} автора {data.author} уже есть в базе!"
        )
    new_book = BookModel(
    title=data.title,
    author=data.author,
    genre=data.genre
    )
    session.add(new_book)
    await session.commit()
    return {"message": "Книга добавлена", "book_id": new_book.id}

############################
#Получение списка со всеми книгами
############################
@router.get(
    "",
    response_model=list[BookSchema],
    summary="Получение данных по всем книгам",
    # tags=["Книги (GET-запросы)"],
    )
async def get_books(session: SessionDep):
    """Возвращает список всех книг с краткой информацией о рейтингах."""
    result = await session.execute(
        select(BookModel)
        # .options(selectinload(BookModel.reviews))
        .options(selectinload(BookModel.reviews).load_only(ReviewModel.rating))
    )
    books = result.scalars().all()
    return books

############################
#Получение конретной книги, включая средний рейтинг
############################
@router.get(
    "/{book_id}",
    response_model=BookSchema,
    summary="Получение данных по конкретной книге",
    description="Получение данных по конкретной книге (выбираем книгу по id-номеру)."
    # tags=["Книги (GET-запросы)"],
    )
async def get_book(book_id: int, session: SessionDep):
    """Получаем информацию о книге по ID-шнику."""
    result = await session.execute(
        select(BookModel)
        .where(BookModel.id == book_id)
        .options(selectinload(BookModel.reviews))
    )
    book = result.scalar()
    if not book:
        raise HTTPException(404, "Книга не найдена")
    return book

############################
#редактирование данных книги из базы данных
############################
@router.patch(
    "/{book_id}",
    response_model=BookSchema,
    summary="Редактирование книги в базе данных",
    description="Внимание!!! При выполнении данного запроса - "
                "происходит изменение данных книги в базе данных (выбираем книгу по id-номеру).",
    # tags=["Книги (PATCH-запросы)"]
)
async def update_book(
    book_id: int,
    data: BookUpdateSchema,
    session: SessionDep
):
    """Обновляем информацию о книге по её ID."""
    result = await session.execute(
        select(BookModel).where(BookModel.id == book_id)
    )
    book = result.scalar()
    #ID-шника нет в базе - получаем 404.
    if not book:
        raise HTTPException(404, "Книга не найдена")
    # Проверяем название книги.
    if data.title:
        session_existing = await session.execute(
            select(BookModel)
            .where(BookModel.title == (data.title or book.title))
            # .where(BookModel.author == (data.author or book.author))
            # .where(BookModel.id != book_id)
        )
        # Если повтор названия книги - получаем 400
        if session_existing.scalar():
            raise HTTPException(400, f"Книга с таким названием <<{data.title}>> уже существует")

    # Update полей
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(book, key, value)

    await session.commit()
    await session.refresh(book)
    return book

############################
#Удаление книги из базы данных
############################

@router.delete(
    "",
    summary="Удаление книги из базы данных",
    description="Внимание!!! При выполнении данного запроса - "
                "происходит удаление книги из базы данных (выбираем книгу по id-номеру).",
    # tags=["Книги (DELETE-запросы)"],
    )
async def del_book(book_id: int, session: SessionDep):
    """Удаляем книгу по указанному ID. Если книгу нашли - удаляем"""
    result = await session.execute(
        select(BookModel).where(BookModel.id == book_id)
    )
    book = result.scalar()
    #книги нет в базе - получаем 404.
    if not book:
        raise HTTPException(404, "Книга не найдена")
    await session.delete(book)
    await session.commit()
    return {"message": f"Книга с ID-номером {book_id} удалена"}
