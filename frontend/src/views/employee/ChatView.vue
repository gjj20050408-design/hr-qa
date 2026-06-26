<template>
  <div class="chat-layout">
    <!-- 左侧会话列表 -->
    <aside class="chat-sessions">
      <div class="sessions-header">
        <el-button type="primary" class="new-session-btn" @click="chatStore.createNewSession()">
          <el-icon><Plus /></el-icon>
          新建会话
        </el-button>
      </div>
      <div class="session-list">
        <div
          v-for="session in chatStore.sessions"
          :key="session.session_id"
          class="session-item"
          :class="{ active: chatStore.currentSessionId === session.session_id }"
          @click="chatStore.selectSession(session.session_id)"
        >
          <p class="session-title">{{ session.title }}</p>
          <p class="session-time">{{ session.created_at }}</p>
        </div>
        <el-empty v-if="!chatStore.sessions.length" description="暂无会话" :image-size="60" />
      </div>
    </aside>

    <!-- 右侧对话区 -->
    <section class="chat-main">
      <!-- 对话头部 -->
      <div class="chat-header">
        <h2>{{ currentSessionTitle }}</h2>
        <el-button link @click="deleteCurrentSession" v-if="chatStore.currentSessionId">
          <el-icon :size="20"><Delete /></el-icon>
        </el-button>
      </div>

      <!-- 消息列表 -->
      <div class="message-list" ref="messageListRef">
        <el-empty v-if="!chatStore.messages.length && !chatStore.currentSessionId" description="开始新的对话吧" :image-size="80" />

        <template v-for="(msg, idx) in chatStore.messages" :key="msg.id">
          <!-- 用户消息 -->
          <div v-if="msg.role === 'user'" class="message-row user-row">
            <div class="message-bubble user-bubble">
              {{ msg.content }}
            </div>
            <el-avatar :size="32" class="user-avatar-sm">
              {{ authStore.user?.name?.charAt(0) }}
            </el-avatar>
          </div>

          <!-- AI消息 -->
          <div v-else class="message-row assistant-row">
            <el-avatar :size="32" class="ai-avatar">AI</el-avatar>
            <div class="message-content">
              <div class="message-bubble ai-bubble">
                <div class="answer-text" v-html="formatAnswer(msg.content)"></div>
                <div class="answer-source" v-if="msg.reference_docs?.length">
                  <span class="source-label">来源：{{ msg.reference_docs[0].title }}</span>
                  <span class="source-time">响应：{{ msg.response_time_ms }}ms</span>
                </div>
              </div>

              <!-- 反馈按钮 -->
              <div class="feedback-row" v-if="idx === chatStore.messages.length - 1 && msg.role === 'assistant'">
                <el-button size="small" text @click="handleFeedback(msg.id, 'helpful')">
                  <el-icon><Pointer /></el-icon> 有帮助
                </el-button>
                <el-button size="small" text @click="handleFeedback(msg.id, 'not_helpful')">
                  <el-icon><Pointer /></el-icon> 无帮助
                </el-button>
                <el-button size="small" text @click="handleFavorite(msg.id)">
                  <el-icon><Star /></el-icon> 收藏
                </el-button>
              </div>
            </div>
          </div>
        </template>

        <!-- 加载状态 -->
        <div v-if="chatStore.isLoading" class="loading-indicator">
          <el-icon class="is-loading" :size="20"><Loading /></el-icon>
          <span>AI正在思考...</span>
        </div>
      </div>

      <!-- 输入区 -->
      <div class="chat-input-area">
        <div class="input-row">
          <el-input
            v-model="inputText"
            type="textarea"
            :rows="2"
            placeholder="输入您的问题..."
            @keyup.enter.exact="handleSend"
            resize="none"
          />
          <el-button
            type="primary"
            class="send-btn"
            :loading="chatStore.isLoading"
            @click="handleSend"
          >
            <el-icon :size="16"><Position /></el-icon>
          </el-button>
        </div>
        <p class="input-tip">AI回答仅供参考，请以制度原文为准 | 每分钟限20次提问</p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { ElMessage } from 'element-plus'
import { Plus, Delete, Pointer, Star, Loading, Position } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const chatStore = useChatStore()
const inputText = ref('')
const messageListRef = ref<HTMLElement>()

