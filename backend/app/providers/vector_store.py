"""VectorStore 抽象接口（一期空实现，二期对接ChromaDB）"""
from typing import Protocol, List
from dataclasses import dataclass


@dataclass
class Chunk:
    chunk_id: str
    document_id: str
    content: str
    chunk_index: int = 0
    token_count: int = 0
    embedding: List[float] = None


class VectorStore(Protocol):
    """向量存储接口"""

    def store(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        """存储向量"""
        ...

    def query(self, embedding: List[float], top_k: int, role_filter: str = "") -> List[Chunk]:
        """向量检索"""
        ...

    def delete(self, document_id: str) -> None:
        """删除文档向量"""
        ...


class NoOpVectorStore:
    """一期空实现"""

    def store(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        pass

    def query(self, embedding: List[float], top_k: int, role_filter: str = "") -> List[Chunk]:
        return []

    def delete(self, document_id: str) -> None:
        pass


class ChromaDBVectorStore:
    """二期实现：对接 ChromaDB"""

    def __init__(self, host: str = "localhost", port: int = 8001, collection_name: str = "hr_policy_qa"):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self._client = None
        self._collection = None

    def _init_client(self):
        if self._client is None:
            import chromadb
            self._client = chromadb.HttpClient(host=self.host, port=self.port)
            self._collection = self._client.get_or_create_collection(self.collection_name)

    def store(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        self._init_client()
        ids = [c.chunk_id for c in chunks]
        documents = [c.content for c in chunks]
        metadatas = [{"document_id": c.document_id, "chunk_index": c.chunk_index} for c in chunks]
        self._collection.add(ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas)

    def query(self, embedding: List[float], top_k: int, role_filter: str = "") -> List[Chunk]:
        self._init_client()
        results = self._collection.query(query_embeddings=[embedding], n_results=top_k)
        chunks = []
        if results and results["ids"]:
            for i, chunk_id in enumerate(results["ids"][0]):
                chunks.append(Chunk(
                    chunk_id=chunk_id,
                    document_id=results["metadatas"][0][i].get("document_id", "") if results.get("metadatas") else "",
                    content=results["documents"][0][i] if results.get("documents") else "",
                    chunk_index=results["metadatas"][0][i].get("chunk_index", 0) if results.get("metadatas") else 0,
                ))
        return chunks

    def delete(self, document_id: str) -> None:
        self._init_client()
        self._collection.delete(where={"document_id": document_id})


vector_store: VectorStore = NoOpVectorStore()
