import request from './request'
import { API_ENDPOINTS } from './config'

// Coze相关API
export interface CozeTokenResponse {
  token: string
  expires_in: number
}

export interface AudioRecord {
  record_id: number
  user_id: number
  audio_url: string
  text_content: string
  record_type: 'speech_to_text' | 'text_to_speech'
  duration: number
  created_at: string
}

export interface AudioRecordsResponse {
  records: AudioRecord[]
  total: number
  page: number
  page_size: number
}

export interface KnowledgeItem {
  kb_id: number
  title: string
  content: string
  category: string
  keywords: string[]
  created_at: string
  updated_at: string
}

export interface KnowledgeListResponse {
  items: KnowledgeItem[]
  total: number
  page: number
  page_size: number
}

export interface UploadKnowledgeRequest {
  title: string
  content: string
  category: string
  keywords?: string[]
}

export interface DeleteKnowledgeRequest {
  kb_id: number
}

export interface ConversationRequest {
  message: string
  session_id?: string
  user_id?: number
}

export interface ConversationResponse {
  response: string
  session_id: string
  timestamp: string
}

export interface CompletionsRequest {
  messages: Array<{
    role: 'user' | 'assistant' | 'system'
    content: string
  }>
  session_id?: string
  user_id?: number
}

export interface CompletionsResponse {
  choices: Array<{
    message: {
      role: string
      content: string
    }
    finish_reason: string
  }>
  usage: {
    prompt_tokens: number
    completion_tokens: number
    total_tokens: number
  }
}

// 获取Coze Token
export const getCozeToken = (): Promise<CozeTokenResponse> => {
  return request.get(API_ENDPOINTS.COZE.TOKEN)
}

// 语音转文字
export const speechToText = (audioFile: File): Promise<{ text: string }> => {
  const formData = new FormData()
  formData.append('audio', audioFile)
  
  return request.post(API_ENDPOINTS.COZE.AUDIO_STT, formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

// 文字转语音
export const textToSpeech = (data: { text: string; voice?: string }): Promise<Blob> => {
  return request.post(API_ENDPOINTS.COZE.AUDIO_TTS, data, {
    responseType: 'blob',
  })
}

// 获取音频记录
export const getAudioRecords = (params?: {
  user_id?: number
  record_type?: string
  start_date?: string
  end_date?: string
  page?: number
  page_size?: number
}): Promise<AudioRecordsResponse> => {
  return request.get(API_ENDPOINTS.COZE.AUDIO_RECORDS, { params })
}

// 上传知识库
export const uploadKnowledge = (data: UploadKnowledgeRequest): Promise<{ message: string; kb_id: number }> => {
  return request.post(API_ENDPOINTS.COZE.KNOWLEDGE_UPLOAD, data)
}

// 删除知识库
export const deleteKnowledge = (data: DeleteKnowledgeRequest): Promise<{ message: string }> => {
  return request.post(API_ENDPOINTS.COZE.KNOWLEDGE_DELETE, data)
}

// 获取知识库列表
export const getKnowledgeList = (params?: {
  category?: string
  search?: string
  page?: number
  page_size?: number
}): Promise<KnowledgeListResponse> => {
  return request.get(API_ENDPOINTS.COZE.KNOWLEDGE_LIST, { params })
}

// Coze对话
export const cozeConversation = (data: ConversationRequest): Promise<ConversationResponse> => {
  return request.post(API_ENDPOINTS.COZE.CHAT_CONVERSATION, data)
}

// Coze补全
export const cozeCompletions = (data: CompletionsRequest): Promise<CompletionsResponse> => {
  return request.post(API_ENDPOINTS.COZE.CHAT_COMPLETIONS, data)
}
