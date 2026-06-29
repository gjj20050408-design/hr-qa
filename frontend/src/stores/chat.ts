import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ChatSession, ChatMessage, QARecord } from '@/types'
import {
  sendQuestion,
  getSessions,
  getSessionMessages,
  deleteSession as deleteSessionApi,
  renameSession as renameSessionApi,
  togglePinSession as togglePinSessionApi,
  toggleFavorite as toggleFavoriteApi,
  submitFeedback as submitFeedbackApi,
} from '@/api/chat'

export const useChatStore = defineStore('chat', () => {
  const sessions = ref<ChatSession[]>([])
  const currentSessionId = ref<string>('')
  const messages = ref<ChatMessage[]>([])
  const isLoading = ref(false)

  // 加载会话列表
  async function loadSessions() {
    try {
      const res = await getSessions()
      sessions.value = res.data.data?.items || []
    } catch {
      // ignore
    }
  }

  // 创建新会话
  function createNewSession() {
    currentSessionId.value = ''
    messages.value = []
  }

  // 选择会话
  async function selectSession(sessionId: string) {
    currentSessionId.value = sessionId
    try {
      const res = await getSessionMessages(sessionId)
      const records = res.data.data?.items || []
      // 每条记录生成 user + assistant 两条消息，按时间正序排列
      const msgs: ChatMessage[] = []
      for (const r of records) {
        msgs.push({
          id: r.record_id + '-q',
          role: 'user',
          content: r.question,
          created_at: r.created_at,
        })
        msgs.push({
          id: r.record_id,
          role: 'assistant',
          content: r.answer,
          answer_type: r.answer_type,
          reference_docs: r.reference_docs,
          response_time_ms: r.response_time_ms,
          is_favorite: r.is_favorite,
          is_permission_denied: r.answer?.startsWith('🔒'),
          created_at: r.created_at,
        })
      }
      messages.value = msgs
    } catch {
      // ignore
    }
  }

  // 发送问题
  async function sendMessage(question: string) {
    if (!question.trim()) return

    // 添加用户消息
    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: question,
      created_at: new Date().toISOString(),
    }
    messages.value.push(userMsg)

    isLoading.value = true
    try {
      const res = await sendQuestion({
        question,
        session_id: currentSessionId.value || undefined,
      })
      const record = res.data.data

      // 更新会话ID
      if (!currentSessionId.value) {
        currentSessionId.value = record.session_id
      }

      // 检查权限拒绝标识
      const isPermissionDenied = record.answer?.startsWith('🔒')

      // 添加助手消息
      const assistantMsg: ChatMessage = {
        id: record.record_id,
        role: 'assistant',
        content: record.answer,
        answer_type: record.answer_type,
        reference_docs: record.reference_docs,
        response_time_ms: record.response_time_ms,
        is_favorite: false,
        is_permission_denied: isPermissionDenied,
        created_at: record.created_at,
      }
      messages.value.push(assistantMsg)

      // 刷新会话列表
      await loadSessions()
    } catch {
      // 添加错误消息
      messages.value.push({
        id: Date.now().toString(),
        role: 'assistant',
        content: '抱歉，服务暂时不可用，请稍后重试。',
        created_at: new Date().toISOString(),
      })
    } finally {
      isLoading.value = false
    }
  }

  // 删除会话
  async function removeSession(sessionId: string) {
    try {
      await deleteSessionApi(sessionId)
      sessions.value = sessions.value.filter(s => s.session_id !== sessionId)
      if (currentSessionId.value === sessionId) {
        createNewSession()
      }
    } catch {
      // ignore
    }
  }

  // 重命名会话
  async function renameSession(sessionId: string, title: string): Promise<boolean> {
    try {
      await renameSessionApi(sessionId, title)
      const s = sessions.value.find(s => s.session_id === sessionId)
      if (s) s.title = title
      return true
    } catch {
      return false
    }
  }

  // 切换置顶
  async function togglePinSession(sessionId: string): Promise<boolean> {
    try {
      const res = await togglePinSessionApi(sessionId)
      const isPinned = res.data.data?.is_pinned ?? false
      // 重新加载列表以应用排序
      await loadSessions()
      return isPinned
    } catch {
      return false
    }
  }

  // 切换收藏
  async function toggleFavorite(recordId: string, isFavorite: boolean): Promise<boolean> {
    try {
      const res = await toggleFavoriteApi(recordId, isFavorite)
      return res.data?.is_favorite ?? false
    } catch {
      return false
    }
  }

  // 提交反馈
  async function submitFeedback(recordId: string, feedback: 'helpful' | 'not_helpful', reason?: string) {
    await submitFeedbackApi(recordId, feedback, reason)
  }

  return {
    sessions,
    currentSessionId,
    messages,
    isLoading,
    loadSessions,
    createNewSession,
    selectSession,
    sendMessage,
    removeSession,
    renameSession,
    togglePinSession,
    toggleFavorite,
    submitFeedback,
  }
})
