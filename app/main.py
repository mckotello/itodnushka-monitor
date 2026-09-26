from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.auth import router as auth_router
from app.api.monitors import router as monitors_router
from app.core.config import settings


BASE_DIR = Path(__file__).resolve().parent


app = FastAPI(
    title=settings.app_name,
    description="Мониторинг доступности сайтов и API",
    version="1.0.0",
)


app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "static"),
    name="static",
)


@app.get("/", include_in_schema=False)
async def dashboard():
    return FileResponse(
        BASE_DIR / "static" / "index.html",
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": settings.app_name,
    }


app.include_router(
    auth_router,
    prefix="/api",
)

app.include_router(
    monitors_router,
    prefix="/api",
)