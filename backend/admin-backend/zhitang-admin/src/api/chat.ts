import request from './request'
import { API_ENDPOINTS } from './config'

// 对话相关API
export interface ChatMessage {
  log_id: number
  user_id: number
  message_content: string
  message_type: 'text' | 'voice'
  sender: 'user' | 'ai'
  timestamp: string
}

export interface ChatHistoryResponse {
  messages: ChatMessage[]
  total: number
  page: number
  page_size: number
}

export interface ChatSession {
  session_id: string
  user_id: number
  title: string
  created_at: string
  updated_at: string
  message_count: number
}

export interface ChatSessionsResponse {
  sessions: ChatSession[]
  total: number
  page: number
  page_size: number
}

export interface SendMessageRequest {
  message: string
  message_type?: 'text' | 'voice'
  session_id?: string
}

export interface SendMessageResponse {
  message: string
  session_id: string
  timestamp: string
}

export interface StreamChatRequest {
  message: string
  session_id?: string
}

// 获取聊天记录
export const getChatHistory = (params?: {
  user_id?: number
  page?: number
  page_size?: number
  start_date?: string
  end_date?: string
}): Promise<ChatHistoryResponse> => {
  return request.get(API_ENDPOINTS.CHAT.HISTORY, { params })
}

// 获取Coze聊天记录
export const getCozeChatHistory = (params?: {
  user_id?: number
  page?: number
  page_size?: number
  start_date?: string
  end_date?: string
}): Promise<ChatHistoryResponse> => {
  return request.get(API_ENDPOINTS.CHAT.COZE_HISTORY, { params })
}

// 获取聊天会话列表
export const getChatSessions = (params?: {
  user_id?: number
  page?: number
  page_size?: number
}): Promise<ChatSessionsResponse> => {
  return request.get(API_ENDPOINTS.CHAT.COZE_SESSIONS, { params })
}

// 发送消息
export const sendMessage = (data: SendMessageRequest): Promise<SendMessageResponse> => {
  return request.post(API_ENDPOINTS.CHAT.SEND, data)
}

// 流式聊天（用于实时对话）
export const streamChat = (data: StreamChatRequest): Promise<ReadableStream> => {
  return request.post(API_ENDPOINTS.CHAT.STREAM, data, {
    responseType: 'stream',
  })
}
