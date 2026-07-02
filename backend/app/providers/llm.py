"""LLMProvider 抽象接口（含熔断降级）"""
import time
import logging
from typing import Protocol, Optional

logger = logging.getLogger(__name__)


class LLMResponse:
    """LLM 响应封装"""
    def __init__(self, content: str, tokens_used: int = 0, model: str = ""):
        self.content = content
        self.tokens_used = tokens_used
        self.model = model


class LLMProvider(Protocol):
    """大语言模型提供者接口"""
    def generate(self, prompt: str, system_prompt: str = "",
                 max_tokens: int = 512, temperature: float = 0.7,
                 history: Optional[list] = None) -> LLMResponse:
        ...
    def health_check(self) -> bool:
        ...


class NoOpLLMProvider:
    """一期空实现"""
    def generate(self, prompt: str, system_prompt: str = "",
                 max_tokens: int = 512, temperature: float = 0.7,
                 history: Optional[list] = None) -> LLMResponse:
        return LLMResponse(content="", tokens_used=0, model="noop")
    def health_check(self) -> bool:
        return False


class CircuitBreakerLLMProvider:
    """带熔断器的LLM提供者包装器（S4.11）

    连续失败N次 → 熔断打开（拒绝请求T秒）→ 半开探测 → 恢复
    """

    def __init__(self, inner: "OpenAILLMProvider", failure_threshold: int = 5, timeout_seconds: int = 30):
        self._inner = inner
        self._failure_threshold = failure_threshold
        self._timeout_seconds = timeout_seconds
        self._failure_count = 0
        self._last_failure_time: float = 0
        self._circuit_open: bool = False

    @property
    def is_circuit_open(self) -> bool:
        if not self._circuit_open:
            return False
        if time.time() - self._last_failure_time > self._timeout_seconds:
            # 进入半开状态
            self._circuit_open = False
            self._failure_count = 0
            logger.info("Circuit breaker: half-open, probing...")
            return False
        return True

    def generate(self, prompt: str, system_prompt: str = "",
                 max_tokens: int = 512, temperature: float = 0.7,
                 history: Optional[list] = None) -> LLMResponse:
        if self.is_circuit_open:
            logger.warning("Circuit breaker OPEN: request rejected")
            return LLMResponse(content="[LLM 服务暂时不可用，已熔断]", model=self._inner.model)

        try:
            response = self._inner.generate(prompt, system_prompt, max_tokens, temperature, history)
            # 成功 → 重置
            self._failure_count = 0
            self._circuit_open = False
            return response
        except Exception as e:
            self._failure_count += 1
            self._last_failure_time = time.time()
            logger.error(f"LLM call failed ({self._failure_count}/{self._failure_threshold}): {e}")
            if self._failure_count >= self._failure_threshold:
                self._circuit_open = True
                logger.critical(f"Circuit breaker OPEN: {self._failure_count} consecutive failures")
            return LLMResponse(content=f"[LLM Error: {str(e)}]", model=self._inner.model)

    def health_check(self) -> bool:
        return not self.is_circuit_open and self._inner.health_check()


class OpenAILLMProvider:
    """二期实现：对接 OpenAI 兼容 API（支持Qwen/GLM等）"""

    def __init__(self, api_key: str, base_url: str, model: str, timeout: int = 120):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self._health_cache: Optional[bool] = None
        self._health_cache_time: float = 0
        self._health_cache_ttl: float = 30

    def generate(self, prompt: str, system_prompt: str = "",
                 max_tokens: int = 512, temperature: float = 0.7,
                 history: Optional[list] = None) -> LLMResponse:
        import openai
        client = openai.OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
            max_retries=0,
        )
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if history:
            messages.extend(history)          # 多轮追问：插入历史对话
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=False,
        )
        return LLMResponse(
            content=response.choices[0].message.content or "",
            tokens_used=response.usage.total_tokens if response.usage else 0,
            model=self.model,
        )

    def health_check(self) -> bool:
        # 使用缓存，避免每次检查都创建新客户端并请求 API
        now = time.time()
        if self._health_cache is not None and (now - self._health_cache_time) < self._health_cache_ttl:
            return self._health_cache
        try:
            import openai
            # 健康探测必须快速失败：max_retries=0 避免连接超时时重试 2 次
            # 造成 ~10s 阻塞；失败后由下方 30s 缓存兜底，不会频繁重连。
            client = openai.OpenAI(
                api_key=self.api_key, base_url=self.base_url,
                timeout=3, max_retries=0,
            )
            client.models.list()
            self._health_cache = True
        except Exception:
            self._health_cache = False
        self._health_cache_time = time.time()
        return self._health_cache


# 默认使用空实现，启动时根据环境变量配置
llm_provider: LLMProvider = NoOpLLMProvider()


def init_llm_provider(
    api_key: str = "", base_url: str = "", model: str = "",
    failure_threshold: int = 5, timeout_seconds: int = 30,
) -> LLMProvider:
    """初始化LLM提供者（含熔断）"""
    global llm_provider
    if api_key and base_url and model:
        inner = OpenAILLMProvider(api_key=api_key, base_url=base_url, model=model)
        llm_provider = CircuitBreakerLLMProvider(
            inner,
            failure_threshold=failure_threshold,
            timeout_seconds=timeout_seconds,
        )
        logger.info(f"LLM provider initialized: model={model}, base_url={base_url}")
    else:
        logger.warning("LLM provider not configured, using NoOp (RAG disabled)")
    return llm_provider
