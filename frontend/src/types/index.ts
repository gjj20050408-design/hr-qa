// ============================================================
// 通用类型定义
// ============================================================

// 用户角色
export type UserRole = 'employee' | 'hr_specialist' | 'admin'

// 用户信息
export interface UserInfo {
  user_id: string
  employee_id: string
  name: string
  email: string
  phone: string
  role: UserRole
  department_id: string
  department_name?: string
  department?: string
  job_level: string
  hire_date: string
  work_location: string
  status: 'active' | 'disabled'
}

// 登录请求
export interface LoginRequest {
  account: string
  password: string
}

// 注册请求
export interface RegisterRequest {
  employee_id: string
  name: string
  department_id: string
  email?: string
  phone?: string
  password: string
}

// 统一API响应
export interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  request_id: string
  timestamp: string
}

// 分页信息
export interface Pagination {
  page: number
  page_size: number
  total: number
  total_pages: number
}

// 分页响应
export interface PaginatedData<T> {
  items: T[]
  pagination: Pagination
}

// 文档分类
export interface Category {
  category_id: string
  name: string
  parent_id: string | null
  type: 'document' | 'faq'
  access_level: 'all_roles' | 'hr_admin_only' | 'admin_only'
  sort_order: number
  children?: Category[]
}

// 制度文档
export interface Document {
  document_id: string
  title: string
  content: string
  summary?: string
  category_id: string
  category_name?: string
  format: 'pdf' | 'word' | 'markdown' | 'html'
  version: string
  version_note: string
  status: 'draft' | 'published' | 'archived'
  access_level: 'inherit' | 'all_roles' | 'hr_admin_only' | 'admin_only'
  uploaded_by: string
  uploader_name?: string
  word_count: number
  published_at: string
  created_at: string
  updated_at: string
  has_access?: boolean
}

// 搜索请求
export interface SearchRequest {
  keyword: string
  category_id?: string
  page?: number
  page_size?: number
}

// 搜索高亮
export interface SearchHighlight {
  title: string
  content: string
}

// FAQ
export interface FAQ {
  faq_id: string
  question: string
  answer: string
  category_id: string
  category_name?: string
  related_doc_id: string
  keywords: string
  view_count: number
  status: 'active' | 'archived'
  created_by: string
  created_at: string
  updated_at: string
}

// 问答记录
export interface QARecord {
  record_id: string
  user_id: string
  session_id: string
  question: string
  answer: string
  answer_type: 'faq' | 'rule' | 'search' | 'rag' | 'no_result'
  confidence: number
  reference_docs: { doc_id: string; title: string; section: string }[]
  response_time_ms: number
  feedback?: 'helpful' | 'not_helpful'
  feedback_reason?: string
  is_favorite: boolean
  created_at: string
}

// 聊天消息
export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  answer_type?: string
  reference_docs?: { doc_id: string; title: string; section: string }[]
  response_time_ms?: number
  is_favorite?: boolean
  is_permission_denied?: boolean
  created_at: string
}

// 会话
export interface ChatSession {
  session_id: string
  title: string
  created_at: string
  is_pinned?: boolean
  messages: ChatMessage[]
}

// 通知公告
export interface Announcement {
  announcement_id: string
  title: string
  content: string
  priority: 'normal' | 'important' | 'urgent'
  target_type: 'all' | 'department' | 'role'
  target_ids: string[]
  attachment: string
  published_by: string
  publisher_name?: string
  published_at: string
  is_read?: boolean
}

// 制度解读
export interface PolicyInterpretation {
  document_id: string
  title: string
  doc_version: string
  summary: string
  flowchart: string
  comparison_table: string
  key_points: string[]
  model?: string
  created_at?: string
  cached?: boolean
  degraded?: boolean
  message?: string
}

// 权益条目
export interface BenefitItem {
  title: string
  value: string
  description: string
  category?: string
  source_rule?: string
}

// 个性化权益报告
export interface BenefitReport {
  year: number
  user_name: string
  department_name?: string | null
  tenure_years?: number | null
  items: BenefitItem[]
  summary: string
  model?: string
  created_at?: string
  cached?: boolean
}

export interface CorrectionRequest {
  request_id: string
  document_id: string
  document_title?: string
  section: string
  description: string
  submitted_by: string
  submitter_name?: string
  reviewed_by: string
  reviewer_name?: string
  status: 'pending' | 'approved' | 'rejected'
  review_comment: string
  created_at: string
  reviewed_at: string
}

// 问答统计
export interface QAStatistics {
  today_count: number
  yesterday_count: number
  active_users: number
  total_documents: number
  published_documents: number
  faq_count: number
  active_faq_count: number
  trend: { date: string; count: number }[]
  type_distribution: { name: string; value: number }[]
  hot_questions: { question: string; count: number }[]
  category_coverage: { name: string; value: number }[]
}

// 反馈信息
export interface FeedbackRequest {
  record_id: string
  feedback: 'helpful' | 'not_helpful'
  reason?: string
}
