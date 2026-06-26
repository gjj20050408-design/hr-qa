import request from './request'
import type { ApiResponse, QAStatistics } from '@/types'

// 获取统计数据
export function getStatistics(): Promise<ApiResponse<QAStatistics>> {
  return request.get('/analytics/dashboard').then(res => res.data)
}
