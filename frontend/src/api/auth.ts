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

// 修改密码
export function changePassword(data: { old_password: string; new_password: string }): Promise<ApiResponse<null>> {
  return request.put('/users/me/password', data).then(res => res.data)
}

// 上传头像
export function uploadAvatar(file: File): Promise<ApiResponse<{ avatar_url: string }>> {
  const form = new FormData()
  form.append('file', file)
  return request
    .post('/users/me/avatar', form, { headers: { 'Content-Type': 'multipart/form-data' } })
    .then(res => res.data)
}

// 删除头像 → 恢复默认字母头像
export function deleteAvatar(): Promise<ApiResponse<null>> {
  return request.delete('/users/me/avatar').then(res => res.data)
}
