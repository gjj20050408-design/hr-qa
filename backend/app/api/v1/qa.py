"""问答接口路由 — /api/v1/search, /api/v1/qa/*, /api/v1/faqs/*"""
import time
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_hr_plus, require_admin
from app.core.redis import get_redis, rate_limit_check
from app.core.config import settings
from app.schemas.qa import (
    AskQuestionRequest, FeedbackRequest, FavoriteToggleRequest,
)
from app.schemas.response import success_response, error_response, list_response
from app.schemas.faq import FAQCreateRequest, FAQUpdateRequest
from app.services.qa_chain import qa_orchestrator, build_response
from app.services.qa_service import QAService
from app.services.search_service import SearchService
from app.services.faq_service import FAQService
from app.models.base import uuid4_str
from app.enums.constants import QA_THRESHOLDS

router = APIRouter(tags=["搜索与问答"])


# ── 搜索 ──

@router.get("/search")
async def search(
    keyword: str = Query(..., min_length=1, max_length=100),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """全文搜索（含权限过滤）"""
    # 限流
    try:
        allowed = await rate_limit_check(
            f"rate:search:{current_user.user_id}",
            settings.RATE_LIMIT_SEARCH_PER_MINUTE,
        )
        if not allowed:
            raise HTTPException(status_code=429, detail=error_response(90003, "搜索频率超限，请稍后再试"))
    except HTTPException:
        raise
    except Exception:
        pass

    items, total, filtered_count = await SearchService.search(
        keyword=keyword,
        user_role=current_user.role,
        db_session=db,
        page=page,
        page_size=page_size,
        category_id=category_id,
    )

    resp = list_response(items=items, page=page, page_size=page_size, total=total)
    if filtered_count > 0:
        resp["data"]["notice"] = f"🔒 {filtered_count}篇相关制度需要更高权限才能查看"
    return resp


# ── 问答 ──

@router.post("/qa/ask")
async def ask_question(
    req: AskQuestionRequest,
    request: Request,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """提交问题（完整策略链）"""
    # 限流
    try:
        allowed = await rate_limit_check(
            f"rate:qa:{current_user.user_id}",
            settings.RATE_LIMIT_QNA_PER_MINUTE,
        )
        if not allowed:
            raise HTTPException(status_code=429, detail=error_response(40002, "提问频率超限，请稍后再试"))
    except HTTPException:
        raise
    except Exception:
        pass

    # 生成或使用现有 session_id
    session_id = req.session_id or uuid4_str()

    # 执行策略链
    start_time = time.time()
    ctx = await qa_orchestrator.ask(
        question=req.question,
        user=current_user,
        session_id=session_id,
        db_session=db,
    )
    elapsed_ms = int((time.time() - start_time) * 1000)

    # 保存记录
    record = await QAService.save_record(
        user_id=current_user.user_id,
        session_id=session_id,
        question=ctx.question,
        answer=ctx.answer,
        answer_type=ctx.answer_type.value if ctx.answer_type else "no_result",
        confidence=ctx.confidence,
        reference_docs=ctx.reference_docs,
        response_time_ms=elapsed_ms,
        db_session=db,
    )

    response = build_response(ctx)
    response["record_id"] = record.record_id
    response["response_time_ms"] = elapsed_ms
    return success_response(data=response)


@router.post("/qa/sessions")
async def create_session(current_user=Depends(get_current_user)):
    """创建新对话会话"""
    session_id = uuid4_str()
    return success_response(data={"session_id": session_id}, message="会话已创建")


@router.get("/qa/sessions")
async def list_sessions(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取用户的会话列表"""
    sessions = await QAService.get_sessions(current_user.user_id, db)
    return success_response(data={"items": sessions})


@router.patch("/qa/sessions/{session_id}/title")
async def rename_session(
    session_id: str,
    req: dict,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """重命名会话"""
    try:
        session = await QAService.rename_session(
            session_id=session_id, user_id=current_user.user_id,
            title=req.get("title", ""), db_session=db,
        )
        return success_response(data={"session_id": session.session_id, "title": session.title})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=error_response(90001, str(e)))


@router.patch("/qa/sessions/{session_id}/pin")
async def toggle_pin_session(
    session_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """切换会话置顶状态"""
    try:
        session = await QAService.toggle_pin_session(
            session_id=session_id, user_id=current_user.user_id, db_session=db,
        )
        return success_response(data={"session_id": session.session_id, "is_pinned": session.is_pinned})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=error_response(90001, str(e)))


@router.delete("/qa/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除会话及其所有问答记录"""
    try:
        await QAService.delete_session(
            session_id=session_id, user_id=current_user.user_id, db_session=db,
        )
        return success_response(message="会话已删除")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=error_response(90001, str(e)))


@router.get("/qa/records")
async def get_qa_records(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session_id: Optional[str] = None,
    answer_type: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """我的问答历史"""
    records, total = await QAService.get_user_records(
        user_id=current_user.user_id,
        db_session=db,
        page=page,
        page_size=page_size,
        session_id=session_id,
        answer_type=answer_type,
    )
    items = [
        {
            "record_id": r.record_id,
            "session_id": r.session_id,
            "question": r.question,
            "answer": r.answer,
            "answer_type": r.answer_type.value if r.answer_type else None,
            "confidence": r.confidence,
            "reference_docs": r.reference_docs,
            "response_time_ms": r.response_time_ms,
            "feedback": r.feedback.value if r.feedback else None,
            "is_favorite": r.is_favorite,
            "created_at": str(r.created_at) if r.created_at else None,
        }
        for r in records
    ]
    return list_response(items=items, page=page, page_size=page_size, total=total)


@router.patch("/qa/records/{record_id}/favorite")
async def toggle_favorite(
    record_id: str,
    req: FavoriteToggleRequest,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """切换收藏状态"""
    try:
        record = await QAService.toggle_favorite(
            record_id=record_id,
            user_id=current_user.user_id,
            is_favorite=req.is_favorite,
            db_session=db,
        )
        return success_response(data={"record_id": record.record_id, "is_favorite": record.is_favorite})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=error_response(90001, str(e)))


@router.get("/qa/stats")
async def get_qa_stats(
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """个人问答统计"""
    stats = await QAService.get_user_stats(current_user.user_id, db)
    return success_response(data=stats)


# ── 反馈 ──

@router.post("/feedback")
async def submit_feedback(
    record_id: str = Query(...),
    feedback: str = Query(...),
    reason: Optional[str] = Query(None, max_length=500),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """提交答案反馈"""
    try:
        record = await QAService.submit_feedback(
            record_id=record_id,
            user_id=current_user.user_id,
            feedback=feedback,
            reason=reason,
            db_session=db,
        )
        return success_response(data={
            "record_id": record.record_id,
            "feedback": record.feedback.value,
        }, message="反馈已提交")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=error_response(50001, str(e)))


# ── FAQ 管理 ──

@router.get("/faqs")
async def list_faqs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category_id: Optional[str] = None,
    keyword: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """FAQ列表"""
    faqs, total = await FAQService.get_faqs(
        db_session=db, page=page, page_size=page_size,
        category_id=category_id, keyword=keyword,
    )
    items = [
        {
            "faq_id": f.faq_id,
            "question": f.question,
            "answer": f.answer,
            "category_id": f.category_id,
            "category_name": f.category.name if f.category else None,
            "related_doc_id": f.related_doc_id,
            "keywords": f.keywords,
            "view_count": f.view_count,
            "status": f.status.value if f.status else None,
            "created_at": str(f.created_at) if f.created_at else None,
            "updated_at": str(f.updated_at) if f.updated_at else None,
        }
        for f in faqs
    ]
    return list_response(items=items, page=page, page_size=page_size, total=total)


@router.post("/faqs")
async def create_faq(
    req: FAQCreateRequest,
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """创建FAQ"""
    faq = await FAQService.create_faq(
        question=req.question, answer=req.answer,
        category_id=req.category_id, created_by=current_user.user_id,
        related_doc_id=req.related_doc_id, keywords=req.keywords,
        db_session=db,
    )
    return success_response(data={"faq_id": faq.faq_id, "question": faq.question}, message="FAQ创建成功")


@router.put("/faqs/{faq_id}")
async def update_faq(
    faq_id: str,
    req: FAQUpdateRequest,
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """更新FAQ"""
    try:
        faq = await FAQService.update_faq(
            faq_id=faq_id, db_session=db, user_id=current_user.user_id,
            question=req.question, answer=req.answer,
            category_id=req.category_id, related_doc_id=req.related_doc_id,
            keywords=req.keywords, status=req.status,
        )
        return success_response(data={"faq_id": faq.faq_id}, message="FAQ更新成功")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=error_response(90002, str(e)))


@router.delete("/faqs/{faq_id}")
async def delete_faq(
    faq_id: str,
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """删除（归档）FAQ"""
    try:
        await FAQService.delete_faq(faq_id, current_user.user_id, db)
        return success_response(message="FAQ已归档")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=error_response(90002, str(e)))
