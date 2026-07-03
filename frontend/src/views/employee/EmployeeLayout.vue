<template>
  <div class="employee-layout">
    <!-- 顶部导航 -->
    <header class="top-header">
      <div class="header-left">
        <div class="logo-icon">
          <el-icon :size="20"><Document /></el-icon>
        </div>
        <span class="logo-text">HR制度智能问答</span>
        <nav class="view-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.key"
            :class="{ active: currentView === tab.key }"
            @click="navigate(tab.key)"
          >
            {{ tab.label }}
          </button>
        </nav>
      </div>
      <div class="header-right">
        <el-badge :value="unreadCount" :hidden="!unreadCount" class="notify-btn">
          <el-button link @click="navigate('notifications')">
            <el-icon :size="20"><Bell /></el-icon>
          </el-button>
        </el-badge>
        <div class="user-info">
          <el-avatar :size="32" :src="authStore.user?.avatar_url || undefined" class="user-avatar">
            {{ authStore.user?.name?.charAt(0) }}
          </el-avatar>
          <div class="user-detail">
            <span class="user-name">{{ authStore.user?.name }}</span>
            <span class="user-role">{{ roleLabel }}</span>
          </div>
        </div>
        <el-dropdown trigger="click" @command="handleCommand">
          <el-button link class="dropdown-btn">
            <el-icon><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人中心</el-dropdown-item>
              <el-dropdown-item command="admin" v-if="authStore.isAdmin || authStore.isHR">管理后台</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>

    <!-- 主内容区 -->
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { getNotifications } from '@/api/notification'
import { Document, Bell, ArrowDown, FolderOpened } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const baseTabs = [
  { key: 'search', label: '制度搜索', route: '/employee/search' },
  { key: 'chat', label: 'AI问答', route: '/employee/chat' },
  { key: 'interpretation', label: '制度解读', route: '/employee/interpretation' },
  { key: 'benefits', label: '我的权益', route: '/employee/benefits' },
  { key: 'faq', label: '常见问题', route: '/employee/faq' },
  { key: 'notifications', label: '通知消息', route: '/employee/notifications' },
  { key: 'history', label: '问答历史', route: '/employee/history' },
  { key: 'favorites', label: '我的收藏', route: '/employee/favorites' },
]

// HR 角色可见的知识库管理 tab
const hrTab = { key: 'knowledge', label: '知识库管理', route: '/employee/knowledge' }

const tabs = computed(() => {
  if (authStore.isHR) {
    // 在"常见问题"前插入知识库管理（索引 4：search/chat/interpretation/benefits 之后）
    return [
      ...baseTabs.slice(0, 4),
      hrTab,
      ...baseTabs.slice(4),
    ]
  }
  return baseTabs
})

const roleLabel = computed(() => {
  const roleMap: Record<string, string> = {
    admin: '管理员',
    hr_specialist: 'HR专员',
    employee: '普通员工',
    manager: '部门经理',
  }
  return roleMap[authStore.user?.role || ''] || '普通员工'
})

const currentView = computed(() => {
  const path = route.path.split('/').pop() || 'search'
  return path
})

function navigate(key: string) {
  const allTabs = [...baseTabs]
  if (authStore.isHR) {
    allTabs.splice(4, 0, hrTab)
  }
  const tab = allTabs.find(t => t.key === key)
  if (tab) router.push(tab.route)
}

const unreadCount = ref(0)

async function loadUnreadCount() {
  try {
    const res = await getNotifications({ page_size: 100 })
    const items = res.data?.items || []
    unreadCount.value = items.filter((n: any) => !n.is_read).length
  } catch {}
}

onMounted(loadUnreadCount)

function handleCommand(cmd: string) {
  if (cmd === 'logout') {
    authStore.logout()
    router.push('/login')
  } else if (cmd === 'admin') {
    router.push('/admin')
  } else if (cmd === 'profile') {
    router.push('/profile')
  }
}
</script>

<style scoped>
.employee-layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--surface);
}

/* 顶部导航 */
.top-header {
  height: 56px;
  background: white;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
  z-index: 30;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}
.logo-icon {
  width: 32px;
  height: 32px;
  background: var(--accent);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}
.logo-text {
  font-weight: 600;
  color: var(--primary);
  font-size: 14px;
  display: none;
}
@media (min-width: 640px) {
  .logo-text { display: inline; }
}

.view-tabs {
  display: flex;
  gap: 4px;
  margin-left: 24px;
}
.view-tabs button {
  padding: 4px 12px;
  font-size: 12px;
  font-weight: 500;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  transition: all 0.15s;
}
.view-tabs button:hover {
  background: var(--surface-muted);
  color: #334155;
}
.view-tabs button.active {
  background: var(--accent);
  color: white;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.notify-btn {
  cursor: pointer;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-left: 12px;
  border-left: 1px solid var(--border);
}
.user-avatar {
  background: var(--accent) !important;
  color: white !important;
  font-weight: 600;
  font-size: 12px;
}
.user-detail {
  display: none;
  flex-direction: column;
}
@media (min-width: 640px) {
  .user-detail { display: flex; }
}
.user-name {
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}
.user-role {
  font-size: 12px;
  color: #94a3b8;
}
.dropdown-btn {
  color: #94a3b8;
}

/* 主内容 */
.main-content {
  flex: 1;
  overflow: hidden;
  display: flex;
}
</style>
