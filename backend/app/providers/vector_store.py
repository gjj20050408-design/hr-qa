"""VectorStore 抽象接口（支持 ChromaDB 与本地 SQLite 持久化）"""
import json
import logging
import sqlite3
import threading
from pathlib import Path
from typing import Protocol, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    content: str
    chunk_index: int = 0
    token_count: int = 0
    embedding: List[float] = None


class VectorStore(Protocol):
    def store(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        ...
    def query(self, embedding: List[float], top_k: int, role_filter: str = "") -> List[Chunk]:
        ...
    def delete(self, document_id: str) -> None:
        ...


class NoOpVectorStore:
    def store(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        pass
    def query(self, embedding: List[float], top_k: int, role_filter: str = "") -> List[Chunk]:
        return []
    def delete(self, document_id: str) -> None:
        pass


class ChromaDBVectorStore:
    """对接 ChromaDB 向量数据库"""

    def __init__(self, host: str = "localhost", port: int = 8000, collection_name: str = "hr_policy_qa"):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self._client = None
        self._collection = None

    def _init_client(self):
        if self._client is None:
            import chromadb
            try:
                self._client = chromadb.HttpClient(host=self.host, port=self.port)
                self._collection = self._client.get_or_create_collection(
                    self.collection_name,
                    metadata={"hnsw:space": "cosine"},
                )
                logger.info(f"ChromaDB connected: {self.host}:{self.port}/{self.collection_name}")
            except Exception:
                logger.warning("ChromaDB HTTP failed, using in-memory mode")
                self._client = chromadb.Client(
                    chromadb.config.Settings(
                        anonymized_telemetry=False,
                        is_persistent=False,
                    )
                )
                self._collection = self._client.get_or_create_collection(
                    self.collection_name,
                    metadata={"hnsw:space": "cosine"},
                )

    def store(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        self._init_client()
        if not chunks:
            return
        ids = [c.chunk_id for c in chunks]
        documents = [c.content for c in chunks]
        metadatas = [{"document_id": c.document_id, "chunk_index": c.chunk_index} for c in chunks]
        try:
            self._collection.upsert(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)
            logger.info(f"Stored {len(chunks)} chunks to ChromaDB")
        except Exception as e:
            logger.error(f"ChromaDB upsert failed: {e}")

    def query(self, embedding: List[float], top_k: int, role_filter: str = "") -> List[Chunk]:
        self._init_client()
        if not embedding:
            return []
        try:
            results = self._collection.query(query_embeddings=[embedding], n_results=top_k)
            chunks = []
            if results and results.get("ids") and results["ids"][0]:
                for i, chunk_id in enumerate(results["ids"][0]):
                    md = results.get("metadatas", [[{}]])[0][i] if results.get("metadatas") else {}
                    chunks.append(Chunk(
                        chunk_id=chunk_id,
                        document_id=md.get("document_id", ""),
                        content=results.get("documents", [[""]])[0][i] if results.get("documents") else "",
                        chunk_index=md.get("chunk_index", 0),
                    ))
            return chunks
        except Exception as e:
            logger.error(f"ChromaDB query failed: {e}")
            return []

    def delete(self, document_id: str) -> None:
        self._init_client()
        try:
            self._collection.delete(where={"document_id": document_id})
        except Exception as e:
            logger.error(f"ChromaDB delete failed: {e}")


class LocalVectorStore:
    """本地持久化向量库（基于 SQLite + numpy 余弦相似度）

    无需启动 ChromaDB 服务，向量数据持久化到 SQLite 文件。
    适合课程设计/中小规模数据场景。
    """

    def __init__(self, db_path: str = "./data/vectors.db"):
        self.db_path = db_path
        self._lock = threading.Lock()
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _init_db(self):
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS vectors (
                chunk_id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                content TEXT NOT NULL,
                chunk_index INTEGER DEFAULT 0,
                embedding TEXT NOT NULL
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_document_id ON vectors(document_id)")
        conn.commit()
        logger.info(f"LocalVectorStore initialized: {self.db_path}")

    def store(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        if not chunks:
            return
        with self._lock:
            conn = self._get_conn()
            for chunk, emb in zip(chunks, embeddings):
                conn.execute(
                    "INSERT OR REPLACE INTO vectors (chunk_id, document_id, content, chunk_index, embedding) "
                    "VALUES (?, ?, ?, ?, ?)",
                    (chunk.chunk_id, chunk.document_id, chunk.content, chunk.chunk_index, json.dumps(emb)),
                )
            conn.commit()
            logger.info(f"LocalVectorStore: stored {len(chunks)} chunks")

    def query(self, embedding: List[float], top_k: int, role_filter: str = "") -> List[Chunk]:
        if not embedding:
            return []
        try:
            import numpy as np
        except ImportError:
            logger.error("numpy not installed, cannot query LocalVectorStore")
            return []

        with self._lock:
            conn = self._get_conn()
            rows = conn.execute("SELECT chunk_id, document_id, content, chunk_index, embedding FROM vectors").fetchall()

        if not rows:
            return []

        query_vec = np.array(embedding, dtype=np.float32)
        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            return []
        query_vec = query_vec / query_norm

        scored = []
        for row in rows:
            try:
                doc_vec = np.array(json.loads(row["embedding"]), dtype=np.float32)
                doc_norm = np.linalg.norm(doc_vec)
                if doc_norm == 0:
                    continue
                doc_vec = doc_vec / doc_norm
                similarity = float(np.dot(query_vec, doc_vec))
                scored.append((similarity, row))
            except Exception:
                continue

        scored.sort(key=lambda x: x[0], reverse=True)

        chunks = []
        for sim, row in scored[:top_k]:
            chunks.append(Chunk(
                chunk_id=row["chunk_id"],
                document_id=row["document_id"],
                content=row["content"],
                chunk_index=row["chunk_index"],
            ))
        return chunks

    def delete(self, document_id: str) -> None:
        with self._lock:
            conn = self._get_conn()
            conn.execute("DELETE FROM vectors WHERE document_id = ?", (document_id,))
            conn.commit()
            logger.info(f"LocalVectorStore: deleted chunks for document {document_id}")


vector_store: VectorStore = NoOpVectorStore()

# 文档分块器默认使用语义分块
from app.providers.document_chunker import SemanticChunker
document_chunker = SemanticChunker()


def init_vector_store(
    host: str = "localhost", port: int = 8000, collection_name: str = "hr_policy_qa",
    use_local: bool = False, local_db_path: str = "./data/vectors.db",
) -> VectorStore:
    """初始化向量存储

    - use_local=True: 使用本地 SQLite 持久化，无需 ChromaDB 服务
    - use_local=False: 使用 ChromaDB
    """
    global vector_store
    if use_local:
        try:
            vector_store = LocalVectorStore(db_path=local_db_path)
            logger.info(f"Vector store initialized (local): {local_db_path}")
        except Exception as e:
            logger.error(f"LocalVectorStore init failed: {e}, using NoOp")
            vector_store = NoOpVectorStore()
    else:
        try:
            vector_store = ChromaDBVectorStore(host=host, port=port, collection_name=collection_name)
            logger.info(f"Vector store initialized: ChromaDB at {host}:{port}")
        except Exception as e:
            logger.warning(f"ChromaDB unavailable ({e}), using NoOp")
    return vector_store
