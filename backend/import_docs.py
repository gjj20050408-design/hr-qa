"""
初始文档导入脚本：读取项目根目录的 .docx 文件，解析→入库 MySQL→分块→向量化→存储 vectors.db

用法: 在项目根目录执行  python backend/import_docs.py
"""
import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# 切换到 backend 目录，确保 .env 能被正确加载
os.chdir(os.path.join(os.path.dirname(__file__)))
sys.path.insert(0, os.getcwd())

import pymysql
from pathlib import Path

# 配置
from app.core.config import settings

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 文档与分类映射
DOC_CONFIGS = [
    {
        "path": PROJECT_ROOT / "福利制度.docx",
        "category_id": "cat_doc_benefit",
        "access_level": "all_roles",
    },
    {
        "path": PROJECT_ROOT / "绩效制度.docx",
        "category_id": "cat_doc_perf",
        "access_level": "all_roles",
    },
]


def parse_docx(file_path: Path) -> str:
    """解析 .docx 文件为 Markdown（保留标题层级、列表、加粗、表格）"""
    from app.providers.docx_parser import parse_docx_to_markdown
    return parse_docx_to_markdown(str(file_path))


def import_to_mysql(conn, doc_id: str, title: str, content: str,
                    category_id: str, access_level: str):
    """将文档写入 MySQL"""
    cursor = conn.cursor()
    try:
        sql = """
            INSERT INTO documents
                (document_id, title, content, category_id, format, version, status,
                 access_level, uploaded_by, file_path, word_count, embedding_status, chunk_count)
            VALUES
                (%s, %s, %s, %s, 'word', '1.0', 'published', %s,
                 'user-admin-001', %s, %s, 'pending', 0)
            ON DUPLICATE KEY UPDATE
                content = VALUES(content), status = 'published',
                word_count = VALUES(word_count), updated_at = NOW()
        """
        file_path = f"/uploads/{title}.docx"
        word_count = len(content)
        cursor.execute(sql, (doc_id, title, content, category_id,
                             access_level, file_path, word_count))

        # 创建版本快照
        from app.models.base import uuid4_str
        version_sql = """
            INSERT INTO document_versions
                (version_id, document_id, version, content_snapshot, change_summary, changed_by)
            VALUES (%s, %s, '1.0', %s, '自动导入', 'user-admin-001')
            ON DUPLICATE KEY UPDATE content_snapshot = VALUES(content_snapshot)
        """
        cursor.execute(version_sql, (uuid4_str(), doc_id, content))
        conn.commit()
        logger.info(f"  MySQL: {title} → documents 表已写入 (word_count={word_count})")
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"  MySQL 写入失败: {e}")
        return False


def vectorize_and_store(doc_id: str, content: str, embedding_provider, vector_store):
    """分块→向量化→存储"""
    from app.providers.vector_store import Chunk as VSChunk
    from app.providers.document_chunker import SemanticChunker

    chunker = SemanticChunker()
    chunks = chunker.split(content, chunk_size=500)

    if not chunks:
        logger.warning("  分块结果为空，跳过")
        return 0

    texts = [c.content for c in chunks]
    logger.info(f"  分块: {len(chunks)} chunks, 开始向量化...")

    embeddings = embedding_provider.embed_batch(texts)
    if not embeddings or not any(e for e in embeddings):
        logger.error("  向量化失败，Embedding API 返回空结果")
        return 0

    vs_chunks = [
        VSChunk(
            chunk_id=c.chunk_id,
            document_id=doc_id,
            content=c.content,
            chunk_index=i,
            token_count=c.token_count,
        )
        for i, c in enumerate(chunks)
    ]
    vector_store.store(vs_chunks, embeddings)
    logger.info(f"  向量化: {len(chunks)} chunks 已存入 vectors.db")
    return len(chunks)


def main():
    # ── 1. 初始化 Embedding Provider ──
    from app.providers.embedding import init_embedding_provider
    emb = init_embedding_provider(
        api_key=settings.EMBEDDING_API_KEY,
        base_url=settings.EMBEDDING_BASE_URL,
        model=settings.EMBEDDING_MODEL,
    )
    logger.info(f"Embedding: {settings.EMBEDDING_MODEL}")

    # ── 2. 初始化 Vector Store ──
    from app.providers.vector_store import init_vector_store, vector_store
    vs = init_vector_store(
        use_local=True,
        local_db_path="./data/vectors.db",
    )
    logger.info(f"VectorStore: local SQLite")

    # ── 3. 连接 MySQL ──
    conn = pymysql.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME,
        charset='utf8mb4',
    )
    logger.info(f"MySQL: {settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}")

    # ── 4. 导入每个文档 ──
    for config in DOC_CONFIGS:
        file_path = config["path"]
        if not file_path.exists():
            logger.warning(f"文件不存在，跳过: {file_path}")
            continue

        title = file_path.stem  # 文件名（不含扩展名）作为标题
        logger.info(f"\n{'='*50}")
        logger.info(f"处理: {title} ({file_path.name})")

        # 解析
        content = parse_docx(file_path)
        logger.info(f"  解析: {len(content)} 字符")

        # 生成固定 document_id
        import hashlib
        doc_id = hashlib.md5(title.encode()).hexdigest()[:16]

        # 写入 MySQL
        if not import_to_mysql(conn, doc_id, title, content,
                               config["category_id"], config["access_level"]):
            continue

        # 清除旧向量（如果存在）
        vs.delete(doc_id)

        # 向量化
        chunk_count = vectorize_and_store(doc_id, content, emb, vs)
        if chunk_count > 0:
            # 更新 embedding_status 和 chunk_count
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE documents SET embedding_status='completed', chunk_count=%s WHERE document_id=%s",
                (chunk_count, doc_id)
            )
            conn.commit()
            logger.info(f"  ✅ {title} 导入完成 ({chunk_count} chunks)")

    # ── 5. 验证 ──
    import sqlite3
    check = sqlite3.connect("./data/vectors.db")
    cnt = check.execute("SELECT COUNT(*) FROM vectors").fetchone()[0]
    logger.info(f"\n{'='*50}")
    logger.info(f"vectors.db 向量总数: {cnt}")
    check.close()

    conn.close()
    logger.info("全部完成！")


if __name__ == "__main__":
    main()
