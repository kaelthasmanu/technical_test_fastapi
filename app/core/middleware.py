import time
import uuid
from functools import wraps
from typing import Callable

from dependency_injector.wiring import inject as di_inject
from fastapi import Request
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware

from app.services.base_service import BaseService


def inject(func):
    @di_inject
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        injected_services = [arg for arg in kwargs.values() if isinstance(arg, BaseService)]
        if injected_services:
            try:
                injected_services[-1].close_scoped_session()
            except Exception as e:
                logger.exception("Error closing scoped session: {}", e)
        return result

    return wrapper


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every request with a correlation id and response time."""

    async def dispatch(self, request: Request, call_next: Callable):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        with logger.contextualize(request_id=request_id, path=request.url.path, method=request.method):
            start = time.perf_counter()
            logger.bind(client=str(request.client.host)).info("--> {} {}", request.method, request.url.path)
            try:
                response = await call_next(request)
            except Exception:
                logger.exception("Unhandled error processing request")
                raise
            finally:
                duration_ms = (time.perf_counter() - start) * 1000
                status_code = getattr(locals().get("response", None), "status_code", "ERR")
                logger.info("<-- {} {} {} {:.2f}ms", request.method, request.url.path, status_code, duration_ms)

        # propagate request id back
        if 'response' in locals():
            response.headers["X-Request-ID"] = request_id
            return response