const currentSessionTitle = computed(() => {
  const session = chatStore.sessions.find(s => s.session_id === chatStore.currentSessionId)
  return session?.title || '新对话'
})

// 滚动到底部
watch(() => chatStore.messages.length, async () => {
  await nextTick()
  if (messageListRef.value) {
    messageListRef.value.scrollTop = messageListRef.value.scrollHeight
  }
})

function formatAnswer(text: string) {
  return text
    .replace(/✅/g, '<span style="color: #10b981">✅</span>')
    .replace(/⚠️/g, '<span style="color: #f59e0b">⚠️</span>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>')
}

async function handleSend() {
  const text = inputText.value.trim()
  if (!text || chatStore.isLoading) return
  inputText.value = ''
  await chatStore.sendMessage(text)
}

function deleteCurrentSession() {
  if (chatStore.currentSessionId) {
    chatStore.removeSession(chatStore.currentSessionId)
  }
}

async function handleFeedback(recordId: string, feedback: 'helpful' | 'not_helpful') {
  try {
    await chatStore.submitFeedback(recordId, feedback)
    ElMessage.success('感谢您的反馈')
  } catch {
    // ignore
  }
}

async function handleFavorite(recordId: string) {
  try {
    const result = await chatStore.toggleFavorite(recordId)
    ElMessage.success(result ? '已收藏' : '已取消收藏')
  } catch {
    // ignore
  }
}
</script>

<style scoped>
.chat-layout {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* 左侧会话列表 */
.chat-sessions {
  width: 280px;
  border-right: 1px solid var(--border);
  background: white;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}
@media (max-width: 768px) {
  .chat-sessions { display: none; }
}

.sessions-header {
  padding: 16px;
  border-bottom: 1px solid var(--border);
}
.new-session-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}
.session-item {
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
  margin-bottom: 4px;
}
.session-item:hover {
  background: var(--surface-muted);
}
.session-item.active {
  background: rgba(3, 105, 161, 0.1);
}
.session-title {
  font-size: 14px;
  font-weight: 500;
  color: #334155;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.active .session-title {
  color: var(--accent);
}
.session-time {
  font-size: 12px;
  color: #94a3b8;
  margin-top: 2px;
}

/* 右侧对话区 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--surface);
}
.chat-header {
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.chat-header h2 {
  font-size: 16px;
  font-weight: 600;
  color: var(--primary);
}

.message-list {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.message-row {
  display: flex;
  margin-bottom: 24px;
}
.user-row {
  justify-content: flex-end;
}
.assistant-row {
  justify-content: flex-start;
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  font-size: 14px;
  line-height: 1.6;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}
.user-bubble {
  background: var(--accent);
  color: white;
  border-radius: 16px 16px 4px 16px;
  margin-right: 0;
}
.ai-bubble {
  background: var(--surface-muted);
  color: #334155;
  border-radius: 16px 16px 16px 4px;
}

.user-avatar-sm {
  background: var(--accent) !important;
  color: white !important;
  font-weight: 600;
  font-size: 12px;
  margin-left: 12px;
  flex-shrink: 0;
}
.ai-avatar {
  background: linear-gradient(135deg, #60a5fa, #3b82f6) !important;
  color: white !important;
  font-weight: 700;
  font-size: 12px;
  margin-right: 12px;
  flex-shrink: 0;
}

.message-content {
  max-width: 70%;
}

.answer-text {
  margin-bottom: 8px;
}
.answer-source {
  font-size: 12px;
  color: #94a3b8;
  padding-top: 8px;
  border-top: 1px solid #e2e8f0;
  display: flex;
  gap: 12px;
}

.feedback-row {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 12px;
}
.feedback-row .el-button {
  color: #94a3b8;
  font-size: 12px;
}

.loading-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #94a3b8;
  font-size: 13px;
  padding: 12px 0;
}

/* 输入区 */
.chat-input-area {
  padding: 16px 24px;
  background: white;
  border-top: 1px solid var(--border);
}
.input-row {
  display: flex;
  gap: 12px;
  align-items: flex-end;
}
.input-row :deep(.el-textarea__inner) {
  border-radius: 12px;
  background: var(--surface);
}
.send-btn {
  border-radius: 8px;
  padding: 8px 12px;
}
.input-tip {
  font-size: 12px;
  color: #94a3b8;
  text-align: center;
  margin-top: 8px;
}
</style>
