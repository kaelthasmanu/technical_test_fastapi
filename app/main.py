from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.routes import routers as v1_routers
from app.api.v2.routes import routers as v2_routers
from app.core.config import configs
from app.core.container import Container
from app.core.logging import setup_logging
from app.core.middleware import RequestLoggingMiddleware
from app.util.class_object import singleton
from loguru import logger


@singleton
class AppCreator:
    def __init__(self):
        # create app with lifespan that will initialize shared resources
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # configure logging with current configs
            setup_logging(configs)

            # instantiate DI container and database here (startup)
            self.container = Container()
            # create the DB provider instance (engine/session factory)
            self.db = self.container.db()

            logger.info("Application startup complete")
            try:
                yield
            finally:
                # place any shutdown cleanup here
                logger.info("Application shutdown")

        # set app default
        self.app = FastAPI(
            title=configs.PROJECT_NAME,
            openapi_url=f"{configs.API}/openapi.json",
            version="0.0.1",
            lifespan=lifespan,
        )

        # set cors
        if configs.BACKEND_CORS_ORIGINS:
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=[str(origin) for origin in configs.BACKEND_CORS_ORIGINS],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        # request logging middleware
        self.app.add_middleware(RequestLoggingMiddleware)

        # set routes
        @self.app.get("/")
        def root():
            return "service is working"

        self.app.include_router(v1_routers, prefix=configs.API_V1_STR)
        self.app.include_router(v2_routers, prefix=configs.API_V2_STR)


app_creator = AppCreator()
app = app_creator.app
# db and container will be available after the app startup (TestClient triggers it)
db = getattr(app_creator, "db", None)
container = getattr(app_creator, "container", None)