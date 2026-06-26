import request from './request'
import type { ApiResponse, FAQ, PaginatedData } from '@/types'

// 获取FAQ列表
export function getFAQs(params: { category_id?: string; keyword?: string; page?: number; page_size?: number }): Promise<ApiResponse<PaginatedData<FAQ>>> {
  return request.get('/faqs', { params }).then(res => res.data)
}
