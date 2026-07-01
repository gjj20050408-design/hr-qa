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
          <div class="session-info">
            <p class="session-title">{{ session.title }}</p>
            <p class="session-time">{{ formatTime(session.created_at) }}</p>
          </div>
          <el-dropdown trigger="click" placement="bottom-end" @command="(cmd: string) => handleSessionAction(cmd, session)" @click.stop>
            <el-button class="more-btn" link @click.stop>
              <el-icon><MoreFilled /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu class="session-menu">
                <el-dropdown-item command="rename">
                  <el-icon><EditPen /></el-icon>
                  <span>重命名</span>
                </el-dropdown-item>
                <el-dropdown-item command="pin">
                  <el-icon><Star /></el-icon>
                  <span>{{ session.is_pinned ? '取消置顶' : '置顶' }}</span>
                </el-dropdown-item>
                <el-dropdown-item command="delete" divided class="danger-item">
                  <el-icon><Delete /></el-icon>
                  <span>删除</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
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
              <div class="message-bubble ai-bubble" :class="{ 'permission-denied-bubble': msg.is_permission_denied }">
                <div v-if="msg.is_permission_denied" class="permission-denied-icon">🔒 权限受限</div>
                <div class="answer-text" v-html="formatAnswer(msg.content)"></div>
                <div class="answer-source" v-if="msg.reference_docs?.length">
                  <span class="source-label">来源：{{ msg.reference_docs[0].title }}</span>
                  <span class="source-time" v-if="msg.response_time_ms">响应：{{ (msg.response_time_ms / 1000).toFixed(2) }}s</span>
                </div>
              </div>

              <!-- 操作按钮（权限拒绝的回答不显示） -->
              <div class="feedback-row" v-if="msg.role === 'assistant' && !msg.is_permission_denied">
                <template v-if="idx === chatStore.messages.length - 1">
                  <el-button size="small" text @click="handleFeedback(msg.id, 'helpful')">
                    <el-icon><Pointer /></el-icon> 有帮助
                  </el-button>
                  <el-button size="small" text @click="handleFeedback(msg.id, 'not_helpful')">
                    <el-icon><Pointer /></el-icon> 无帮助
                  </el-button>
                </template>
                <el-button size="small" text :type="msg.is_favorite ? 'warning' : ''" @click="handleFavorite(msg.id, idx)">
                  <el-icon><StarFilled v-if="msg.is_favorite" /><Star v-else /></el-icon> {{ msg.is_favorite ? '已收藏' : '收藏' }}
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
import { ref, computed, nextTick, watch, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Delete, Pointer, Star, StarFilled, Loading, Position, MoreFilled, EditPen } from '@element-plus/icons-vue'

const authStore = useAuthStore()
const chatStore = useChatStore()
const inputText = ref('')
const messageListRef = ref<HTMLElement>()

// 页面加载时获取会话列表
onMounted(() => {
  chatStore.loadSessions()
})

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

function formatTime(time: string) {
  if (!time) return ''
  try {
    const d = new Date(time)
    return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
  } catch {
    return time
  }
}

async function handleSend() {
  const text = inputText.value.trim()
  if (!text || chatStore.isLoading) return
  inputText.value = ''
  await chatStore.sendMessage(text)
}

function deleteCurrentSession() {
  if (chatStore.currentSessionId) {
    handleSessionAction('delete', chatStore.sessions.find(s => s.session_id === chatStore.currentSessionId) as any)
  }
}

async function handleSessionAction(cmd: string, session: any) {
  if (cmd === 'rename') {
    try {
      const { value } = await ElMessageBox.prompt('请输入新的会话名称', '重命名会话', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputValue: session.title,
        inputPattern: /.+/,
        inputErrorMessage: '名称不能为空',
      })
      const ok = await chatStore.renameSession(session.session_id, value)
      ElMessage[ok ? 'success' : 'error'](ok ? '重命名成功' : '重命名失败')
    } catch {
      // 用户取消
    }
  } else if (cmd === 'pin') {
    const isPinned = await chatStore.togglePinSession(session.session_id)
    ElMessage.success(isPinned ? '已置顶' : '已取消置顶')
  } else if (cmd === 'delete') {
    try {
      await ElMessageBox.confirm('确定删除该会话吗？所有对话记录将被清除。', '删除会话', {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger',
      })
      await chatStore.removeSession(session.session_id)
      ElMessage.success('会话已删除')
    } catch {
      // 用户取消
    }
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

async function handleFavorite(recordId: string, idx: number) {
  try {
    const msg = chatStore.messages[idx]
    const newState = !msg.is_favorite
    const result = await chatStore.toggleFavorite(recordId, newState)
    msg.is_favorite = result
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
  display: flex;
  align-items: center;
  gap: 4px;
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
.session-info {
  flex: 1;
  min-width: 0;
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
.more-btn {
  flex-shrink: 0;
  padding: 4px;
  color: #94a3b8;
  opacity: 0;
  transition: opacity 0.15s;
}
.session-item:hover .more-btn,
.session-item.active .more-btn {
  opacity: 1;
}
.more-btn:hover {
  color: var(--accent);
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

.permission-denied-bubble {
  background: #f1f5f9 !important;
  border: 1px dashed #cbd5e1;
}
.permission-denied-icon {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  gap: 4px;
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

<style>
/* 会话下拉菜单样式（非 scoped，覆盖 element-plus） */
.session-menu .el-dropdown-menu__item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  font-size: 14px;
}
.session-menu .el-dropdown-menu__item .el-icon {
  font-size: 16px;
}
.session-menu .danger-item {
  color: #ef4444 !important;
}
.session-menu .danger-item .el-icon {
  color: #ef4444 !important;
}
.session-menu .danger-item:hover {
  background: #fef2f2 !important;
  color: #ef4444 !important;
}
</style>
