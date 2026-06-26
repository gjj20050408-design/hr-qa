import request from './request'
import type { ApiResponse, Announcement, PaginatedData } from '@/types'

// 获取通知列表
export function getNotifications(params?: { page?: number; page_size?: number }): Promise<ApiResponse<PaginatedData<Announcement>>> {
  return request.get('/notifications', { params }).then(res => res.data)
}

// 标记已读
export function markAsRead(announcementId: string): Promise<ApiResponse<null>> {
  return request.post(`/notifications/${announcementId}/actions/read`).then(res => res.data)
}

// 全部标记已读
export function markAllRead(): Promise<ApiResponse<null>> {
  return request.post('/notifications/actions/read-all').then(res => res.data)
}
