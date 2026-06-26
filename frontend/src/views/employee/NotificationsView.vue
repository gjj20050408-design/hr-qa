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
import { ref, computed } from 'vue'
import type { Announcement } from '@/types'

const filter = ref('all')

// Mock数据
const notifications = ref<Announcement[]>([
  {
    announcement_id: 'ann-001',
    title: '薪酬制度 V3.0 更新通知',
    content: '薪酬制度已更新至V3.0版本，涉及薪资结构调整和个税计算方式变更，请全体员工及时查阅最新版本。',
    priority: 'urgent',
    target_type: 'all',
    target_ids: [],
    attachment: '',
    published_by: '',
    publisher_name: '系统管理员',
    published_at: '2026-06-24 09:00',
    is_read: false,
  },
  {
    announcement_id: 'ann-002',
    title: '关于2026年度健康体检安排的通知',
    content: '本年度员工健康体检将于6月25日至7月15日进行，请各部门组织员工按时参加。',
    priority: 'important',
    target_type: 'all',
    target_ids: [],
    attachment: '',
    published_by: '',
    publisher_name: 'HR部门',
    published_at: '2026-06-23 14:30',
    is_read: false,
  },
  {
    announcement_id: 'ann-003',
    title: '年假制度修订说明',
    content: '关于年假延期政策的补充说明：未休年假可延期至次年3月31日。因工作需要无法休假的特殊情况需部门总监审批。',
    priority: 'normal',
    target_type: 'all',
    target_ids: [],
    attachment: '',
    published_by: '',
    publisher_name: 'HR部门',
    published_at: '2026-06-20',
    is_read: true,
  },
  {
    announcement_id: 'ann-004',
    title: '假期申请流程优化通知',
    content: '为提升效率，OA系统假期申请流程已优化，新增移动端审批功能。',
    priority: 'normal',
    target_type: 'all',
    target_ids: [],
    attachment: '',
    published_by: '',
    publisher_name: '系统管理员',
    published_at: '2026-06-18',
    is_read: true,
  },
  {
    announcement_id: 'ann-005',
    title: 'HR制度智能问答系统正式上线',
    content: '欢迎使用HR制度智能问答系统！本系统提供7×24小时制度查询与AI问答服务。',
    priority: 'normal',
    target_type: 'all',
    target_ids: [],
    attachment: '',
    published_by: '',
    publisher_name: '系统管理员',
    published_at: '2026-06-15',
    is_read: true,
  },
])

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

function handleRead(item: Announcement) {
  item.is_read = true
}

function markAllRead() {
  notifications.value.forEach(n => n.is_read = true)
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
