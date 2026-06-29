import request from './request'
import type { ApiResponse, LoginRequest, RegisterRequest, UserInfo } from '@/types'

// 登录
export function login(data: LoginRequest): Promise<ApiResponse<{ access_token: string; refresh_token: string; user: UserInfo }>> {
  return request.post('/auth/login', data).then(res => res.data)
}

// 注册
export function register(data: RegisterRequest): Promise<ApiResponse<UserInfo>> {
  return request.post('/auth/register', data).then(res => res.data)
}

// 获取当前用户信息
export function getCurrentUser(): Promise<ApiResponse<UserInfo>> {
  return request.get('/users/me').then(res => res.data)
}

// 刷新Token
export function refreshToken(token: string): Promise<ApiResponse<{ access_token: string; refresh_token: string }>> {
  return request.post('/auth/refresh', { refresh_token: token }).then(res => res.data)
}

// 退出登录
export function logout(): Promise<ApiResponse<null>> {
  return request.post('/auth/logout').then(res => res.data)
}
