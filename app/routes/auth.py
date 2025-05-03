"""
Модуль для работы с аутентификацией и управлением пользователями.

Содержит эндпоинты для регистрации/ авторизации/  обновления/ удаления пользователей.
"""

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.future import select
from sqlalchemy import func

from app.database import SessionDep
from app.models import UserModel
from app.schemas import UserSchema, UserAddSchema, UserUpdateSchema
from app.security import create_access_token, pwd_context

router = APIRouter(prefix="/auth", tags=["Users"])


@router.post(
    "/register",
    response_model=UserSchema,
    summary="Регистрация нового пользователя",
    description="Логин должен быть цельным словом без пробелов, Пароль не менее 8 символов;"
    # tags=["Пользователи"]
)
async def register_user(
        user_data: UserAddSchema,
        session: SessionDep
        ):
    """Проверка имени юзера."""
    user = await session.execute(
        select(UserModel).where(UserModel.username == user_data.username)
    )
    if user.scalar():
        raise HTTPException(400, "Пользователь с таким именем уже существует!!! Измените логин")

    # Создание пользователя#.
    hashed_password = pwd_context.hash(user_data.password)
    create_user = UserModel\
        (username=user_data.username,
         password=hashed_password
    )

    session.add(create_user)
    await session.commit()
    await session.refresh(create_user)
    return create_user

@router.patch(
    "/{user_id}",
    response_model=UserSchema,
    summary="Редактирование данных пользователя в базе данных",
    description="Внимание!!! При выполнении данного запроса - "
                "происходит изменение данных пользователя в базе данных "
                "(выбираем юзера по id-номеру).",
)


#Проверка имени юзера.
async def update_user(
    user_id: int,
    data: UserUpdateSchema,
    session: SessionDep
):
    """олучаем id-юзера из модели по id-номеру."""
    result = await session.execute(
        select(UserModel).where(UserModel.id == user_id)
    )
    actual_user = result.scalar()
    # Если id-шник не верный, то выдает ошибку
    if not actual_user:
        raise HTTPException(404, f"Юзер с именем {user_id} не найден")
    # Далее проверяем логина юзера на совпадение с базой данных
    # Если есть, то выдает ошибку
    if data.username:
        session_existing = await session.execute(
            select(UserModel)
            .where(UserModel.username == (data.username or actual_user.username))
        )
        if session_existing.scalar():
            raise HTTPException(400, f"Пользователь <<{data.username}>> уже существует!")

    # Обновляем данные юзера
    update_data = data.model_dump(exclude_unset=True)
    # Если пароль был изменён
    if "password" in update_data:
        hashed_password = pwd_context.hash(update_data["password"])
        update_data["password"] = hashed_password
    for key, value in update_data.items():
        setattr(actual_user, key, value)

    await session.commit()
    await session.refresh(actual_user)
    return actual_user

###############################
#Удаление данных конкретного пользователя
#примерно по аналогии с delete книги
##############################

@router.delete(
    "",
    summary="Удаление пользователя из базы данных",
    description="Внимание!!! При выполнении данного запроса - "
                "происходит удаление данны хпользователя из базы данных "
                "(выбираем юзера по id-номеру).",
    )
async def del_user(user_id: int, session: SessionDep):
    """Получаем юзера из модели по id-номеру."""
    result = await session.execute(
        select(UserModel).where(UserModel.id == user_id)
    )
    user = result.scalar()
    if not user:
        raise HTTPException(404, f"Пользователь с ID-номером {user_id} не найден")
    await session.delete(user)
    await session.commit()

    return {"message": f"Данные пользователя с ID-номером {user_id} удалены"}

#############################
#Логин пользователя
##############################
@router.post("/login", response_model=dict)
async def login(user_data: UserAddSchema, session: SessionDep):
    """Логирование пользователя и получение JWT-токена."""
    result = await session.execute(
        select(UserModel)
        .where(func.lower(UserModel.username) == user_data.username.lower())
    )
    user = result.scalar()

    #Проверка  на корретность ввода либо логина либо пароля
    if not user or not pwd_context.verify(user_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Доступ запрещен, проверьте данные пользователя (логин или пароль)",
        )
    #Генерация токена
    token_data = {"sub": user.username.lower()}
    access_token = create_access_token(token_data)
    return {"access_token": access_token, "token_type": "bearer"}
