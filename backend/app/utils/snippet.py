"""文本摘要生成工具 — 从搜索结果中提取高亮片段"""
import jieba


def generate_snippet(content: str, query: str, context_radius: int = 50) -> str:
    """从文档内容中生成包含查询关键词的摘要片段。

    使用 jieba 分词进行中文关键词匹配，优先返回包含完整查询词的位置，
    退而寻找任意分词匹配的位置。

    Args:
        content: 完整文档内容
        query: 搜索关键词
        context_radius: 匹配位置前后的上下文字符数

    Returns:
        带省略号的摘要字符串
    """
    if not content:
        return ""

    # 策略1：直接字符串匹配
    idx = content.find(query)

    # 策略2：使用 jieba 分词匹配
    if idx == -1:
        query_words = list(jieba.cut(query))
        for word in query_words:
            if len(word.strip()) >= 2:  # 跳过单字
                idx = content.find(word)
                if idx != -1:
                    break

    # 策略3：退回到任意字符匹配
    if idx == -1:
        for ch in query:
            idx = content.find(ch)
            if idx != -1:
                break

    # 未找到任何匹配，返回开头截断
    if idx == -1:
        if len(content) > context_radius * 3:
            return content[:context_radius * 3] + "..."
        return content

    start = max(0, idx - context_radius)
    end = min(len(content), idx + context_radius * 2)
    snippet = content[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(content):
        snippet += "..."
    return snippet


def similarity_chinese(text1: str, text2: str) -> float:
    """基于 jieba 分词的余弦相似度计算，适用于中文短文本。

    使用词频向量计算两个文本的余弦相似度，对 FAQ 匹配等场景效果优于 bigram。

    Args:
        text1: 第一个文本
        text2: 第二个文本

    Returns:
        0.0 ~ 1.0 之间的相似度分数
    """
    if not text1 or not text2:
        return 0.0

    # jieba 分词
    words1 = [w for w in jieba.cut(text1) if len(w.strip()) >= 1]
    words2 = [w for w in jieba.cut(text2) if len(w.strip()) >= 1]

    if not words1 or not words2:
        return 0.0

    # 构建联合词表
    all_words = set(words1) | set(words2)

    # 词频向量
    vec1 = [words1.count(w) for w in all_words]
    vec2 = [words2.count(w) for w in all_words]

    # 余弦相似度
    dot = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = sum(a * a for a in vec1) ** 0.5
    norm2 = sum(b * b for b in vec2) ** 0.5

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot / (norm1 * norm2)
