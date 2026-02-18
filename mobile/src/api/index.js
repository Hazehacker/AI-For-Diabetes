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

// 积分 / 每日签到相关接口
export const pointsApi = {
  /**
   * 获取签到+积分仪表盘
   * 返回当日签到状态、连续天数、月历、积分余额等
   */
  getCheckinDashboard() {
    return request({
      url: '/points/checkin/dashboard',
      method: 'GET'
    })
  },

  /**
   * 每日签到
   */
  submitCheckin() {
    return request({
      url: '/points/checkin',
      method: 'POST'
    })
  },

  /**
   * 获取积分余额
   */
  getBalance() {
    return request({
      url: '/points/balance',
      method: 'GET'
    })
  },

  /**
   * 获取积分记录
   */
  getRecords(params) {
    return request({
      url: '/points/records',
      method: 'GET',
      data: params
    })
  },

  /**
   * 积分商城商品列表
   */
  getRewards(params) {
    return request({
      url: '/points/rewards',
      method: 'GET',
      data: params
    })
  },

  /**
   * 积分兑换
   */
  redeemReward(data) {
    return request({
      url: '/points/redeem',
      method: 'POST',
      data
    })
  }
}

// 小游戏相关接口
export const gamesApi = {
  /**
   * 获取小游戏列表
   * GET /games
   */
  getGames(params) {
    return request({
      url: '/games',
      method: 'GET',
      data: params
    })
  },

  /**
   * 获取游戏配置
   * GET /games/{game_id}/config
   */
  getGameConfig(gameId, params) {
    return request({
      url: `/games/${gameId}/config`,
      method: 'GET',
      data: params
    })
  },

  /**
   * 上报成绩
   * POST /games/{game_id}/result
   */
  submitGameResult(gameId, data) {
    return request({
      url: `/games/${gameId}/result`,
      method: 'POST',
      data
    })
  },

  /**
   * 个人历史
   * GET /games/{game_id}/history
   */
  getGameHistory(gameId, params) {
    return request({
      url: `/games/${gameId}/history`,
      method: 'GET',
      data: params
    })
  },

  /**
   * 排行榜
   * GET /games/{game_id}/leaderboard
   */
  getLeaderboard(gameId, params) {
    return request({
      url: `/games/${gameId}/leaderboard`,
      method: 'GET',
      data: params
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
  },

  /**
   * OCR图片识别食物
   * POST /calories/ocr/recognize
   * data: { image: base64或file }
   */
  recognizeFoodImage(data) {
    return request({
      url: '/calories/ocr/recognize',
      method: 'POST',
      data,
      header: {
        'Content-Type': 'multipart/form-data'
      }
    })
  },

  /**
   * 条码扫描识别食物
   * POST /calories/barcode/scan
   * data: { barcode: string }
   */
  scanBarcode(data) {
    return request({
      url: '/calories/barcode/scan',
      method: 'POST',
      data
    })
  },

  /**
   * 搜索食物库
   * GET /calories/foods/search?keyword=xxx
   */
  searchFoods(params) {
    return request({
      url: '/calories/foods/search',
      method: 'GET',
      data: params
    })
  },

  /**
   * 获取食谱详情
   * GET /calories/recipes/{id}
   */
  getRecipeDetail(id, params) {
    return request({
      url: `/calories/recipes/${id}`,
      method: 'GET',
      data: params
    })
  },

  /**
   * 收藏/取消收藏食谱
   * POST /calories/recipes/{id}/favorite
   */
  toggleRecipeFavorite(id, data) {
    return request({
      url: `/calories/recipes/${id}/favorite`,
      method: 'POST',
      data
    })
  },

  /**
   * 发送食谱给家属
   * POST /calories/recipes/{id}/share
   */
  shareRecipeToFamily(id, data) {
    return request({
      url: `/calories/recipes/${id}/share`,
      method: 'POST',
      data
    })
  },

  /**
   * 获取饮食-血糖关联分析数据
   * GET /calories/analysis/linkage?date=YYYY-MM-DD
   */
  getLinkageAnalysis(params) {
    return request({
      url: '/calories/analysis/linkage',
      method: 'GET',
      data: params
    })
  }
}

// 科普知识相关接口
export const knowledgeApi = {
  /**
   * 获取科普文章列表
   * GET /knowledge/articles
   */
  getArticles(params) {
    return request({
      url: '/knowledge/articles',
      method: 'GET',
      data: params
    })
  },

  /**
   * 获取科普文章详情
   * GET /knowledge/articles/{id}
   */
  getArticleDetail(id, params) {
    return request({
      url: `/knowledge/articles/${id}`,
      method: 'GET',
      data: params
    })
  },

  /**
   * 标记文章已阅读并领取奖励
   * POST /knowledge/articles/{id}/complete
   */
  completeArticle(id, data) {
    return request({
      url: `/knowledge/articles/${id}/complete`,
      method: 'POST',
      data
    })
  },

  /**
   * 获取科普学习概览统计（可选）
   * GET /knowledge/summary
   */
  getSummary(params) {
    return request({
      url: '/knowledge/summary',
      method: 'GET',
      data: params
    })
  }
}

// 视频学习相关接口
export const videoApi = {
  /**
   * 获取视频课程列表
   * GET /video/lessons
   */
  getVideos(params) {
    return request({
      url: '/video/lessons',
      method: 'GET',
      data: params
    })
  },

  /**
   * 获取单个视频详情
   * GET /video/lessons/{id}
   */
  getVideoDetail(id, params) {
    return request({
      url: `/video/lessons/${id}`,
      method: 'GET',
      data: params
    })
  },

  /**
   * 标记视频完成并领取奖励
   * POST /video/lessons/{id}/complete
   */
  completeVideo(id, data) {
    return request({
      url: `/video/lessons/${id}/complete`,
      method: 'POST',
      data
    })
  },

  /**
   * 获取视频学习概览统计（可选）
   * GET /video/summary
   */
  getSummary(params) {
    return request({
      url: '/video/summary',
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
