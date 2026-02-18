/**
 * 聊天状态管理
 */
import { defineStore } from 'pinia'
import { chatApi } from '@/api'
import { generateId } from '@/utils/common'

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [],
    conversationId: uni.getStorageSync('conversationId') || null,
    isTyping: false,
    enableTTS: uni.getStorageSync('enableTTS') || false,

    // 糖糖问答每日题目
    dailyQuestion: null,
    userChoice: null,
    hasAnswered: false,
    lastAnswerDate: null,
    
    // 答题历史记录
    quizHistory: JSON.parse(uni.getStorageSync('quizHistory') || '[]'),

    // 题库
    questionBank: [
      {
        id: 'q001',
        question: '1型糖尿病患者每天至少要测4次血糖',
        correctAnswer: true,
        explanation: '正确！1型糖尿病患者建议每天至少测4次血糖（三餐前+睡前），以便及时调整胰岛素剂量，保持血糖稳定。',
        trueCount: 0,
        falseCount: 0
      },
      {
        id: 'q002',
        question: '运动后血糖一定会降低',
        correctAnswer: false,
        explanation: '错误！虽然运动通常会降低血糖，但剧烈运动或高强度运动可能导致应激反应，使血糖暂时升高。运动后应监测血糖变化。',
        trueCount: 0,
        falseCount: 0
      },
      {
        id: 'q003',
        question: '糖化血红蛋白(HbA1c)反映近3个月的平均血糖水平',
        correctAnswer: true,
        explanation: '正确！糖化血红蛋白能反映过去2-3个月的平均血糖水平，是评估长期血糖控制的重要指标。目标值通常为<7%。',
        trueCount: 0,
        falseCount: 0
      },
      {
        id: 'q004',
        question: '低血糖时应该立即注射胰岛素',
        correctAnswer: false,
        explanation: '错误！低血糖时应该立即补充快速吸收的碳水化合物（如葡萄糖片、果汁），而不是注射胰岛素。胰岛素会进一步降低血糖，非常危险！',
        trueCount: 0,
        falseCount: 0
      },
      {
        id: 'q005',
        question: '糖尿病患者可以适量吃水果',
        correctAnswer: true,
        explanation: '正确！糖尿病患者可以适量吃水果，建议选择低升糖指数的水果（如苹果、梨、柚子），在两餐之间食用，并计入每日碳水化合物总量。',
        trueCount: 0,
        falseCount: 0
      }
    ]
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
    },
    
    // 生成每日题目
    generateDailyQuestion() {
      const today = new Date().toDateString()
      
      // 检查是否已经生成今日题目
      if (this.lastAnswerDate === today && this.dailyQuestion) {
        return
      }
      
      // 重置答题状态
      this.hasAnswered = false
      this.userChoice = null
      
      // 随机选择一道题目
      const randomIndex = Math.floor(Math.random() * this.questionBank.length)
      this.dailyQuestion = { ...this.questionBank[randomIndex] }
    },
    
    // 提交答案
    submitAnswer(choice) {
      if (this.hasAnswered) return
      
      this.userChoice = choice
      this.hasAnswered = true
      this.lastAnswerDate = new Date().toDateString()
      
      // 更新统计数据（模拟）
      if (choice) {
        this.dailyQuestion.trueCount++
      } else {
        this.dailyQuestion.falseCount++
      }
      
      // 保存到答题历史
      const historyRecord = {
        id: Date.now(),
        date: new Date().toISOString().split('T')[0],
        questionId: this.dailyQuestion.id,
        question: this.dailyQuestion.question,
        userAnswer: choice,
        correctAnswer: this.dailyQuestion.correctAnswer,
        isCorrect: choice === this.dailyQuestion.correctAnswer,
        explanation: this.dailyQuestion.explanation
      }
      this.quizHistory.unshift(historyRecord)
      uni.setStorageSync('quizHistory', JSON.stringify(this.quizHistory))
    },
    
    // 获取答题历史
    getQuizHistory() {
      return this.quizHistory
    },
    
    // 获取答题统计
    getAnswerStats() {
      if (!this.dailyQuestion) return null
      
      const total = this.dailyQuestion.trueCount + this.dailyQuestion.falseCount
      if (total === 0) return { truePercent: 50, falsePercent: 50 }
      
      return {
        truePercent: Math.round((this.dailyQuestion.trueCount / total) * 100),
        falsePercent: Math.round((this.dailyQuestion.falseCount / total) * 100)
      }
    }
  }
})
