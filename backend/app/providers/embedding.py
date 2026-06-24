"""EmbeddingProvider 抽象接口（一期空实现，二期对接云端API）"""
from typing import Protocol, List


class EmbeddingProvider(Protocol):
    """向量嵌入提供者接口"""

    def embed(self, text: str) -> List[float]:
        """单文本向量化"""
        ...

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量文本向量化"""
        ...


class NoOpEmbeddingProvider:
    """一期空实现"""

    def embed(self, text: str) -> List[float]:
        return []

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [[] for _ in texts]


class OpenAIEmbeddingProvider:
    """二期实现：对接 OpenAI Embedding API"""

    def __init__(self, api_key: str, base_url: str, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    def embed(self, text: str) -> List[float]:
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
            response = client.embeddings.create(model=self.model, input=text)
            return response.data[0].embedding
        except Exception:
            return []

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        results = []
        for text in texts:
            results.append(self.embed(text))
        return results


embedding_provider: EmbeddingProvider = NoOpEmbeddingProvider()
