"""搜索服务 — 中文 LIKE 模糊匹配 + 权限过滤"""
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document
from app.enums.enums import DocStatus
from app.services.qa_chain import PermissionFilter
from app.utils.snippet import generate_snippet


class SearchService:

    @staticmethod
    async def search(
        keyword: str, user_role, db_session: AsyncSession,
        page: int = 1, page_size: int = 20, category_id: str = None,
    ) -> tuple:
        # 用 LIKE 模糊匹配（中文场景比 FULLTEXT 更稳定）
        kw = f"%{keyword}%"
        conditions = [
            Document.status == DocStatus.PUBLISHED,
            or_(
                Document.title.like(kw),
                Document.content.like(kw),
            ),
        ]
        if category_id:
            conditions.append(Document.category_id == category_id)

        # 搜索（预加载 category 关系，避免异步懒加载报错）
        query = select(Document).options(selectinload(Document.category)).where(*conditions)
        result = await db_session.execute(query)
        docs = result.scalars().all()

        # 权限过滤
        allowed, filtered = await PermissionFilter.filter_documents(docs, user_role)

        # 分页
        total = len(allowed)
        start = (page - 1) * page_size
        paged = allowed[start:start + page_size]

        # 生成高亮摘要
        items = []
        for doc in paged:
            snippet = generate_snippet(doc.content, keyword)
            items.append({
                "document_id": doc.document_id,
                "title": doc.title,
                "snippet": snippet,
                "category": doc.category.name if doc.category else "",
                "category_id": doc.category_id,
                "version": doc.version,
                "access_level": doc.access_level.value if doc.access_level else "",
                "published_at": str(doc.published_at) if doc.published_at else None,
            })

        return items, total, len(filtered)

