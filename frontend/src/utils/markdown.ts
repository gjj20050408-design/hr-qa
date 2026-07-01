import { marked } from 'marked'
import DOMPurify from 'dompurify'

marked.setOptions({ breaks: true, gfm: true })

/**
 * 将 markdown 渲染为消毒后的安全 HTML。
 * 用于制度解读摘要、对比表格、文档正文等场景。
 */
export function renderMarkdown(raw: string): string {
  if (!raw) return ''
  return DOMPurify.sanitize(marked.parse(raw, { async: false }) as string)
}
