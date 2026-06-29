import request from './request'
import type { ApiResponse, Document, SearchRequest, PaginatedData } from '@/types'

// 全文搜索
export function searchDocuments(params: SearchRequest): Promise<ApiResponse<PaginatedData<Document>>> {
  return request.get('/search', { params })
}

// 获取文档详情
export function getDocumentDetail(id: string): Promise<ApiResponse<Document>> {
  return request.get(`/documents/${id}`)
}
