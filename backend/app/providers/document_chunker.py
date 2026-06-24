"""DocumentChunker 文档分块器抽象接口（一期透传，二期语义分块）"""
from typing import Protocol, List
from dataclasses import dataclass


@dataclass
class ChunkUnit:
    chunk_id: str
    content: str
    token_count: int = 0
    start_index: int = 0
    end_index: int = 0


class DocumentChunker(Protocol):
    """文档分块器接口"""

    def split(self, content: str, chunk_size: int = 500) -> List[ChunkUnit]:
        """将文档按指定大小分块"""
        ...


class PassthroughChunker:
    """一期透传实现：不分块，整个文档作为一个块"""

    def split(self, content: str, chunk_size: int = 500) -> List[ChunkUnit]:
        from app.models.base import uuid4_str
        return [ChunkUnit(
            chunk_id=uuid4_str(),
            content=content,
            token_count=len(content),
            start_index=0,
            end_index=len(content),
        )]


class SemanticChunker:
    """二期语义分块实现：按 ~500 tokens 分割"""

    def split(self, content: str, chunk_size: int = 500) -> List[ChunkUnit]:
        from app.models.base import uuid4_str
        import re

        # 按段落分割
        paragraphs = re.split(r'\n\s*\n', content)
        chunks = []
        current_chunk = ""
        current_start = 0

        for para in paragraphs:
            if current_chunk and len(current_chunk) + len(para) > chunk_size * 4:  # ~500 tokens ≈ 2000 chars
                chunks.append(ChunkUnit(
                    chunk_id=uuid4_str(),
                    content=current_chunk.strip(),
                    token_count=len(current_chunk) // 4,
                    start_index=current_start,
                    end_index=current_start + len(current_chunk),
                ))
                current_start += len(current_chunk)
                current_chunk = para
            else:
                if current_chunk:
                    current_chunk += "\n\n" + para
                else:
                    current_chunk = para

        if current_chunk.strip():
            chunks.append(ChunkUnit(
                chunk_id=uuid4_str(),
                content=current_chunk.strip(),
                token_count=len(current_chunk) // 4,
                start_index=current_start,
                end_index=current_start + len(current_chunk),
            ))

        return chunks


document_chunker: DocumentChunker = PassthroughChunker()
