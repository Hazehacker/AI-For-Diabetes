import request from './request'
import { API_ENDPOINTS } from './config'

// 健康管理相关API
export interface CheckinRecord {
  record_id: number
  user_id: number
  checkin_type: 'blood_glucose' | 'diet' | 'exercise' | 'medication'
  checkin_value: string
  timestamp: string
  is_completed: boolean
}

export interface CheckinRequest {
  checkin_type: 'blood_glucose' | 'diet' | 'exercise' | 'medication'
  checkin_value: string
}

export interface CheckinResponse {
  message: string
  record_id: number
  points_earned: number
}

export interface UserTag {
  tag_id: number
  user_id: number
  tag_name: string
  confidence_score: number
  created_at: string
  updated_at: string
}

export interface UserProfile {
  profile_id: number
  user_id: number
  static_data: Record<string, any>
  dynamic_data_summary: Record<string, any>
  last_updated: string
}

export interface HealthDataResponse {
  checkin_records: CheckinRecord[]
  user_tags: UserTag[]
  user_profile: UserProfile
  total_points: number
  total_checkins: number
}

// 获取健康数据
export const getHealthData = (params?: {
  user_id?: number
  start_date?: string
  end_date?: string
}): Promise<HealthDataResponse> => {
  return request.get('/api/health/data', { params })
}

// 获取打卡记录
export const getCheckinRecords = (params?: {
  user_id?: number
  checkin_type?: string
  start_date?: string
  end_date?: string
  page?: number
  page_size?: number
}): Promise<{
  records: CheckinRecord[]
  total: number
  page: number
  page_size: number
}> => {
  return request.get('/api/health/checkin/records', { params })
}

// 获取用户标签
export const getUserTags = (params?: {
  user_id?: number
}): Promise<{
  tags: UserTag[]
}> => {
  return request.get('/api/health/user/tags', { params })
}

// 获取用户画像
export const getUserProfile = (params?: {
  user_id?: number
}): Promise<{
  profile: UserProfile
}> => {
  return request.get('/api/health/user/profile', { params })
}

// 创建打卡记录（管理员操作）
export const createCheckinRecord = (data: CheckinRequest & { user_id: number }): Promise<CheckinResponse> => {
  return request.post(API_ENDPOINTS.HEALTH.CHECKIN, data)
}
