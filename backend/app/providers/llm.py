"""LLMProvider 抽象接口（一期空实现，二期对接云端API）"""
from typing import Protocol, Optional


class LLMResponse:
    """LLM 响应封装"""
    def __init__(self, content: str, tokens_used: int = 0, model: str = ""):
        self.content = content
        self.tokens_used = tokens_used
        self.model = model


class LLMProvider(Protocol):
    """大语言模型提供者接口"""

    def generate(self, prompt: str, system_prompt: str = "",
                 max_tokens: int = 512, temperature: float = 0.7) -> LLMResponse:
        """生成回复"""
        ...

    def health_check(self) -> bool:
        """健康检查"""
        ...


class NoOpLLMProvider:
    """一期空实现：不执行任何 LLM 调用"""

    def generate(self, prompt: str, system_prompt: str = "",
                 max_tokens: int = 512, temperature: float = 0.7) -> LLMResponse:
        return LLMResponse(content="", tokens_used=0, model="noop")

    def health_check(self) -> bool:
        return False


class OpenAILLMProvider:
    """二期实现：对接 OpenAI 兼容 API"""

    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    def generate(self, prompt: str, system_prompt: str = "",
                 max_tokens: int = 512, temperature: float = 0.7) -> LLMResponse:
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return LLMResponse(
                content=response.choices[0].message.content,
                tokens_used=response.usage.total_tokens if response.usage else 0,
                model=self.model,
            )
        except Exception as e:
            return LLMResponse(content=f"[LLM Error: {str(e)}]", model=self.model)

    def health_check(self) -> bool:
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
            client.models.list()
            return True
        except Exception:
            return False


# 默认使用空实现
llm_provider: LLMProvider = NoOpLLMProvider()
