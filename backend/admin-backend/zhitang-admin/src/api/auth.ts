import request from './request'
import { API_ENDPOINTS } from './config'

// 认证相关API
export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  token: string
  user: {
    user_id: number
    username: string
    nickname: string
    phone_number?: string
    email?: string
    avatar_url?: string
  }
  message: string
}

export interface RegisterRequest {
  username: string
  password: string
  nickname?: string
  phone_number?: string
  email?: string
}

export interface PhoneLoginRequest {
  phone_number: string
  verification_code: string
}

// 用户登录
export const login = (data: LoginRequest): Promise<LoginResponse> => {
  return request.post(API_ENDPOINTS.AUTH.LOGIN, data)
}

// 用户注册
export const register = (data: RegisterRequest): Promise<LoginResponse> => {
  return request.post(API_ENDPOINTS.AUTH.REGISTER, data)
}

// 手机号登录
export const loginWithPhone = (data: PhoneLoginRequest): Promise<LoginResponse> => {
  return request.post(API_ENDPOINTS.AUTH.LOGIN_PHONE, data)
}

// 刷新token
export const refreshToken = (): Promise<{ token: string }> => {
  return request.post(API_ENDPOINTS.AUTH.REFRESH_TOKEN)
}
