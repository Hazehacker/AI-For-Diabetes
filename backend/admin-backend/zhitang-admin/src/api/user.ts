import request from './request'
import { API_ENDPOINTS } from './config'

// 用户相关API
export interface User {
  user_id: number
  username: string
  nickname: string
  phone_number?: string
  email?: string
  avatar_url?: string
  gender?: string
  date_of_birth?: string
  registration_date: string
  last_login_date?: string
  is_active: boolean
}

export interface UserProfile {
  user_id: number
  username: string
  nickname: string
  phone_number?: string
  email?: string
  avatar_url?: string
  gender?: string
  date_of_birth?: string
  registration_date: string
  last_login_date?: string
}

export interface UpdatePhoneRequest {
  phone_number: string
  verification_code: string
}

export interface UpdatePasswordRequest {
  old_password: string
  new_password: string
}

export interface UserListResponse {
  users: User[]
  total: number
  page: number
  page_size: number
}

// 获取用户列表（管理员）
export const getUserList = (params?: {
  page?: number
  page_size?: number
  search?: string
}): Promise<UserListResponse> => {
  return request.get(API_ENDPOINTS.USER.LIST, { params })
}

// 获取用户详情
export const getUserProfile = (userId?: number): Promise<UserProfile> => {
  const url = userId ? `${API_ENDPOINTS.USER.PROFILE}?user_id=${userId}` : API_ENDPOINTS.USER.PROFILE
  return request.get(url)
}

// 更新手机号
export const updatePhone = (data: UpdatePhoneRequest): Promise<{ message: string }> => {
  return request.put(API_ENDPOINTS.USER.UPDATE_PHONE, data)
}

// 更新密码
export const updatePassword = (data: UpdatePasswordRequest): Promise<{ message: string }> => {
  return request.put(API_ENDPOINTS.USER.UPDATE_PASSWORD, data)
}
