from fastapi import FastAPI
from databaseConfig import engine
from api.controllers import router
import api.models as models

from api.middleware import LoggingMiddleware  # Import the middleware
from api.logger import logger  # Import the logger
from metrics import setup_metrics # importing metrics setup

app = FastAPI(openapi_url="/payment/openapi.json", docs_url="/payment/docs")

# Add logging middleware
app.add_middleware(LoggingMiddleware)

models.Base.metadata.create_all(bind=engine)

app.include_router(router)

# Initialize Prometheus metrics
setup_metrics(app)

logger.info("Payment service started", extra={"event": "application_startup"})