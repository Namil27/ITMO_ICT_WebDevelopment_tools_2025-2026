from fastapi import FastAPI

from src.routers import book_router, exchange_request_router, user_router
from src.routers.auth import router as auth_router

app = FastAPI(
    title="Bookcrossing API",
    description="Учебное веб-приложение для буккросинга на FastAPI + PostgreSQL",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(book_router)
app.include_router(exchange_request_router)


@app.get("/")
def root():
    return {"message": "Bookcrossing API is running"}