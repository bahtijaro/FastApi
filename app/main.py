"""
Экземпляр FastApi
"""
from fastapi import FastAPI
from app.routes import books, reviews, auth, adm

app = FastAPI()


@app.get(
    "/",
    # tags=["Начальная страница"],
    tags=["Welcome"],
    description="Добро пожаловать в API- каталог книг"
)
async def root():
    """
    Эндпоинт - Приветствие
    """
    return {"message": "Добро пожаловать в API- каталог книг"}

app.include_router(adm.router)
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(reviews.router)
