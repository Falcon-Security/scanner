from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk

from core.config import settings

from motor.motor_asyncio import AsyncIOMotorClient

from v1.home.api import router as home_router
from v1.recon.api import router as recon_router

contact = {
    "name": "Srijan Gupta",
    "email": "gupta.srijan94@gmail.com",
    "url": "https://srijankgupta.vercel.app"
}

license = {
    "name": "MIT",
    "url": "https://github.com/geekymeeky/invexis/blob/main/LICENSE"
}

if settings.ENVIRONMENT == "production":
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        traces_sample_rate=1.0,
    )


def init() -> FastAPI:
    _app: FastAPI = FastAPI(title=settings.PROJECT_NAME,
                            license_info=license,
                            docs_url="/",
                            contact=contact)

    _app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            str(origin) for origin in settings.BACKEND_CORS_ORIGINS
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @_app.on_event("startup")
    def startup():
        _app.mongodb_client = AsyncIOMotorClient(settings.MONGO_URI)
        _app.mongodb = _app.mongodb_client[settings.MONGO_DB]

    @_app.on_event("shutdown")
    def shutdown():
        _app.mongodb_client.close()

    _app.include_router(home_router, prefix=settings.API_V1_STR)
    _app.include_router(recon_router, prefix=settings.API_V1_STR)

    return _app


app = init()