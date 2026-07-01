"""制度解读 / 个性化权益报告路由 — /api/v1/interpretations, /api/v1/benefits"""
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_hr_plus
from app.schemas.response import success_response, error_response
from app.services.interpretation_service import InterpretationService, PermissionDeniedError
from app.services.benefit_service import BenefitService

router = APIRouter(tags=["制度解读与权益报告"])


# ── 制度解读 ──

@router.get("/interpretations/{document_id}")
async def get_interpretation(
    document_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取制度解读（按需生成 + 缓存）"""
    try:
        data = await InterpretationService.get_or_generate(
            document_id, current_user.role, db,
        )
        return success_response(data=data)
    except PermissionDeniedError:
        raise HTTPException(status_code=403, detail=error_response(40300, "无权查看该制度文档"))
    except ValueError:
        raise HTTPException(status_code=404, detail=error_response(30001, "文档不存在"))


@router.post("/interpretations/{document_id}/refresh")
async def refresh_interpretation(
    document_id: str,
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """强制重新生成制度解读（HR/管理员）"""
    try:
        data = await InterpretationService.get_or_generate(
            document_id, current_user.role, db, force=True,
        )
        return success_response(data=data, message="已重新生成解读")
    except PermissionDeniedError:
        raise HTTPException(status_code=403, detail=error_response(40300, "无权查看该制度文档"))
    except ValueError:
        raise HTTPException(status_code=404, detail=error_response(30001, "文档不存在"))


# ── 个性化权益报告 ──

@router.get("/benefits/report")
async def get_benefit_report(
    year: Optional[int] = Query(None, ge=2000, le=2100),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取本人专属权益报告（按需生成 + 缓存）"""
    target_year = year or datetime.now(timezone.utc).year
    data = await BenefitService.get_or_generate(current_user, target_year, db)
    return success_response(data=data)


@router.post("/benefits/report/refresh")
async def refresh_benefit_report(
    year: Optional[int] = Query(None, ge=2000, le=2100),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """强制重新生成本人权益报告"""
    target_year = year or datetime.now(timezone.utc).year
    data = await BenefitService.get_or_generate(current_user, target_year, db, force=True)
    return success_response(data=data, message="已重新生成权益报告")
