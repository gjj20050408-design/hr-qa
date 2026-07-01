import asyncio
from app.core.database import async_session_factory
from app.services.document_service import DocumentService
from app.models.document import Document
from app.enums.enums import DocStatus
from sqlalchemy import select, text

async def main():
    async with async_session_factory() as db:
        # 找一个已归档文档
        r = await db.execute(text("SELECT document_id, status, title FROM documents WHERE status='ARCHIVED' LIMIT 1"))
        row = r.fetchone()
        print("raw archived row:", row)
        if not row:
            print("没有已归档文档")
            return
        doc_id = row[0]

        # ORM 读出来看 status 枚举解析
        doc = await db.get(Document, doc_id)
        print("ORM status =", repr(doc.status), "| == ARCHIVED?", doc.status == DocStatus.ARCHIVED)

        # 调用 restore_service
        try:
            restored = await DocumentService.restore_document(doc_id, "user-admin-001", db)
            print("restore OK -> status =", repr(restored.status))
            await db.rollback()  # 不真正改库，回滚
            print("(已回滚，不影响数据)")
        except Exception as e:
            print("restore FAILED:", type(e).__name__, e)

asyncio.run(main())
