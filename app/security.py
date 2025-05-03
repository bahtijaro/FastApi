"""
Модуль аутентификации и авторизации пользователей.
"""

from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select, func

from app.database import SessionDep
from app.models import UserModel

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "3d6f45a5fc12445dbdc2345f12b5e6c9d3b8a7e1c2d4f5a6b7c8d9e0f1a2b3c4"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(data: dict) -> str:
    """Создает JWT-токен доступа на основе переданных данных."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
        session: SessionDep,
        token: str = Depends(oauth2_scheme)
) -> UserModel:
    """Возвращает текущего пользователя на основе JWT-токена."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Не удалось проверить учетные данные",
        # headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Декодирование токена
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"[DEBUG] Decoded payload: {payload}")

        # Извлечение username
        username = payload.get("sub")
        if not username:
            print("[AUTH] Токен не содержит идентификатора пользователя (sub)")
            raise credentials_exception
        # Поиск пользователя (регистронезависимый)
        query = select(UserModel).where(func.lower(UserModel.username) == username.lower())
        result = await session.execute(query)
        user = result.scalar()

        if user is None:
            print(f"[ERROR] User {username} not found in DB")
            raise credentials_exception
        # Возврат пользователя
        return user

    except JWTError as e:
        print(f"[AUTH] Ошибка JWT: {str(e)}")
        raise credentials_exception
