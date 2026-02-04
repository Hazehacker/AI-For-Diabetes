// API配置文件
export const API_CONFIG = {
  // 后端API基础URL
  BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://115.120.251.86:8900',
  
  // 请求超时时间
  TIMEOUT: 30000,
  
  // 请求头配置
  HEADERS: {
    'Content-Type': 'application/json',
  }
}

// API端点配置
export const API_ENDPOINTS = {
  // 认证相关
  AUTH: {
    LOGIN: '/api/login',
    REGISTER: '/api/register',
    LOGIN_PHONE: '/api/login/phone',
    REFRESH_TOKEN: '/api/refresh-token',
  },
  
  // 用户管理
  USER: {
    PROFILE: '/api/user/profile',
    UPDATE_PHONE: '/api/user/phone',
    UPDATE_PASSWORD: '/api/user/password',
    LIST: '/api/admin/users',
  },
  
  // 对话管理
  CHAT: {
    HISTORY: '/api/chat/history',
    STREAM: '/api/chat/stream',
    SEND: '/api/chat/send',
    COZE_HISTORY: '/api/chat/coze/history',
    COZE_SESSIONS: '/api/chat/coze/sessions',
  },
  
  // 健康管理
  HEALTH: {
    CHECKIN: '/api/checkin',
  },
  
  // Coze相关
  COZE: {
    TOKEN: '/api/coze/token',
    AUDIO_STT: '/api/coze/audio/speech-to-text',
    AUDIO_TTS: '/api/coze/audio/text-to-speech',
    AUDIO_RECORDS: '/api/coze/audio/records',
    KNOWLEDGE_UPLOAD: '/api/coze/knowledge/upload',
    KNOWLEDGE_DELETE: '/api/coze/knowledge/delete',
    KNOWLEDGE_LIST: '/api/coze/knowledge/list',
    CHAT_CONVERSATION: '/api/coze/chat/conversation',
    CHAT_COMPLETIONS: '/api/coze/chat/completions',
  },
  
  // 系统
  SYSTEM: {
    HEALTH: '/api/health',
  }
}

// 响应状态码
export const HTTP_STATUS = {
  SUCCESS: 200,
  CREATED: 201,
  BAD_REQUEST: 400,
  UNAUTHORIZED: 401,
  FORBIDDEN: 403,
  NOT_FOUND: 404,
  INTERNAL_SERVER_ERROR: 500,
}

// 错误消息
export const ERROR_MESSAGES = {
  NETWORK_ERROR: '网络连接失败，请检查网络设置',
  TIMEOUT_ERROR: '请求超时，请稍后重试',
  UNAUTHORIZED: '登录已过期，请重新登录',
  FORBIDDEN: '没有权限访问此资源',
  NOT_FOUND: '请求的资源不存在',
  SERVER_ERROR: '服务器内部错误，请稍后重试',
  UNKNOWN_ERROR: '未知错误，请稍后重试',
}
