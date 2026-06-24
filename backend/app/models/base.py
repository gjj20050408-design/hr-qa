"""基础模型 — UUID 工具函数"""
from uuid import uuid4


def uuid4_str() -> str:
    """生成不带横线的 UUID 字符串"""
    return uuid4().hex
