from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import time
import jwt
import logging
from typing import Callable, Awaitable
from src.config.settings import settings

logger = logging.getLogger(__name__)


async def rate_limit_handler(request: Request, call_next):
    client_ip = request.client.host
    current_time = time.time()

    # Initialize rate limiting for new IP
    if client_ip not in request.app.state.rate_limits:
        request.app.state.rate_limits[client_ip] = {
            'requests': [],
            'blocked_until': 0
        }

    client_limits = request.app.state.rate_limits[client_ip]

    # Check if client is blocked
    if current_time < client_limits['blocked_until']:
        raise HTTPException(
            status_code=429,
            detail="Too many requests. Please try again later."
        )

    # Clean old requests
    client_limits['requests'] = [
        req_time for req_time in client_limits['requests']
        if current_time - req_time < 60  # 1 minute window
    ]

    # Check rate limit
    if len(client_limits['requests']) >= 100:  # 100 requests per minute
        client_limits['blocked_until'] = current_time + 60
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again in 1 minute."
        )

    # Add current request
    client_limits['requests'].append(current_time)

    return await call_next(request)


async def error_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={"error": e.detail}
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        )


async def auth_handler(
        request: Request,
        call_next: Callable[[Request], Awaitable[JSONResponse]]
):
    if request.url.path.startswith("/api/v1/public"):
        return await call_next(request)

    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise HTTPException(
                status_code=401,
                detail="Missing or invalid authentication token"
            )

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=['HS256']
            )
            request.state.user = payload
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )

        return await call_next(request)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal authentication error"
        )


async def cors_handler(request: Request, call_next):
    response = await call_next(request)

    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'

    return response


class RequestContextHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def __call__(self, request: Request, call_next):
        request_id = str(time.time())
        request.state.request_id = request_id

        # Log request
        self.logger.info(
            f"Request {request_id}: {request.method} {request.url.path}"
        )

        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        # Log response
        self.logger.info(
            f"Request {request_id} completed in {duration:.2f}s with status {response.status_code}"
        )

        response.headers['X-Request-ID'] = request_id
        response.headers['X-Response-Time'] = f"{duration:.2f}s"

        return response


def setup_handlers(app):
    app.middleware("http")(RequestContextHandler())
    app.middleware("http")(rate_limit_handler)
    app.middleware("http")(auth_handler)
    app.middleware("http")(error_handler)
    app.middleware("http")(cors_handler)

    # Initialize rate limiting state
    app.state.rate_limits = {}