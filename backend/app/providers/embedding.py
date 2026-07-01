"""EmbeddingProvider 抽象接口（支持云端API与本地模型）"""
import logging
import os
from typing import Protocol, List

logger = logging.getLogger(__name__)


class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> List[float]:
        ...
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        ...


class NoOpEmbeddingProvider:
    def embed(self, text: str) -> List[float]:
        return []
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [[] for _ in texts]


class OpenAIEmbeddingProvider:
    """对接 OpenAI 兼容 Embedding API"""

    def __init__(self, api_key: str, base_url: str, model: str = "text-embedding-3-small"):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    def embed(self, text: str) -> List[float]:
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=10)
            response = client.embeddings.create(model=self.model, input=text)
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding failed: {e}")
            return []

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        results = []
        for text in texts:
            results.append(self.embed(text))
        return results


class LocalEmbeddingProvider:
    """本地 Embedding 模型（基于 sentence-transformers）

    推荐模型：
    - BAAI/bge-small-zh-v1.5  (中文, 512维, 轻量快速, ~95MB)
    - BAAI/bge-base-zh-v1.5   (中文, 768维, 效果更好, ~400MB)
    首次使用会自动从 HuggingFace 下载模型到本地缓存。
    """

    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5"):
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            # 国内环境自动使用 HuggingFace 镜像站，避免下载超时
            if not os.environ.get("HF_ENDPOINT"):
                os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
                logger.info("Using HF mirror: https://hf-mirror.com")
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading local embedding model: {self.model_name} (首次加载需下载)...")
            self._model = SentenceTransformer(self.model_name)
            logger.info(f"Local embedding model loaded: {self.model_name}")
        return self._model

    def embed(self, text: str) -> List[float]:
        try:
            model = self._get_model()
            embedding = model.encode(text, normalize_embeddings=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Local embedding failed: {e}")
            return []

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        try:
            model = self._get_model()
            embeddings = model.encode(texts, normalize_embeddings=True, batch_size=32)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Local embedding batch failed: {e}")
            return [[] for _ in texts]


embedding_provider: EmbeddingProvider = NoOpEmbeddingProvider()


def init_embedding_provider(
    api_key: str = "", base_url: str = "", model: str = "text-embedding-3-small",
    use_local: bool = False, local_model: str = "BAAI/bge-small-zh-v1.5",
) -> EmbeddingProvider:
    """初始化 Embedding 提供者

    - use_local=True: 使用本地 sentence-transformers 模型，无需 API Key
    - use_local=False: 使用 OpenAI 兼容云端 API（需 api_key + base_url）
    """
    global embedding_provider
    if use_local:
        try:
            embedding_provider = LocalEmbeddingProvider(model_name=local_model)
            logger.info(f"Embedding provider initialized (local): model={local_model}")
        except Exception as e:
            logger.error(f"Local embedding init failed: {e}, falling back to NoOp")
            embedding_provider = NoOpEmbeddingProvider()
    elif api_key and base_url:
        embedding_provider = OpenAIEmbeddingProvider(api_key=api_key, base_url=base_url, model=model)
        logger.info(f"Embedding provider initialized (API): model={model}")
    return embedding_provider
