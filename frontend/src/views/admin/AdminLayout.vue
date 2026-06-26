<template>
  <div class="admin-layout">
    <!-- 左侧导航 -->
    <aside class="admin-sidebar">
      <div class="sidebar-logo">
        <div class="logo-icon">
          <el-icon :size="20"><Document /></el-icon>
        </div>
        <div class="logo-text">
          <h1>HR问答系统</h1>
          <p>管理后台</p>
        </div>
      </div>

      <nav class="sidebar-nav">
        <div class="nav-section-title">核心功能</div>

        <router-link
          v-for="item in coreNav"
          :key="item.key"
          :to="item.route"
          class="nav-item"
          active-class="active"
        >
          <component :is="item.icon" class="nav-icon" />
          <span>{{ item.label }}</span>
          <span v-if="item.badge" class="nav-badge">{{ item.badge }}</span>
        </router-link>

        <div class="nav-section-title">内容运营</div>

        <router-link
          v-for="item in contentNav"
          :key="item.key"
          :to="item.route"
          class="nav-item"
          active-class="active"
        >
          <component :is="item.icon" class="nav-icon" />
          <span>{{ item.label }}</span>
        </router-link>

        <div class="nav-section-title">系统管理</div>

        <router-link
          v-for="item in systemNav"
          :key="item.key"
          :to="item.route"
          class="nav-item"
          active-class="active"
        >
          <component :is="item.icon" class="nav-icon" />
          <span>{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="sidebar-footer">
        <router-link to="/employee/search" class="switch-link">
          <el-icon><Back /></el-icon>
          切换到员工端
        </router-link>
      </div>
    </aside>

    <!-- 右侧主内容 -->
    <main class="admin-main">
      <header class="admin-header">
        <h2>{{ pageTitle }}</h2>
        <div class="header-user">
          <el-avatar :size="28" class="admin-avatar">管</el-avatar>
          <span>系统管理员</span>
        </div>
      </header>

      <div class="admin-content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  Document, Back, Grid, Files, QuestionFilled,
  CircleCheck, Lock, Bell, User, List
} from '@element-plus/icons-vue'

const route = useRoute()

const pageTitle = computed(() => {
  const map: Record<string, string> = {
    dashboard: '数据驾驶舱',
    documents: '文档管理',
    faqs: 'FAQ 管理',
    corrections: '纠错审核',
    categories: '分类权限',
    announcements: '通知公告',
    users: '用户管理',
    audit: '审计日志',
  }
  const key = route.path.split('/').pop() || 'dashboard'
  return map[key] || '管理后台'
})

const coreNav = [
  { key: 'dashboard', label: '数据驾驶舱', route: '/admin/dashboard', icon: Grid },
  { key: 'documents', label: '文档管理', route: '/admin/documents', icon: Files },
  { key: 'faqs', label: 'FAQ 管理', route: '/admin/faqs', icon: QuestionFilled },
  { key: 'corrections', label: '纠错审核', route: '/admin/corrections', icon: CircleCheck, badge: '3' },
  { key: 'categories', label: '分类权限', route: '/admin/categories', icon: Lock },
]

const contentNav = [
  { key: 'announcements', label: '通知公告', route: '/admin/announcements', icon: Bell },
]

const systemNav = [
  { key: 'users', label: '用户管理', route: '/admin/users', icon: User },
  { key: 'audit', label: '审计日志', route: '/admin/audit', icon: List },
]
</script>

<style scoped>
.admin-layout {
  height: 100vh;
  display: flex;
  overflow: hidden;
}

/* 左侧导航 */
.admin-sidebar {
  width: 240px;
  background: white;
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-logo {
  padding: 20px 20px 16px;
  display: flex;
  align-items: center;
  gap: 12px;
}
.logo-icon {
  width: 32px;
  height: 32px;
  background: var(--primary);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  flex-shrink: 0;
}
.logo-text h1 {
  font-size: 14px;
  font-weight: 700;
  color: var(--primary);
}
.logo-text p {
  font-size: 11px;
  color: #94a3b8;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 0 12px;
}

.nav-section-title {
  font-size: 11px;
  font-weight: 600;
  color: #94a3b8;
  letter-spacing: 0.05em;
  padding: 16px 12px 4px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
  text-decoration: none;
  margin-bottom: 4px;
  transition: all 0.15s;
}
.nav-item:hover {
  background: var(--surface-muted);
  color: #334155;
}
.nav-item.active {
  background: #eff6ff;
  color: var(--accent);
  font-weight: 600;
}
.nav-icon { flex-shrink: 0; }

.nav-badge {
  margin-left: auto;
  min-width: 20px;
  height: 20px;
  background: var(--danger);
  color: white;
  font-size: 10px;
  font-weight: 700;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-footer {
  padding: 12px;
  border-top: 1px solid var(--border);
}
.switch-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 8px;
  font-size: 12px;
  color: #94a3b8;
  border-radius: 8px;
  transition: all 0.15s;
}
.switch-link:hover {
  color: var(--accent);
  background: rgba(3, 105, 161, 0.05);
}

/* 右侧主内容 */
.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.admin-header {
  height: 56px;
  background: white;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  flex-shrink: 0;
}
.admin-header h2 {
  font-size: 16px;
  font-weight: 600;
  color: var(--primary);
}
.header-user {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #475569;
}
.admin-avatar {
  background: var(--primary) !important;
  color: white !important;
  font-weight: 600;
  font-size: 12px;
}

.admin-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}
</style>
