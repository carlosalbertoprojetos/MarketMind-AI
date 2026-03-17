from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title=settings.PROJECT_NAME)
    if settings.ENV == "production" and settings.SECRET_KEY == "change-me":
        raise RuntimeError("SECRET_KEY must be set for production.")

    origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
    if origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    app.include_router(api_router, prefix=settings.API_V1_STR)
    return app


app = create_app()
