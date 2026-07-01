"""FAQ 管理接口路由 — /api/v1/faqs/*

读取：所有登录用户可访问（员工端可查看常见问题）
写入（增/改/删）：HR专员 + 管理员
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_hr_plus
from app.schemas.faq import FAQCreateRequest, FAQUpdateRequest
from app.schemas.response import success_response, error_response, list_response
from app.services.faq_service import FAQService

router = APIRouter(tags=["FAQ管理"])

FAQ_PREFIX = "/faqs"


def _faq_to_dict(faq) -> dict:
    return {
        "faq_id": faq.faq_id,
        "question": faq.question,
        "answer": faq.answer,
        "category_id": faq.category_id,
        "category_name": faq.category.name if faq.category else None,
        "related_doc_id": faq.related_doc_id,
        "keywords": faq.keywords,
        "view_count": faq.view_count or 0,
        "status": faq.status.value if faq.status else None,
        "created_by": faq.created_by,
        "created_at": str(faq.created_at) if faq.created_at else None,
        "updated_at": str(faq.updated_at) if faq.updated_at else None,
    }


@router.get(f"{FAQ_PREFIX}")
async def list_faqs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[str] = None,
    keyword: Optional[str] = None,
    status: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FAQ 列表（默认仅展示正常状态，已归档的不返回）"""
    # 未显式传入 status 时默认只看正常 FAQ，使删除（归档）后的条目不再出现
    effective_status = status if status else "active"
    faqs, total = await FAQService.get_faqs(
        db_session=db, page=page, page_size=page_size,
        category_id=category_id, status=effective_status, keyword=keyword,
    )
    items = [_faq_to_dict(f) for f in faqs]
    return list_response(items=items, page=page, page_size=page_size, total=total)


@router.post(f"{FAQ_PREFIX}")
async def create_faq(
    req: FAQCreateRequest,
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """新增 FAQ（HR专员/管理员）"""
    faq = await FAQService.create_faq(
        question=req.question,
        answer=req.answer,
        category_id=req.category_id,
        created_by=current_user.user_id,
        related_doc_id=req.related_doc_id,
        keywords=req.keywords,
        db_session=db,
    )
    return success_response(
        data={"faq_id": faq.faq_id, "question": faq.question},
        message="FAQ创建成功",
    )


@router.put(f"{FAQ_PREFIX}/{{faq_id}}")
async def update_faq(
    faq_id: str,
    req: FAQUpdateRequest,
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """编辑 FAQ（HR专员/管理员）"""
    try:
        faq = await FAQService.update_faq(
            faq_id=faq_id, db_session=db, user_id=current_user.user_id,
            question=req.question, answer=req.answer, category_id=req.category_id,
            related_doc_id=req.related_doc_id, keywords=req.keywords, status=req.status,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=error_response(60001, str(e)))
    return success_response(
        data={"faq_id": faq.faq_id},
        message="FAQ已更新",
    )


@router.delete(f"{FAQ_PREFIX}/{{faq_id}}")
async def delete_faq(
    faq_id: str,
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """删除 FAQ（归档，HR专员/管理员）"""
    try:
        await FAQService.delete_faq(faq_id=faq_id, user_id=current_user.user_id, db_session=db)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=error_response(60001, str(e)))
    return success_response(message="FAQ已删除")
