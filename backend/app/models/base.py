"""基础模型 — UUID 工具函数 & 大小写不敏感枚举"""
from typing import Type
from uuid import uuid4

from sqlalchemy import String, TypeDecorator


def uuid4_str() -> str:
    """生成不带横线的 UUID 字符串"""
    return uuid4().hex


class CaseInsensitiveEnum(TypeDecorator):
    """大小写不敏感枚举映射 — 兼容数据库中大写值与 Python 枚举小写值
    
    使用 String 而非 Enum 作为 impl，避免 MySQL ENUM 方言在 process_result_value 
    之前执行 _object_value_for_elem 导致大写值 LookupError。
    """
    impl = String(30)
    cache_ok = True

    def __init__(self, enum_class: Type, **kwargs):
        super().__init__(length=30, **kwargs)
        self._enum = enum_class

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, self._enum):
            return value.value
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        for member in self._enum:
            if member.value == value.lower():
                return member
        return self._enum(value) if hasattr(self._enum, '__call__') else value
