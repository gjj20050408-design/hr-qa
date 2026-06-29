import request from './request'
import type { ApiResponse, Announcement, PaginatedData } from '@/types'

// 获取公告列表（对齐后端 /announcements）
export function getNotifications(params?: { page?: number; page_size?: number }): Promise<ApiResponse<PaginatedData<Announcement>>> {
  return request.get('/announcements', { params }).then(res => res.data)
}

// 标记单条已读（对齐后端 /announcements/mark-read）
export function markAsRead(announcementId: string): Promise<ApiResponse<null>> {
  return request.post('/announcements/mark-read', { announcement_id: announcementId }).then(res => res.data)
}

// 全部标记已读
export function markAllRead(): Promise<ApiResponse<null>> {
  return request.post('/announcements/mark-read', {}).then(res => res.data)
}
