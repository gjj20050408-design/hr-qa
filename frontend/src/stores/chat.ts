import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ChatSession, ChatMessage, QARecord } from '@/types'
import {
  sendQuestion,
  getSessions,
  getSessionMessages,
  deleteSession as deleteSessionApi,
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
      sessions.value = res.data
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
      messages.value = res.data
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
      const record = res.data

      // 更新会话ID
      if (!currentSessionId.value) {
        currentSessionId.value = record.session_id
      }

      // 添加助手消息
      const assistantMsg: ChatMessage = {
        id: record.record_id,
        role: 'assistant',
        content: record.answer,
        answer_type: record.answer_type,
        reference_docs: record.reference_docs,
        response_time_ms: record.response_time_ms,
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

  // 切换收藏
  async function toggleFavorite(recordId: string): Promise<boolean> {
    try {
      const res = await toggleFavoriteApi(recordId)
      return res.data.is_favorite
    } catch {
      return false
    }
  }

  // 提交反馈
  async function submitFeedback(recordId: string, feedback: 'helpful' | 'not_helpful', reason?: string) {
    await submitFeedbackApi(recordId, { feedback, reason })
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
    toggleFavorite,
    submitFeedback,
  }
})
