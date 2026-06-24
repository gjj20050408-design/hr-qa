"""文档异步处理任务"""
from app.tasks.celery_app import celery_app
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=10)
def parse_document(self, document_id: str, file_path: str, file_format: str):
    """异步解析上传的文档内容"""
    logger.info(f"Starting document parse: {document_id}")
    try:
        if file_format == "pdf":
            from PyPDF2 import PdfReader
            reader = PdfReader(file_path)
            content = "\n".join(page.extract_text() or "" for page in reader.pages)
        elif file_format == "word":
            from docx import Document as DocxDoc
            doc = DocxDoc(file_path)
            content = "\n".join(p.text for p in doc.paragraphs)
        elif file_format == "markdown":
            import markdown
            with open(file_path, "r", encoding="utf-8") as f:
                raw = f.read()
            # 提取纯文本
            from html.parser import HTMLParser
            html = markdown.markdown(raw)
            parser = HTMLParser()
            # 简化处理：移除HTML标签
            import re
            content = re.sub(r'<[^>]+>', '', html)
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

        # TODO: 更新数据库中文档内容
        logger.info(f"Document parsed successfully: {document_id}, length={len(content)}")
        return {"document_id": document_id, "word_count": len(content)}
    except Exception as e:
        logger.error(f"Document parse failed: {document_id}, error={e}")
        self.retry(exc=e)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def generate_embeddings(self, document_id: str):
    """二期：异步生成文档向量嵌入"""
    logger.info(f"Starting embedding generation: {document_id}")
    # TODO: 二期实现
    return {"document_id": document_id, "status": "pending"}
