from fastapi import FastAPI
from databaseConfig import engine
from api.controllers import router

from api.middleware import LoggingMiddleware # for logging
from api.logger import logger

import api.models as models

from metrics import setup_metrics # importing metrics setup

app = FastAPI(openapi_url="/train/openapi.json", docs_url="/train/docs")

# Add logging middleware
app.add_middleware(LoggingMiddleware)

models.Base.metadata.create_all(bind=engine)

app.include_router(router)

# Initialize Prometheus metrics
setup_metrics(app)

# Log application startup
logger.info("Train service started", extra={"event": "application_startup"})
