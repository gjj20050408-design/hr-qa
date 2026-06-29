<template>
  <div class="notifications-layout">
    <div class="notifications-header">
      <div>
        <h2>通知消息</h2>
        <p>共 <strong>{{ notifications.length }}</strong> 条通知，<span class="unread-count">{{ unreadCount }}</span> 条未读</p>
      </div>
      <div class="header-actions">
        <el-button size="small" @click="markAllRead">全部已读</el-button>
        <el-select v-model="filter" size="small" class="filter-select">
          <el-option label="全部" value="all" />
          <el-option label="未读" value="unread" />
          <el-option label="重要" value="important" />
          <el-option label="紧急" value="urgent" />
        </el-select>
      </div>
    </div>

    <div class="notifications-list">
      <div
        v-for="item in filteredNotifications"
        :key="item.announcement_id"
        class="notification-card"
        :class="{
          urgent: item.priority === 'urgent',
          unread: !item.is_read,
          read: item.is_read,
        }"
        @click="handleRead(item)"
      >
        <div class="notify-body">
          <div class="notify-icon" :class="item.priority">
            <el-icon v-if="item.priority === 'urgent'" :size="20"><Warning /></el-icon>
            <el-icon v-else-if="item.priority === 'important'" :size="20"><Bell /></el-icon>
            <el-icon v-else :size="20"><InfoFilled /></el-icon>
          </div>
          <div class="notify-content">
            <div class="notify-tags">
              <el-tag
                :type="item.priority === 'urgent' ? 'danger' : item.priority === 'important' ? 'warning' : 'info'"
                size="small"
              >
                {{ priorityLabel(item.priority) }}
              </el-tag>
              <span v-if="!item.is_read" class="unread-dot"></span>
              <span v-if="!item.is_read" class="unread-text">未读</span>
            </div>
            <h3>{{ item.title }}</h3>
            <p class="notify-desc">{{ item.content }}</p>
            <div class="notify-meta">
              <span>{{ item.publisher_name || '系统' }} · {{ item.published_at?.slice(0, 16) }}</span>
              <el-button link type="primary" size="small">查看详情</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import type { Announcement } from '@/types'
import { getNotifications, markAsRead, markAllRead as markAllReadApi } from '@/api/notification'
import { ElMessage } from 'element-plus'

const filter = ref('all')
const notifications = ref<Announcement[]>([])

async function loadNotifications() {
  try {
    const res = await getNotifications({ page_size: 100 })
    notifications.value = (res.data?.items || []).map((n: Announcement) => ({
      ...n,
      is_read: n.is_read ?? false,
    }))
  } catch {}
}

onMounted(loadNotifications)

const unreadCount = computed(() => notifications.value.filter(n => !n.is_read).length)

const filteredNotifications = computed(() => {
  if (filter.value === 'unread') return notifications.value.filter(n => !n.is_read)
  if (filter.value === 'urgent') return notifications.value.filter(n => n.priority === 'urgent')
  if (filter.value === 'important') return notifications.value.filter(n => n.priority === 'important')
  return notifications.value
})

function priorityLabel(p: string) {
  const map: Record<string, string> = { urgent: '紧急', important: '重要', normal: '公告' }
  return map[p] || '公告'
}

async function handleRead(item: Announcement) {
  if (!item.is_read) {
    try {
      await markAsRead(item.announcement_id)
      item.is_read = true
    } catch {}
  }
}

async function markAllRead() {
  try {
    await markAllReadApi()
    notifications.value.forEach(n => n.is_read = true)
    ElMessage.success('已全部标记为已读')
  } catch {}
}
</script>

<style scoped>
.notifications-layout {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.notifications-header {
  padding: 24px;
  background: white;
  border-bottom: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}
.notifications-header h2 {
  font-size: 18px;
  font-weight: 700;
  color: var(--primary);
}
.notifications-header p {
  font-size: 14px;
  color: #94a3b8;
  margin-top: 4px;
}
.unread-count {
  color: var(--danger);
  font-weight: 600;
}
.header-actions {
  display: flex;
  gap: 8px;
}
.filter-select {
  width: 100px;
}

.notifications-list {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
}

.notification-card {
  padding: 20px;
  border-radius: 12px;
  margin-bottom: 12px;
  cursor: pointer;
  transition: all 0.15s;
}
.notification-card:hover {
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}
.notification-card.urgent {
  background: #fef2f2;
  border: 1px solid #fecaca;
}
.notification-card:not(.urgent) {
  background: white;
  border: 1px solid var(--border);
}
.notification-card.read {
  opacity: 0.75;
}

.notify-body {
  display: flex;
  gap: 16px;
}
.notify-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  margin-top: 2px;
}
.notify-icon.urgent {
  background: #fee2e2;
  color: #ef4444;
}
.notify-icon.important {
  background: #fef3c7;
  color: #f59e0b;
}
.notify-icon.normal {
  background: #dbeafe;
  color: #3b82f6;
}

.notify-content {
  flex: 1;
}
.notify-tags {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}
.unread-dot {
  width: 8px;
  height: 8px;
  background: var(--accent);
  border-radius: 50%;
}
.unread-text {
  font-size: 12px;
  color: var(--accent);
  font-weight: 500;
}
.notify-content h3 {
  font-size: 14px;
  font-weight: 600;
  color: #334155;
  margin-bottom: 4px;
}
.notify-desc {
  font-size: 13px;
  color: #64748b;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 12px;
}
.notify-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #94a3b8;
}
</style>
