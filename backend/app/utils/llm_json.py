"""LLM 结构化输出解析工具

从 LLM 返回文本中稳健地提取 JSON 对象，兼容三种常见形态：
1. 直接是合法 JSON
2. 被 ```json ... ``` 代码块包裹
3. 文本中夹带首个 {...} 块
"""
import json
import re
from typing import Optional


def parse_llm_json(content: str) -> Optional[dict]:
    """从 LLM 响应中解析 JSON（处理可能的 markdown 包裹）。

    解析失败时返回 None，调用方需自行决定降级策略。
    """
    if not content:
        return None
    # 尝试直接解析
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    # 尝试提取 ```json ... ``` 代码块
    m = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', content, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1).strip())
        except json.JSONDecodeError:
            pass
    # 尝试提取第一个 { ... } 块
    m = re.search(r'\{.*\}', content, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    return None
