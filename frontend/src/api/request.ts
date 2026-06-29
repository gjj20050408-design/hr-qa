import axios, { type AxiosResponse, type InternalAxiosRequestConfig } from 'axios'
import type { ApiResponse } from '@/types'
import { ElMessage } from 'element-plus'

// 创建 Axios 实例
const request = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
    'X-Client-Platform': 'web',
  },
})

// 请求拦截器 - 自动附加 Token
request.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('access_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器 - 统一错误处理
request.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    const { data } = response
    if (data.code !== 0) {
      ElMessage.error(data.message || '请求失败')
      // Token过期或无效
      if (data.code === 10001 || data.code === 10002) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user_info')
        window.location.href = '/login'
      }
      return Promise.reject(new Error(data.message))
    }
    return response
  },
  (error) => {
    const status = error.response?.status
    const backendDetail = error.response?.data?.detail
    const message =
      (typeof backendDetail === 'object' && backendDetail?.message)
        || error.response?.data?.message
        || error.message
        || '网络错误'
    if (status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_info')
      window.location.href = '/login'
    } else if (status === 403) {
      ElMessage.error('无权限访问该资源')
    } else if (status === 429) {
      ElMessage.error('请求频率超限，请稍后重试')
    } else if (status === 500) {
      ElMessage.error('服务器内部错误')
    } else {
      ElMessage.error(message)
    }
    return Promise.reject(error)
  }
)

export default request
