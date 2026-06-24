"""全局异常处理器"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.schemas.response import error_response
from datetime import datetime
import traceback
import logging

logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception):
    """捕获所有未处理的异常，返回统一错误格式"""
    logger.error(f"Unhandled exception: {exc}\n{traceback.format_exc()}")

    if isinstance(exc, HTTPException):
        # FastAPI HTTPException — 直接返回
        detail = exc.detail
        if isinstance(detail, dict) and "code" in detail:
            return JSONResponse(status_code=exc.status_code, content=detail)
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response(90004, str(exc.detail)),
        )

    # 未知异常
    return JSONResponse(
        status_code=500,
        content={
            "code": 90004,
            "message": "服务器内部错误",
            "data": None,
            "request_id": getattr(request.state, "request_id", None),
            "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        },
    )


async def validation_exception_handler(request: Request, exc: Exception):
    """Pydantic 校验异常处理"""
    from pydantic import ValidationError

    if isinstance(exc, ValidationError):
        errors = []
        for error in exc.errors():
            errors.append({
                "field": ".".join(str(l) for l in error["loc"]),
                "message": error["msg"],
            })
        return JSONResponse(
            status_code=400,
            content={
                "code": 90001,
                "message": f"请求参数校验失败",
                "data": {"errors": errors},
                "request_id": getattr(request.state, "request_id", None),
                "timestamp": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        )
    return None
