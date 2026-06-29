import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '@/types'
import { login as loginApi, register as registerApi, getCurrentUser, logout as logoutApi } from '@/api/auth'
import type { LoginRequest, RegisterRequest } from '@/types'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<UserInfo | null>(null)
  const accessToken = ref<string>(localStorage.getItem('access_token') || '')
  const refreshToken = ref<string>(localStorage.getItem('refresh_token') || '')

  // 是否已登录
  const isLoggedIn = computed(() => !!accessToken.value)
  // 是否为管理员
  const isAdmin = computed(() => user.value?.role === 'admin')
  // 是否为HR
  const isHR = computed(() => user.value?.role === 'hr_specialist' || user.value?.role === 'admin')

  // 登录
  async function login(data: LoginRequest) {
    const res = await loginApi(data)
    accessToken.value = res.data.access_token
    refreshToken.value = res.data.refresh_token
    user.value = res.data.user
    localStorage.setItem('access_token', res.data.access_token)
    localStorage.setItem('refresh_token', res.data.refresh_token)
    localStorage.setItem('user_info', JSON.stringify(res.data.user))
  }

  // 注册
  async function register(data: RegisterRequest) {
    await registerApi(data)
  }

  // 获取用户信息
  async function fetchUserInfo() {
    if (accessToken.value) {
      try {
        const res = await getCurrentUser()
        user.value = res.data
      } catch {
        clearAuth()
      }
    }
  }

  // 退出登录
  async function logout() {
    try {
      await logoutApi()
    } finally {
      clearAuth()
    }
  }

  // 清除认证信息
  function clearAuth() {
    accessToken.value = ''
    refreshToken.value = ''
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_info')
  }

  // 从localStorage恢复用户信息
  function restoreUser() {
    const token = localStorage.getItem('access_token')
    if (token) {
      accessToken.value = token
    }
    const stored = localStorage.getItem('user_info')
    if (stored) {
      try {
        user.value = JSON.parse(stored)
      } catch {
        // ignore
      }
    }
  }

  return {
    user,
    accessToken,
    refreshToken,
    isLoggedIn,
    isAdmin,
    isHR,
    login,
    register,
    fetchUserInfo,
    logout,
    clearAuth,
    restoreUser,
  }
})
