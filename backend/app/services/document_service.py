"""文档管理服务"""
from typing import Optional
from datetime import datetime
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document
from app.models.document_sub import DocumentVersion
from app.models.category import Category
from app.models.audit_log import AuditLog
from app.models.base import uuid4_str
from app.enums.enums import DocStatus, DocFormat, DocAccessLevel


class DocumentService:

    @staticmethod
    async def create_document(
        title: str, content: str, category_id: str, format: str,
        uploaded_by: str, file_path: str,
        access_level: str = "inherit", version_note: str = None,
        db_session: AsyncSession = None,
    ) -> Document:
        doc = Document(
            document_id=uuid4_str(),
            title=title,
            content=content,
            category_id=category_id,
            format=DocFormat(format) if format in [f.value for f in DocFormat] else DocFormat.MARKDOWN,
            version="1.0",
            version_note=version_note,
            status=DocStatus.DRAFT,
            access_level=DocAccessLevel(access_level) if access_level in [a.value for a in DocAccessLevel] else DocAccessLevel.INHERIT,
            uploaded_by=uploaded_by,
            file_path=file_path,
            word_count=len(content),
        )
        db_session.add(doc)

        # 创建初始版本快照
        version = DocumentVersion(
            version_id=uuid4_str(),
            document_id=doc.document_id,
            version="1.0",
            content_snapshot=content,
            change_summary=version_note or "初始版本",
            changed_by=uploaded_by,
        )
        db_session.add(version)

        # 审计日志
        audit = AuditLog(
            log_id=uuid4_str(), user_id=uploaded_by,
            action="document_create", resource_type="document",
            resource_id=doc.document_id,
            detail={"title": title, "format": format},
        )
        db_session.add(audit)
        await db_session.flush()
        return doc

    @staticmethod
    async def get_documents(
        db_session: AsyncSession, page: int = 1, page_size: int = 20,
        status: str = None, category_id: str = None, keyword: str = None,
    ) -> tuple:
        conditions = []
        if status and status in [s.value for s in DocStatus]:
            conditions.append(Document.status == DocStatus(status))
        if category_id:
            conditions.append(Document.category_id == category_id)
        if keyword:
            conditions.append(Document.title.contains(keyword))

        query = select(Document)
        for c in conditions:
            query = query.where(c)

        # 总数
        count_query = select(func.count(Document.document_id))
        for c in conditions:
            count_query = count_query.where(c)
        result = await db_session.execute(count_query)
        total = result.scalar() or 0

        # 分页
        query = query.order_by(desc(Document.updated_at)).offset((page - 1) * page_size).limit(page_size)
        result = await db_session.execute(query)
        docs = result.scalars().all()

        return docs, total

    @staticmethod
    async def update_document(
        document_id: str, db_session: AsyncSession,
        title: str = None, content: str = None, category_id: str = None,
        access_level: str = None, version_note: str = None, changed_by: str = None,
    ) -> Document:
        doc = await db_session.get(Document, document_id)
        if not doc:
            raise ValueError("文档不存在")

        old_content = doc.content

        if title:
            doc.title = title
        if content:
            doc.content = content
            doc.word_count = len(content)
        if category_id:
            doc.category_id = category_id
        if access_level and access_level in [a.value for a in DocAccessLevel]:
            doc.access_level = DocAccessLevel(access_level)

        # 版本号自增
        if content:
            parts = doc.version.split(".")
            parts[-1] = str(int(parts[-1]) + 1)
            doc.version = ".".join(parts)

            # 创建版本快照
            version = DocumentVersion(
                version_id=uuid4_str(),
                document_id=doc.document_id,
                version=doc.version,
                content_snapshot=content,
                change_summary=version_note or "内容更新",
                changed_by=changed_by,
            )
            db_session.add(version)

        doc.version_note = version_note

        # 审计日志
        audit = AuditLog(
            log_id=uuid4_str(), user_id=changed_by,
            action="document_update", resource_type="document",
            resource_id=doc.document_id,
            detail={"title": doc.title},
        )
        db_session.add(audit)
        await db_session.flush()
        return doc

    @staticmethod
    async def get_document_detail(document_id: str, db_session: AsyncSession) -> Document:
        from sqlalchemy.orm import selectinload
        from sqlalchemy import select
        result = await db_session.execute(
            select(Document)
            .options(selectinload(Document.category), selectinload(Document.uploader))
            .where(Document.document_id == document_id)
        )
        doc = result.scalar_one_or_none()
        if not doc:
            raise ValueError("文档不存在")
        return doc

    @staticmethod
    async def get_document_versions(document_id: str, db_session: AsyncSession) -> list:
        result = await db_session.execute(
            select(DocumentVersion)
            .where(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.created_at.desc())
        )
        return result.scalars().all()

    @staticmethod
    async def archive_document(document_id: str, user_id: str, db_session: AsyncSession) -> Document:
        doc = await db_session.get(Document, document_id)
        if not doc:
            raise ValueError("文档不存在")
        doc.archive()

        audit = AuditLog(
            log_id=uuid4_str(), user_id=user_id,
            action="document_archive", resource_type="document",
            resource_id=document_id,
        )
        db_session.add(audit)
        await db_session.flush()
        return doc
