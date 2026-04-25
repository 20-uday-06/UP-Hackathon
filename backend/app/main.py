from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.db.session import create_db_and_tables

app = FastAPI(title=settings.app_name)
create_db_and_tables()
app.mount("/app", StaticFiles(directory="app/web", html=True), name="app")


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


@app.get("/")
def root() -> dict[str, str]:
    return {"service": settings.app_name, "environment": settings.environment}


app.include_router(v1_router, prefix=settings.api_v1_prefix)
