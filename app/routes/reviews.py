"""
Модуль роутов - по отзывам на книги.
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database import SessionDep
from app.models import BookModel, ReviewModel
from app.schemas import ReviewAddSchema, ReviewSchema

# router = APIRouter(prefix="/reviews", tags=["Отзывы на книги"])
router = APIRouter(prefix="/reviews", tags=["Reviews books"])

##########################
#Добавление отзывов на книгу
##########################
@router.post(
    "",
    summary="Добавление отзывов",
    description="При выполнении данного запроса, можно добавить отзыв "
                "на конкретную книгу (выбираем книгу по id-номеру)"

    # tags=["Книги (POST-запросы)"],
)
async def add_review(data: ReviewAddSchema, session: SessionDep):
    """Добавляем новый отзыв для указанной книги."""
    new_review = ReviewModel(
        book_id=data.book_id,
        text=data.text,
        rating=data.rating,
        user_id=data.user_id
        )
    result = await session.execute(
        select(BookModel).where(BookModel.id == data.book_id)
    )
    book = result.scalar()

    if not book:
        raise HTTPException(404, "Книга не найдена")

    session.add(new_review)
    await session.commit()
    return {"message": "Отзыв добавлен"}


##########################
#Получение списка отзывов на книги
##########################
@router.get(
    "",
    response_model=list[ReviewSchema],
    summary="Получение списка отзывов на все книги",
    description="При выполнении данного запроса - получение списка отзывов на все книги"
    # tags=["Книги (GET-запросы)"]
    )
async def get_reviews(session: SessionDep):
    """Возвращает список всех отзывов."""
    result = await session.execute(
        select(ReviewModel)
        .options(
            selectinload(ReviewModel.book),
            selectinload(ReviewModel.user))
        )
    reviews = result.scalars().all()
    return reviews
