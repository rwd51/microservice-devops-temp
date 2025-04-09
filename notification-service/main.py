from fastapi import FastAPI
from api.controllers import router
from api.middleware import LoggingMiddleware  # Import the middleware
from api.logger import logger  # Import the logger
from metrics import setup_metrics # importing metrics setup
from rabbitmq_consumer import start_consumer

import threading

app = FastAPI(openapi_url="/notification/openapi.json", docs_url="/notification/docs")

# Add logging middleware
app.add_middleware(LoggingMiddleware)

app.include_router(router)

# Initialize Prometheus metrics
setup_metrics(app)

# Start RabbitMQ consumer in a separate thread
consumer_thread = threading.Thread(target=start_consumer, daemon=True)
consumer_thread.start()

logger.info("Notification service started", extra={"event": "application_startup"})