import request from './request'
import type { ApiResponse, ChatMessage, ChatSession, QARecord, PaginatedData } from '@/types'

// 发送问题
export function sendQuestion(data: { question: string; session_id?: string }): Promise<ApiResponse<any>> {
  return request.post('/qa/ask', data)
}

// 创建会话
export function createSession(): Promise<ApiResponse<{ session_id: string }>> {
  return request.post('/qa/sessions')
}

// 获取会话列表
export function getSessions(params?: any): Promise<ApiResponse<any>> {
  return request.get('/qa/sessions', { params })
}

// 获取会话消息
export function getSessionMessages(sessionId: string): Promise<ApiResponse<any>> {
  return request.get('/qa/records', { params: { session_id: sessionId, page_size: 100 } })
}

// 删除会话
export function deleteSession(sessionId: string): Promise<ApiResponse<null>> {
  return request.delete(`/qa/sessions/${sessionId}`)
}

// 重命名会话
export function renameSession(sessionId: string, title: string): Promise<ApiResponse<any>> {
  return request.patch(`/qa/sessions/${sessionId}/title`, { title })
}

// 切换会话置顶
export function togglePinSession(sessionId: string): Promise<ApiResponse<any>> {
  return request.patch(`/qa/sessions/${sessionId}/pin`)
}

// 获取问答历史
export function getQARecords(params: { page?: number; page_size?: number; answer_type?: string; keyword?: string }) {
  return request.get('/qa/records', { params })
}

// 切换收藏
export function toggleFavorite(recordId: string, isFavorite: boolean) {
  return request.patch(`/qa/records/${recordId}/favorite`, { is_favorite: isFavorite })
}

// 提交反馈
export function submitFeedback(recordId: string, feedback: string, reason?: string): Promise<ApiResponse<null>> {
  return request.post('/feedback', null, { params: { record_id: recordId, feedback, reason } })
}
