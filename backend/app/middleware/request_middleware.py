"""请求中间件 — 客户端类型识别、请求ID注入、响应头"""
import time
import uuid
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint


class RequestIDMiddleware(BaseHTTPMiddleware):
    """为每个请求注入唯一 request_id，并在响应头返回"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:16]
        request.state.request_id = request_id
        request.state.start_time = time.time()

        response = await call_next(request)

        response.headers["X-Request-ID"] = request_id
        response.headers["X-API-Version"] = "v1"
        response.headers["X-Response-Time"] = f"{int((time.time() - request.state.start_time) * 1000)}ms"

        return response


class ClientPlatformMiddleware(BaseHTTPMiddleware):
    """识别客户端平台（web / android），注入到 request.state"""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        platform = request.headers.get("X-Client-Platform", "web")
        version = request.headers.get("X-Client-Version", "unknown")
        request.state.client_platform = platform
        request.state.client_version = version
        return await call_next(request)
