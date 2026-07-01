import request from './request'

// ── 制度解读 ──

// 获取制度解读（按需生成 + 缓存）。调用方用 res.data.data 取负载。
export function getInterpretation(documentId: string) {
  return request.get(`/interpretations/${documentId}`)
}

// 强制重新生成解读（HR/管理员）
export function refreshInterpretation(documentId: string) {
  return request.post(`/interpretations/${documentId}/refresh`)
}

// ── 个性化权益报告 ──

// 获取本人权益报告（year 可选，默认当前年）
export function getBenefitReport(year?: number) {
  return request.get('/benefits/report', { params: year ? { year } : {} })
}

// 强制重新生成本人权益报告
export function refreshBenefitReport(year?: number) {
  return request.post('/benefits/report/refresh', null, { params: year ? { year } : {} })
}
