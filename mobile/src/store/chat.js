/**
 * 聊天状态管理
 */
import { defineStore } from 'pinia'
import { chatApi } from '@/api'

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [],
    conversationId: uni.getStorageSync('conversationId') || '',
    isTyping: false,
    enableTTS: uni.getStorageSync('enableTTS') || false
  }),
  
  actions: {
    // 添加消息
    addMessage(message) {
      this.messages.push({
        id: Date.now(),
        ...message,
        timestamp: new Date().toISOString()
      })
    },
    
    // 清空消息
    clearMessages() {
      this.messages = []
    },
    
    // 设置会话ID
    setConversationId(id) {
      this.conversationId = id
      uni.setStorageSync('conversationId', id)
    },
    
    // 获取最新会话ID
    async fetchLatestSession(userId) {
      try {
        const res = await chatApi.getLatestSession(userId)
        if (res.data && res.data.conversation_id) {
          this.setConversationId(res.data.conversation_id)
        } else {
          // 创建新会话ID
          const newId = `chat_${userId}_${Date.now()}`
          this.setConversationId(newId)
        }
      } catch (error) {
        console.error('获取会话ID失败:', error)
        // 创建新会话ID
        const newId = `chat_${userId}_${Date.now()}`
        this.setConversationId(newId)
      }
    },
    
    // 切换TTS
    toggleTTS() {
      this.enableTTS = !this.enableTTS
      uni.setStorageSync('enableTTS', this.enableTTS)
    }
  }
})
