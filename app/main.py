from contextlib import asynccontextmanager
from pathlib import Path
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.documents import router as documents_router
from app.api.search import router as search_router
from app.api.chat import router as chat_router

from app.services.clickhouse import initialize_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_tables()
    yield


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = FastAPI(
    title="Clinical RAG API",
    description=(
        "Система интеллектуального поиска и формирования ответов "
        "по медицинским клиническим рекомендациям на базе "
        "GigaChat и ClickHouse."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# CORS нужен для внешних интерфейсов. При работе через один домен
# запросы к API являются same-origin и не требуют CORS.
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://127.0.0.1:5500,http://localhost:5500,"
        "http://127.0.0.1:8080,http://localhost:8080"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Accept"]
)


@app.get("/", include_in_schema=False)
def frontend():
    index_file = FRONTEND_DIR / "index.html"

    if not index_file.is_file():
        return {
            "status": "online",
            "service": "Clinical RAG API",
            "version": "1.0.0",
            "message": "Frontend files are not installed"
        }

    return FileResponse(index_file)


@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "healthy",
        "service": "Clinical RAG API",
        "version": "1.0.0"
    }


app.include_router(documents_router)
app.include_router(search_router)
app.include_router(chat_router)

# Статические файлы интерфейса: CSS и JavaScript.
# Mount размещается после API-маршрутов, чтобы не перехватывать их.
if FRONTEND_DIR.is_dir():
    app.mount(
        "/",
        StaticFiles(directory=FRONTEND_DIR),
        name="frontend_static"
    )
