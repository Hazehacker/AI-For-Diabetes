/**
 * API接口统一管理
 */
import request from '@/utils/request'
import { streamSSE } from '@/utils/sse'

// 用户相关接口
export const userApi = {
  // 登录
  login(data) {
    return request({
      url: '/login',
      method: 'POST',
      data
    })
  },
  
  // 获取用户信息
  getUserProfile(userId) {
    return request({
      url: '/user/profile',
      method: 'GET',
      data: { user_id: userId }
    })
  }
}

// 对话相关接口
export const chatApi = {
  // 获取最新会话ID
  getLatestSession(userId) {
    return request({
      url: '/chat/sessions/latest',
      method: 'GET',
      data: { user_id: userId }
    })
  },
  
  // 获取历史对话记录（用于聊天记录展示）
  getHistory(params) {
    return request({
      url: '/chat/history',
      method: 'GET',
      data: params
    })
  },
  
  // 发送消息（流式）
  sendMessage(data) {
    return request({
      url: '/chat/stream_with_tts',
      method: 'POST',
      data
    })
  },

  // 发送消息（流式SSE，移动端/H5对齐）
  streamMessage(data, handlers) {
    return streamSSE({
      path: '/chat/stream_with_tts',
      body: data,
      handlers
    })
  },
  
  // 语音转文字
  speechToText(data) {
    return request({
      url: '/chat/speech_to_text',
      method: 'POST',
      data
    })
  }
}

// TTS相关接口
export const ttsApi = {
  // 文字转语音
  textToSpeech(data) {
    return request({
      url: '/tts/stream',
      method: 'POST',
      data
    })
  }
}

// 热量记录与食谱推荐相关接口
export const caloriesApi = {
  /**
   * 获取某一天的热量统计与饮食记录
   * GET /calories/daily?date=YYYY-MM-DD
   */
  getDailySummary(params) {
    return request({
      url: '/calories/daily',
      method: 'GET',
      data: params
    })
  },

  /**
   * 新增一条饮食记录
   * POST /calories/records
   */
  createRecord(data) {
    return request({
      url: '/calories/records',
      method: 'POST',
      data
    })
  },

  /**
   * 获取推荐食谱列表
   * GET /calories/recipes/recommend
   */
  getRecipeRecommendations(params) {
    return request({
      url: '/calories/recipes/recommend',
      method: 'GET',
      data: params
    })
  }
}

// 打卡相关接口
export const checkinApi = {
  // 提交打卡
  submitCheckin(data) {
    return request({
      url: '/checkin',
      method: 'POST',
      data
    })
  },
  
  // 获取打卡记录
  getCheckinRecords() {
    return request({
      url: '/checkin/records',
      method: 'GET'
    }).then((res) => {
      // 兼容多种返回结构：
      // 1) 旧：{ data: [] }
      // 2) 新：{ code:200, data:{ records:[], stats:{...}, success:true }, success:true }
      const records = Array.isArray(res?.data)
        ? res.data
        : (Array.isArray(res?.data?.records) ? res.data.records : [])

      const normalized = records.map((r) => ({
        ...r,
        // 统一字段名，供页面渲染使用
        id: r.id ?? r.record_id,
        checkin_time: r.checkin_time ?? r.timestamp,
        glucose_status: r.glucose_status ?? '好'
      }))

      return {
        ...res,
        data: normalized,
        stats: res?.data?.stats
      }
    })
  }
}
