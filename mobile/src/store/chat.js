/**
 * 聊天状态管理
 */
import { defineStore } from 'pinia'
import { chatApi } from '@/api'
import { generateId } from '@/utils/common'

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
      const id = message?.id ?? generateId()
      this.messages.push({
        id,
        ...message,
        timestamp: new Date().toISOString()
      })
      return id
    },

    // 更新消息内容（用于流式增量）
    setMessageContent(messageId, content) {
      const idx = this.messages.findIndex((m) => m.id === messageId)
      if (idx === -1) return
      this.messages[idx] = {
        ...this.messages[idx],
        content: content ?? ''
      }
    },

    // 追加消息内容（用于流式增量）
    appendMessageContent(messageId, delta) {
      const idx = this.messages.findIndex((m) => m.id === messageId)
      if (idx === -1) return
      const prev = this.messages[idx]?.content ?? ''
      this.messages[idx] = {
        ...this.messages[idx],
        content: prev + (delta ?? '')
      }
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
        // H5端返回结构：{ success, data: { conversation_id } }
        const conversationId = res?.data?.conversation_id ?? res?.conversation_id ?? ''
        if (conversationId) {
          this.setConversationId(conversationId)
          return
        }

        // 没有历史会话时，不要“伪造conversationId”，让后端在首次对话时创建并在流里返回
        this.setConversationId('')
      } catch (error) {
        console.error('获取会话ID失败:', error)
        // 失败时也不伪造，交给首次对话创建
        this.setConversationId('')
      }
    },
    
    // 切换TTS
    toggleTTS() {
      this.enableTTS = !this.enableTTS
      uni.setStorageSync('enableTTS', this.enableTTS)
    }
  }
})
