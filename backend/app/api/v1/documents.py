"""文档管理接口路由 — /api/v1/documents/* 和 /api/v1/categories/*"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user, require_hr_plus, require_admin
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
                    from app.providers.docx_parser import parse_docx_to_markdown
                    content = parse_docx_to_markdown(file_content)
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
            "has_access": d.can_access(current_user.role),
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
        # 权限检查：无访问权限的用户只能看到有限元数据
        has_access = doc.can_access(current_user.role)
        response_data = {
            "document_id": doc.document_id,
            "title": doc.title,
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
            "has_access": has_access,
            "published_at": str(doc.published_at) if doc.published_at else None,
            "created_at": str(doc.created_at) if doc.created_at else None,
            "updated_at": str(doc.updated_at) if doc.updated_at else None,
        }
        # 无权限时隐藏正文内容
        if has_access:
            response_data["content"] = doc.content
        else:
            response_data["content"] = "🔒 该内容需要HR权限才能查看。如有疑问，请联系HR部门（hr@company.com）"
        return success_response(data=response_data)
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


@router.post(f"{DOC_PREFIX}/{{document_id}}/publish")
async def publish_document(
    document_id: str,
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """发布文档并触发向量化"""
    import logging
    logger = logging.getLogger(__name__)

    from app.models.document import Document
    from app.enums.enums import DocStatus

    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail=error_response(30001, "文档不存在"))

    # 状态检查
    if doc.status != DocStatus.DRAFT:
        raise HTTPException(status_code=400, detail=error_response(30002, "只有草稿状态的文档可以发布"))

    try:
        # 1. 发布文档
        doc.publish()

        # 2. 分块
        from app.providers.vector_store import document_chunker, vector_store
        from app.providers.embedding import embedding_provider
        from app.providers.vector_store import Chunk as VSChunk

        chunks = document_chunker.split(doc.content, chunk_size=500)
        if not chunks:
            raise ValueError("文档内容为空，无法分块")

        logger.info(f"Document {document_id}: split into {len(chunks)} chunks")

        # 3. 向量化
        texts = [c.content for c in chunks]
        embeddings = embedding_provider.embed_batch(texts)

        valid_embeddings = any(e for e in embeddings)
        if not valid_embeddings:
            raise ValueError("向量化失败，Embedding API 返回空结果")

        logger.info(f"Document {document_id}: generated {len(embeddings)} embeddings")

        # 4. 存入向量库
        vs_chunks = [
            VSChunk(
                chunk_id=c.chunk_id,
                document_id=document_id,
                content=c.content,
                chunk_index=i,
                token_count=c.token_count,
            )
            for i, c in enumerate(chunks)
        ]
        vector_store.store(vs_chunks, embeddings)

        # 5. 更新文档元数据
        doc.embedding_status = "completed"
        doc.chunk_count = len(chunks)

        await db.flush()
        logger.info(f"Document {document_id}: published with {len(chunks)} chunks vectorized")

        return success_response(data={
            "document_id": doc.document_id,
            "title": doc.title,
            "status": doc.status.value,
            "chunk_count": doc.chunk_count,
            "embedding_status": doc.embedding_status,
        }, message="文档发布成功，向量化完成")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=error_response(30002, str(e)))
    except Exception as e:
        logger.error(f"Publish failed for document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=error_response(90001, f"发布失败: {str(e)}"))


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


@router.post(f"{DOC_PREFIX}/{{document_id}}/restore")
async def restore_document(
    document_id: str,
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """恢复已归档文档（恢复为草稿，需重新发布以更新向量化）"""
    try:
        doc = await DocumentService.restore_document(document_id, current_user.user_id, db)
        return success_response(
            data={"document_id": doc.document_id, "status": doc.status.value},
            message="文档已恢复为草稿，请重新发布以更新检索数据",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=error_response(30001, str(e)))


@router.delete(f"{DOC_PREFIX}/{{document_id}}/permanent")
async def delete_document(
    document_id: str,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """彻底删除文档（物理删除，含版本/分块/向量索引，不可恢复，仅管理员）"""
    try:
        title = await DocumentService.delete_document(document_id, current_user.user_id, db)
        return success_response(data={"document_id": document_id}, message=f"文档「{title}」已彻底删除")
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


@router.get(f"{DOC_PREFIX}/{{document_id}}/versions/diff")
async def diff_document_versions(
    document_id: str,
    version_id_1: str = Query(..., description="第一个版本ID"),
    version_id_2: str = Query(..., description="第二个版本ID"),
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """对比两个文档版本的差异"""
    from app.models.document_sub import DocumentVersion
    import difflib

    # 查询两个版本
    v1_result = await db.execute(
        select(DocumentVersion).where(
            DocumentVersion.version_id == version_id_1,
            DocumentVersion.document_id == document_id,
        )
    )
    v1 = v1_result.scalars().first()
    if not v1:
        raise HTTPException(status_code=404, detail=error_response(30001, f"版本 {version_id_1} 不存在"))

    v2_result = await db.execute(
        select(DocumentVersion).where(
            DocumentVersion.version_id == version_id_2,
            DocumentVersion.document_id == document_id,
        )
    )
    v2 = v2_result.scalars().first()
    if not v2:
        raise HTTPException(status_code=404, detail=error_response(30001, f"版本 {version_id_2} 不存在"))

    text1 = v1.content_snapshot or ""
    text2 = v2.content_snapshot or ""

    # 字符级统计
    added_chars = max(0, len(text2) - len(text1))
    deleted_chars = max(0, len(text1) - len(text2))

    # 逐行对比
    lines1 = text1.splitlines()
    lines2 = text2.splitlines()
    differ = difflib.unified_diff(lines1, lines2, fromfile=f"v{v1.version}", tofile=f"v{v2.version}", lineterm="")
    diff_lines = list(differ)

    summary_parts = []
    if added_chars > 0:
        summary_parts.append(f"新增{added_chars}字符")
    if deleted_chars > 0:
        summary_parts.append(f"删除{deleted_chars}字符")
    if not summary_parts:
        summary_parts.append("内容无变化")

    return success_response(data={
        "version_1": v1.version,
        "version_2": v2.version,
        "summary": " / ".join(summary_parts),
        "diff": diff_lines,
    })


@router.put(f"{DOC_PREFIX}/{{document_id}}/file")
async def update_document_file(
    document_id: str,
    title: str = Form(None),
    version_note: Optional[str] = Form(None),
    file: UploadFile = File(...),
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """上传新文件替换文档内容（版本号自动递增）"""
    from app.models.document import Document

    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail=error_response(30001, "文档不存在"))

    try:
        # 根据文件格式解析内容
        file_content = await file.read()
        content = ""
        ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""

        format_map = {"pdf": "pdf", "doc": "word", "docx": "word", "md": "markdown", "html": "html", "txt": "txt"}
        fmt = format_map.get(ext, "markdown")

        if fmt in ("markdown", "html", "txt"):
            content = file_content.decode("utf-8", errors="ignore")
        elif fmt == "pdf":
            try:
                from io import BytesIO
                from PyPDF2 import PdfReader
                reader = PdfReader(BytesIO(file_content))
                content = "\n".join(page.extract_text() or "" for page in reader.pages)
            except Exception:
                content = f"[PDF文件: {file.filename}]"
        elif fmt == "word":
            try:
                from app.providers.docx_parser import parse_docx_to_markdown
                content = parse_docx_to_markdown(file_content)
            except Exception:
                content = f"[Word文件: {file.filename}]"

        if not content.strip():
            raise ValueError("文件内容为空，无法解析")

        # 更新文档
        updated = await DocumentService.update_document(
            document_id=document_id,
            db_session=db,
            title=title,
            content=content,
            version_note=version_note or f"文件更新: {file.filename}",
            changed_by=current_user.user_id,
        )

        # 如果文档之前已发布，重置为草稿状态以便重新向量化
        from app.enums.enums import DocStatus
        if updated.status == DocStatus.PUBLISHED:
            from app.providers.vector_store import vector_store
            vector_store.delete(document_id)

        updated.status = DocStatus.DRAFT
        updated.embedding_status = "pending"
        updated.file_path = f"/uploads/{file.filename}"
        await db.flush()

        return success_response(data={
            "document_id": updated.document_id,
            "title": updated.title,
            "version": updated.version,
            "status": updated.status.value,
            "word_count": updated.word_count,
        }, message="文件已替换，请重新发布以更新向量化数据")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=error_response(30002, str(e)))


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
    if req.access_level not in [a.value for a in AccessLevel]:
        raise HTTPException(status_code=400, detail=error_response(90001, f"无效的权限级别: {req.access_level}"))
    category = Category(
        category_id=uuid4_str(),
        name=req.name,
        parent_id=req.parent_id,
        type=CategoryType(req.type),
        access_level=AccessLevel(req.access_level),
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
    from app.enums.enums import AccessLevel, DocAccessLevel
    from app.models.document import Document
    from sqlalchemy import func

    cat = await db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail=error_response(90002, "分类不存在"))

    if req.access_level in [a.value for a in AccessLevel]:
        cat.access_level = AccessLevel(req.access_level)

    await db.flush()

    # 级联统计：cascade=True 时统计并批量更新该分类下 inherit 文档
    affected_docs = 0
    if req.cascade:
        count_result = await db.execute(
            select(func.count(Document.document_id)).where(
                Document.category_id == category_id,
                Document.access_level == DocAccessLevel.INHERIT,
            )
        )
        affected_docs = count_result.scalar() or 0
        # 批量更新 inherit 文档的 updated_at，触发前端感知权限变更
        if affected_docs > 0:
            from sqlalchemy import update
            update_query = (
                update(Document)
                .where(
                    Document.category_id == category_id,
                    Document.access_level == DocAccessLevel.INHERIT,
                )
                .values(updated_at=func.now())
            )
            await db.execute(update_query)

    return success_response(data={
        "category_id": cat.category_id,
        "access_level": cat.access_level.value,
        "affected_docs": affected_docs,
    }, message="分类权限更新成功")


@router.put(f"{CAT_PREFIX}/{{category_id}}")
async def update_category(
    category_id: str,
    name: str = Query(..., min_length=1, max_length=100, description="分类名称"),
    parent_id: Optional[str] = Query(None, description="上级分类ID"),
    sort_order: int = Query(0, description="排序"),
    current_user=Depends(require_hr_plus),
    db: AsyncSession = Depends(get_db),
):
    """更新分类信息"""
    cat = await db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail=error_response(90002, "分类不存在"))

    cat.name = name
    if parent_id is not None:
        # 检查父分类是否存在
        if parent_id != "":
            parent = await db.get(Category, parent_id)
            if not parent:
                raise HTTPException(status_code=400, detail=error_response(90002, "父分类不存在"))
            # 防止循环引用
            if parent_id == category_id:
                raise HTTPException(status_code=400, detail=error_response(90002, "不能将分类设为自己的子分类"))
            cat.parent_id = parent_id
        else:
            cat.parent_id = None
    cat.sort_order = sort_order
    await db.flush()
    return success_response(data={
        "category_id": cat.category_id,
        "name": cat.name,
        "parent_id": cat.parent_id,
        "sort_order": cat.sort_order,
    }, message="分类更新成功")


@router.delete(f"{CAT_PREFIX}/{{category_id}}")
async def delete_category(
    category_id: str,
    current_user=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """删除分类（需检查关联文档和子分类）"""
    from app.models.document import Document

    cat = await db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail=error_response(90002, "分类不存在"))

    # 检查是否有关联文档
    doc_result = await db.execute(
        select(Document).where(Document.category_id == category_id).limit(1)
    )
    if doc_result.scalars().first():
        raise HTTPException(
            status_code=409,
            detail=error_response(90003, "该分类下存在关联文档，无法删除"),
        )

    # 检查是否有子分类
    child_result = await db.execute(
        select(Category).where(Category.parent_id == category_id).limit(1)
    )
    if child_result.scalars().first():
        raise HTTPException(
            status_code=409,
            detail=error_response(90004, "该分类下存在子分类，无法删除"),
        )

    await db.delete(cat)
    await db.commit()
    return success_response(data={"category_id": category_id}, message="分类删除成功")
