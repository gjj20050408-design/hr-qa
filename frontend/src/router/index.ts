import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/employee/search',
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue'),
      meta: { guest: true },
    },
    // 员工端
    {
      path: '/employee',
      component: () => import('@/views/employee/EmployeeLayout.vue'),
      redirect: '/employee/search',
      children: [
        {
          path: 'search',
          name: 'employee-search',
          component: () => import('@/views/employee/SearchView.vue'),
        },
        {
          path: 'chat',
          name: 'employee-chat',
          component: () => import('@/views/employee/ChatView.vue'),
        },
        {
          path: 'faq',
          name: 'employee-faq',
          component: () => import('@/views/employee/FaqView.vue'),
        },
        {
          path: 'notifications',
          name: 'employee-notifications',
          component: () => import('@/views/employee/NotificationsView.vue'),
        },
        {
          path: 'history',
          name: 'employee-history',
          component: () => import('@/views/employee/HistoryView.vue'),
        },
        {
          path: 'favorites',
          name: 'employee-favorites',
          component: () => import('@/views/employee/FavoritesView.vue'),
        },
      ],
    },
    // 管理后台
    {
      path: '/admin',
      component: () => import('@/views/admin/AdminLayout.vue'),
      meta: { requiresAdmin: true },
      redirect: '/admin/dashboard',
      children: [
        {
          path: 'dashboard',
          name: 'admin-dashboard',
          component: () => import('@/views/admin/DashboardView.vue'),
        },
        {
          path: 'documents',
          name: 'admin-documents',
          component: () => import('@/views/admin/DocumentsView.vue'),
        },
        {
          path: 'faqs',
          name: 'admin-faqs',
          component: () => import('@/views/admin/FaqsView.vue'),
        },
        {
          path: 'corrections',
          name: 'admin-corrections',
          component: () => import('@/views/admin/CorrectionsView.vue'),
        },
        {
          path: 'categories',
          name: 'admin-categories',
          component: () => import('@/views/admin/CategoriesView.vue'),
        },
        {
          path: 'announcements',
          name: 'admin-announcements',
          component: () => import('@/views/admin/AnnouncementsView.vue'),
        },
        {
          path: 'users',
          name: 'admin-users',
          component: () => import('@/views/admin/UsersView.vue'),
        },
        {
          path: 'audit',
          name: 'admin-audit',
          component: () => import('@/views/admin/AuditView.vue'),
        },
      ],
    },
  ],
})

// 路由守卫
router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()
  authStore.restoreUser()

  // 游客页面直接放行
  if (to.meta.guest) {
    return next()
  }

  // 需要管理员权限
  if (to.meta.requiresAdmin && !authStore.isAdmin) {
    return next('/employee/search')
  }

  next()
})

export default router
