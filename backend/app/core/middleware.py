import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

logger = logging.getLogger("api.access")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        process_time = time.time() - start_time
        
        log_dict = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration": f"{process_time:.4f}s",
            "client": request.client.host if request.client else "unknown"
        }
        
        logger.info(f"Request: {log_dict}")
        
        return response
