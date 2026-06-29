import request from './request'

// ── 文档管理 ──
export function getDocuments(params?: any) {
  return request.get('/documents', { params })
}
export function getDocument(id: string) {
  return request.get(`/documents/${id}`)
}
export function createDocument(data: FormData) {
  return request.post('/documents', data, { headers: { 'Content-Type': 'multipart/form-data' } })
}
export function updateDocument(id: string, data: any) {
  return request.put(`/documents/${id}`, data)
}
export function archiveDocument(id: string) {
  return request.delete(`/documents/${id}`)
}
export function getDocumentVersions(id: string) {
  return request.get(`/documents/${id}/versions`)
}
export function updateDocumentAccess(id: string, accessLevel: string) {
  return request.patch(`/documents/${id}/access`, { access_level: accessLevel })
}

// ── 分类管理 ──
export function getCategories(params?: any) {
  return request.get('/categories', { params })
}
export function createCategory(data: any) {
  return request.post('/categories', data)
}
export function updateCategoryAccess(id: string, accessLevel: string, cascade: boolean = false) {
  return request.patch(`/categories/${id}/access`, { access_level: accessLevel, cascade })
}

// ── FAQ管理 ──
export function getFAQs(params?: any) {
  return request.get('/faqs', { params })
}
export function createFAQ(data: any) {
  return request.post('/faqs', data)
}
export function updateFAQ(id: string, data: any) {
  return request.put(`/faqs/${id}`, data)
}
export function deleteFAQ(id: string) {
  return request.delete(`/faqs/${id}`)
}

// ── 纠错审核 ──
export function getCorrections(params?: any) {
  return request.get('/corrections', { params })
}
export function createCorrection(data: any) {
  return request.post('/corrections', data)
}
export function reviewCorrection(id: string, data: { action: string; comment?: string }) {
  return request.post(`/corrections/${id}/review`, data)
}

// ── 公告管理 ──
export function getAnnouncements(params?: any) {
  return request.get('/announcements', { params })
}
export function createAnnouncement(data: any) {
  return request.post('/announcements', data)
}
export function getAnnouncementReads(id: string) {
  return request.get(`/announcements/${id}/reads`)
}

// ── 用户管理 ──
export function getUsers(params?: any) {
  return request.get('/users', { params })
}
export function importEmployees(file: File) {
  const fd = new FormData()
  fd.append('file', file)
  return request.post('/import/employees', fd, { headers: { 'Content-Type': 'multipart/form-data' } })
}

// ── 审计日志 ──
export function getAuditLogs(params?: any) {
  return request.get('/audit/logs', { params })
}

// ── 数据分析仪表盘 ──
export function getDashboard(timeRange: string = '7d') {
  return request.get('/analytics/dashboard', { params: { time_range: timeRange } })
}
