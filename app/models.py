"""
Модели SQLAlchemy для базы данных
"""
from pydantic import computed_field
from sqlalchemy import String, ForeignKey, func, select
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from app.database import Base

class UserModel(Base):
    """Модель пользователя"""
    __tablename__ = "users"

    # pylint: disable=too-few-public-methods
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    reviews: Mapped[list["ReviewModel"]] = relationship(
        "ReviewModel",
        back_populates="user",
        cascade="all, delete"
        )

    def __str__(self):
        """Логин плюс id пользователя"""
        return f"Пользователь {self.username} (ID: {self.id})"

class BookModel(Base):
    """Модель книги"""
    __tablename__ = "books"

    # pylint: disable=too-few-public-methods
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    author: Mapped[str] = mapped_column(String(50), nullable=False)
    genre: Mapped[str] = mapped_column(String(30), nullable=False)
    reviews: Mapped[list["ReviewModel"]] = relationship(
        "ReviewModel",
        back_populates="book",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    @ hybrid_property
    def avg_rating(self) -> float:
        """Рассчитывает средний рейтинг книги на основе отзывов (объект в питоне)"""
        if not self.reviews:
            return 0.0
        return sum(review.rating for review in self.reviews) / len(self.reviews)

    @avg_rating.expression
    def avg_rating(cls):
        """SQL-выражение для расчета среднего рейтинга"""
        return (
            select(func.avg(ReviewModel.rating))
            .where(ReviewModel.book_id == cls.id)
            .label("avg_rating")
        )

class ReviewModel(Base):
    """Модель отзыва на книгу"""
    __tablename__ = "reviews"

    # pylint: disable=too-few-public-methods
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(500))
    rating: Mapped[int] = mapped_column( nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    user: Mapped["UserModel"] = relationship("UserModel", back_populates="reviews")
    book: Mapped["BookModel"] = relationship("BookModel", back_populates="reviews")

    @property
    def book_title(self):
        """Добавлено, чтобы в отзыве было видно название книги"""
        return self.book.title if self.book else "Книга удалена"

    @computed_field(alias="Имя пользователя")
    def user_title(self) -> str:
        """Добавлено, чтобы в отзыве было видно логин пользователя"""
        return self.user.username if self.user else "Пользователь удален"
