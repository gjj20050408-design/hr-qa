import request from './request'
import type { ApiResponse, ChatMessage, ChatSession, QARecord, PaginatedData } from '@/types'

// 发送问题
export function sendQuestion(data: { question: string; session_id?: string }): Promise<ApiResponse<QARecord>> {
  return request.post('/qa/ask', data).then(res => res.data)
}

// 获取会话列表
export function getSessions(): Promise<ApiResponse<ChatSession[]>> {
  return request.get('/qa/sessions').then(res => res.data)
}

// 获取会话消息
export function getSessionMessages(sessionId: string): Promise<ApiResponse<ChatMessage[]>> {
  return request.get(`/qa/sessions/${sessionId}`).then(res => res.data)
}

// 删除会话
export function deleteSession(sessionId: string): Promise<ApiResponse<null>> {
  return request.delete(`/qa/sessions/${sessionId}`).then(res => res.data)
}

// 获取问答历史
export function getQARecords(params: { page?: number; page_size?: number; type?: string; keyword?: string }): Promise<ApiResponse<PaginatedData<QARecord>>> {
  return request.get('/qa/records', { params }).then(res => res.data)
}

// 获取收藏列表
export function getFavorites(): Promise<ApiResponse<QARecord[]>> {
  return request.get('/qa/favorites').then(res => res.data)
}

// 切换收藏
export function toggleFavorite(recordId: string): Promise<ApiResponse<{ is_favorite: boolean }>> {
  return request.post(`/qa/records/${recordId}/actions/favorite`).then(res => res.data)
}

// 提交反馈
export function submitFeedback(recordId: string, data: { feedback: string; reason?: string }): Promise<ApiResponse<null>> {
  return request.post(`/qa/records/${recordId}/actions/feedback`, data).then(res => res.data)
}
