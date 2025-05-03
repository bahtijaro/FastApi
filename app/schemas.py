"""
Модуль pydantic-схем для работы с книгами, отзывами и пользователями.
"""

from typing import Optional

from pydantic import BaseModel, Field, field_validator, ConfigDict


##############################
#Проверки для схемы с книгами.
#############################

def checkinput_genre(genre: str) -> str:
    """Проверка на жанр книги."""
    access_genres = ["Роман", "Повесть", "Рассказ", "Новелла", "Поэма",
                     "Трагедия", "Комедия", "Детектив", "Антиутопия", "Фантастика"
    ]
    if genre not in access_genres:
        raise ValueError(f"Жанр должен быть одним из: {access_genres}")
    return genre

def checkinput_author(name: str) -> str:
    """Проверка на ввод автора книги."""
    if len(name.split()) < 2:
        raise ValueError("Автор должен иметь имя и фамилию")
    return name

##############################
#Проверки для логина и пароля пользователя
# (для схемы добавления/редактирования данных юзера.
##############################

def checkinput_username(login: str) -> str:
    """Проверка на наличие пробелов в логине."""
    if ' ' in login.strip():
        raise ValueError("Логин должен быть цельным словом без пробелов")
    return login

##############################
#Схема - Базовый класс для книг(все поля обязательны!!!)
# Один раз объявили и потом наследование !!!Single Responsibility!!!
##############################

class BookBaseSchema(BaseModel):
    """Базовая схема для книг с основными полями."""
    title: str = Field(
        example="Пример ввода - Война и Мир",
        min_length=2,
        max_length=100,
        alias="Название книги",
        )
    author: str = Field(
        example="Пример ввода - Толстой А.Н.",
        min_length=2,
        max_length=50,
        alias="Автор книги",
        )
    genre: str = Field(
        example=("Выбрать один жанр из списка - Роман, Повесть, Рассказ, Новелла, Поэма, "
                 "Трагедия, Комедия, Детектив, Антиутопия, Фантастика"
        ),
        min_length=2,
        max_length=50,
        alias="Жанр книги",
    )

##############################
#Схема - Добавить книгу(наследуется от Базового класса)
# + валидаторы.
##############################

class BookAddSchema(BookBaseSchema):
    """Схема для добавления книги."""
    @field_validator("author")
    def validate_author(cls, input_author):
        """Схема для добавления книги."""
        return checkinput_author(input_author)

    @field_validator("genre")
    def validate_genre(cls, input_genre):
        """Проверяется - есть ли указанный жанр в разрешенном списке."""
        return checkinput_genre(input_genre)

##############################
#Схема - Книга (наследуется от Базового класса)
# + id + avg-рейтинг (авт. генерация).
##############################
class BookSchema(BookBaseSchema):
    """#Схема - Книга (наследуется от Базового класса) + id + avg-рейтинг."""
    id: int = Field(
        example=1,
        alias="ID-номер книги в базе",
        )
    avg_rating: float = Field(
        example=4.5,
        description="Average рейтинг книги",
        alias="Средний рейтинг"
        )

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
        )


##############################
#Схема - Редактировать книгу
# (наследуется от схемы - книга).
##############################

class BookUpdateSchema(BaseModel):
    """Схема для обновления информации о книге."""
    title: Optional[str] = Field(
        None,
        alias="Название книги",
        example="Пример ввода - Война и Мир",
        )

    author: Optional[str] = Field(
        None,
        alias="Автор книги",
        example="Пример ввода - Толстой А.Н.",
        )

    genre: Optional[str] = Field(
        None,
        alias="Жанр книги",
        example="Выбрать один жанр из списка - Роман, Повесть, Рассказ, Новелла, Поэма, "
                "Трагедия, Комедия, Детектив, Антиутопия, Фантастика",
        )

    model_config = ConfigDict(
        populate_by_name=True,
        extra="forbid"
        )

    @field_validator("author")
    def validate_author(cls, input_author):
        """Проверка на корретный ввод автора книги."""
        return checkinput_author(input_author)

    ##Проверка на жанр книги:
    @field_validator("genre")
    def validate_genre(cls, input_genre):
        """Проверяет наличие жанра в разрещенном списке."""
        return checkinput_genre(input_genre)


##############################
#Схема - Добавить отзыв на книгу.
##############################

class ReviewAddSchema(BaseModel):
    """Схема для добавления отзыва на книгу."""
    book_id: int = Field(
        alias="Номер книги в базе",
        example="в формате integer"
    )
    text: str = Field(
        alias="Отзыв на книгу",
        example="в формате string"
    )
    rating: int = Field(
        alias="Рейтинг книги",
        example="в формате integer от 1 до 10"

    )
    user_id: int = Field(
        alias="Id-номер пользователя",
        example="в формате integer"
    )

    @field_validator("rating")
    def validate_rating(cls, value):
        """Проверка диапазона оценки (1-10)."""
        if value < 1 or value > 10:
            raise ValueError(f"Оценка в диапазоне от 1 до 10: введеное значение равно {value}")
        return value

##############################
#Схема - Отзыв на книгу (наследуется от схемы - Добавить отзыв).
##############################

class ReviewSchema(ReviewAddSchema):
    """Схема для отображения отзыва"""
    id: int = Field(alias="Id-номер рецензии")
    book_title: str = Field(alias="Название книги")
    user_title: str = Field(alias="Имя пользователя")

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True
        )

##############################
#Схема - База для пользователя (по аналогии с книгой).
##############################

class UserBaseSchema(BaseModel):
    """Базовая схема для пользователя."""
    username: str = Field(
        example="Пример ввода - pupkinVasya",
        min_length=8,
        # max_length=50,
        alias="Имя пользователя"
        )
    password: str = Field(
        example = "Пример ввода - kupiPirozhok",
        min_length=8,
        # max_length=50,
        alias="Пароль пользователя"
        )
    model_config = ConfigDict(
        extra="forbid",
        from_attributes=True,
        populate_by_name=True
    )

##############################
#Схема - Создание пользователя + валидатор логина.
##############################

class UserAddSchema(UserBaseSchema):
    """проверка ввода имени пользователя"""
    @field_validator("username")
    def validate_username(cls,username):
        return checkinput_username(username)

##############################
#Схема - Пользователь с Id.
##############################

class UserSchema(UserBaseSchema):
    """Схема для отображения информации о пользователе + ID."""
    id: int = Field(example=1)
    model_config = ConfigDict(
        from_attributes=True,
        )

##############################
#Схема - Обновление данных пользователя.
##############################

class UserUpdateSchema(UserBaseSchema):
    """Схема для update данных пользователя."""
    username: Optional[str] = Field(
        None,
        example="Новое имя pulkinKolya",
        alias="Имя пользователя"
    )

    password: Optional[str] = Field(
        None,
        example="Пример ввода - prodaiPirozhok",
        min_length=8,
        # max_length=50,
        alias="Пароль пользователя"
    )

    #проверка ввода имени пользователя
    @field_validator("username")
    def validate_username(cls,username):
        """Проверка отсутствия пробелов в логине."""
        return checkinput_username(username)
