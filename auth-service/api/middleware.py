import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from api.logger import logger

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Record request start time
        start_time = time.time()
        
        # Process the request
        try:
            response = await call_next(request)
            
            # Calculate request duration
            duration_ms = round((time.time() - start_time) * 1000)
            
            # Log basic request info
            logger.info(f"{request.method} {request.url.path} - Status: {response.status_code} - Duration: {duration_ms}ms")
            
            return response
            
        except Exception as exc:
            # Log exception
            logger.exception(f"Request failed: {request.method} {request.url.path}")
            
            # Re-raise the exception to be handled by FastAPI
            raise