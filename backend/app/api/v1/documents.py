"""文档管理接口路由 — /api/v1/documents/* 和 /api/v1/categories/*"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_hr_plus
from app.schemas.document import (
    DocumentUpdateRequest, DocumentAccessUpdateRequest,
)
from app.schemas.category import (
    CategoryCreateRequest, CategoryAccessUpdateRequest,
)
from app.schemas.response import success_response, error_response, list_response
from app.services.document_service import DocumentService
from app.models.category import Category
from sqlalchemy import select

router = APIRouter(tags=["文档与分类管理"])

DOC_PREFIX = "/documents"
CAT_PREFIX = "/categories"


# ── 文档 CRUD ──

@router.post(f"{DOC_PREFIX}")
async def create_document(
    title: str = Form(...),
    category_id: str = Form(...),
    format: str = Form(...),
    access_level: str = Form(default="inherit"),
    version_note: Optional[str] = Form(None),
    file: UploadFile = File(None),
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """上传文档"""
    try:
        content = ""
        file_path = ""
        if file:
            file_content = await file.read()
            if format in ("markdown", "html", "txt"):
                content = file_content.decode("utf-8", errors="ignore")
            elif format == "pdf":
                try:
                    from io import BytesIO
                    from PyPDF2 import PdfReader
                    reader = PdfReader(BytesIO(file_content))
                    content = "\n".join(page.extract_text() or "" for page in reader.pages)
                except Exception:
                    content = f"[PDF文件: {file.filename}]"
            elif format == "word":
                try:
                    from io import BytesIO
                    from docx import Document as DocxDoc
                    doc = DocxDoc(BytesIO(file_content))
                    content = "\n".join(p.text for p in doc.paragraphs)
                except Exception:
                    content = f"[Word文件: {file.filename}]"
            file_path = f"/uploads/{file.filename}"

        doc = await DocumentService.create_document(
            title=title, content=content, category_id=category_id,
            format=format, uploaded_by=current_user.user_id,
            file_path=file_path or f"/manual/{title}",
            access_level=access_level, version_note=version_note,
            db_session=db,
        )
        return success_response(data={
            "document_id": doc.document_id,
            "title": doc.title,
            "status": doc.status.value,
            "version": doc.version,
            "word_count": doc.word_count,
        }, message="文档创建成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=error_response(30002, str(e)))


@router.get(f"{DOC_PREFIX}")
async def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    category_id: Optional[str] = None,
    keyword: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """文档列表"""
    docs, total = await DocumentService.get_documents(
        db_session=db, page=page, page_size=page_size,
        status=status, category_id=category_id, keyword=keyword,
    )
    items = [
        {
            "document_id": d.document_id,
            "title": d.title,
            "category_id": d.category_id,
            "category_name": d.category.name if d.category else None,
            "format": d.format.value if d.format else None,
            "version": d.version,
            "version_note": d.version_note,
            "status": d.status.value if d.status else None,
            "access_level": d.access_level.value if d.access_level else None,
            "word_count": d.word_count,
            "chunk_count": d.chunk_count,
            "embedding_status": d.embedding_status,
            "published_at": str(d.published_at) if d.published_at else None,
            "created_at": str(d.created_at) if d.created_at else None,
            "updated_at": str(d.updated_at) if d.updated_at else None,
            "uploader_name": d.uploader.name if d.uploader else None,
        }
        for d in docs
    ]
    return list_response(items=items, page=page, page_size=page_size, total=total)


@router.get(f"{DOC_PREFIX}/{{document_id}}")
async def get_document(
    document_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """文档详情"""
    try:
        doc = await DocumentService.get_document_detail(document_id, db)
        return success_response(data={
            "document_id": doc.document_id,
            "title": doc.title,
            "content": doc.content,
            "category_id": doc.category_id,
            "category_name": doc.category.name if doc.category else None,
            "format": doc.format.value,
            "version": doc.version,
            "version_note": doc.version_note,
            "status": doc.status.value,
            "access_level": doc.access_level.value,
            "uploaded_by": doc.uploaded_by,
            "uploader_name": doc.uploader.name if doc.uploader else None,
            "file_path": doc.file_path,
            "word_count": doc.word_count,
            "chunk_count": doc.chunk_count,
            "embedding_status": doc.embedding_status,
            "published_at": str(doc.published_at) if doc.published_at else None,
            "created_at": str(doc.created_at) if doc.created_at else None,
            "updated_at": str(doc.updated_at) if doc.updated_at else None,
        })
    except ValueError as e:
        raise HTTPException(status_code=404, detail=error_response(30001, str(e)))


@router.put(f"{DOC_PREFIX}/{{document_id}}")
async def update_document(
    document_id: str,
    req: DocumentUpdateRequest,
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """更新文档"""
    try:
        doc = await DocumentService.update_document(
            document_id=document_id,
            db_session=db,
            title=req.title,
            content=req.content,
            category_id=req.category_id,
            access_level=req.access_level,
            version_note=req.version_note,
            changed_by=current_user.user_id,
        )
        return success_response(data={
            "document_id": doc.document_id,
            "title": doc.title,
            "version": doc.version,
            "status": doc.status.value,
        }, message="文档更新成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=error_response(30001, str(e)))


@router.delete(f"{DOC_PREFIX}/{{document_id}}")
async def archive_document(
    document_id: str,
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """归档文档"""
    try:
        doc = await DocumentService.archive_document(document_id, current_user.user_id, db)
        return success_response(data={"document_id": doc.document_id, "status": doc.status.value}, message="文档已归档")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=error_response(30001, str(e)))


@router.get(f"{DOC_PREFIX}/{{document_id}}/versions")
async def get_document_versions(
    document_id: str,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """文档版本历史"""
    versions = await DocumentService.get_document_versions(document_id, db)
    items = [
        {
            "version_id": v.version_id,
            "document_id": v.document_id,
            "version": v.version,
            "change_summary": v.change_summary,
            "changed_by": v.changed_by,
            "changer_name": v.changer.name if v.changer else None,
            "created_at": str(v.created_at) if v.created_at else None,
        }
        for v in versions
    ]
    return success_response(data={"items": items})


@router.patch(f"{DOC_PREFIX}/{{document_id}}/access")
async def update_document_access(
    document_id: str,
    req: DocumentAccessUpdateRequest,
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """更新文档访问权限"""
    try:
        doc = await DocumentService.update_document(
            document_id=document_id, db_session=db,
            access_level=req.access_level,
            changed_by=current_user.user_id,
        )
        return success_response(data={
            "document_id": doc.document_id,
            "access_level": doc.access_level.value,
        }, message="权限更新成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=error_response(30001, str(e)))


# ── 分类管理 ──

@router.get(f"{CAT_PREFIX}")
async def list_categories(
    type: Optional[str] = None,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """分类树列表"""
    conditions = []
    from app.enums.enums import CategoryType
    if type and type in [t.value for t in CategoryType]:
        conditions.append(Category.type == CategoryType(type))

    query = select(Category)
    for c in conditions:
        query = query.where(c)

    result = await db.execute(query)
    categories = result.scalars().all()

    # 构建树
    cat_map = {}
    for cat in categories:
        cat_map[cat.category_id] = {
            "category_id": cat.category_id,
            "name": cat.name,
            "parent_id": cat.parent_id,
            "type": cat.type.value if cat.type else None,
            "access_level": cat.access_level.value if cat.access_level else None,
            "sort_order": cat.sort_order,
            "children": [],
        }

    roots = []
    for cat_id, node in cat_map.items():
        parent_id = node.get("parent_id")
        if parent_id and parent_id in cat_map:
            cat_map[parent_id]["children"].append(node)
        else:
            roots.append(node)

    return success_response(data={"items": roots})


@router.post(f"{CAT_PREFIX}")
async def create_category(
    req: CategoryCreateRequest,
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """创建分类"""
    from app.models.base import uuid4_str
    from app.enums.enums import CategoryType, AccessLevel
    category = Category(
        category_id=uuid4_str(),
        name=req.name,
        parent_id=req.parent_id,
        type=CategoryType(req.type),
        access_level=AccessLevel(req.access_level) if req.access_level in [a.value for a in AccessLevel] else AccessLevel.ALL_ROLES,
        sort_order=req.sort_order,
    )
    db.add(category)
    await db.flush()
    return success_response(data={
        "category_id": category.category_id,
        "name": category.name,
    }, message="分类创建成功")


@router.patch(f"{CAT_PREFIX}/{{category_id}}/access")
async def update_category_access(
    category_id: str,
    req: CategoryAccessUpdateRequest,
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """设置分类默认访问权限"""
    from app.enums.enums import AccessLevel
    cat = await db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail=error_response(90002, "分类不存在"))

    if req.access_level in [a.value for a in AccessLevel]:
        cat.access_level = AccessLevel(req.access_level)

    await db.flush()
    return success_response(data={
        "category_id": cat.category_id,
        "access_level": cat.access_level.value,
    }, message="分类权限更新成功")
