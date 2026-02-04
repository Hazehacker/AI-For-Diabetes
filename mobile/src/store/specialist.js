/**
 * AI专科对话状态管理
 */
import { defineStore } from 'pinia'

export const useSpecialistStore = defineStore('specialist', {
  state: () => ({
    // 专科场景列表
    scenes: [
      {
        id: 'report',
        name: '报告解读室',
        nameEn: 'The Report Lab',
        icon: '📊',
        color: '#3B82F6',
        description: '上传检查报告，AI为您深度解读',
        keywords: ['HbA1c', '血糖', '化验单', '检查报告']
      },
      {
        id: 'drug',
        name: '药品小药箱',
        nameEn: 'Smart Medicine Box',
        icon: '💊',
        color: '#10B981',
        description: '扫描药盒，智能管理用药',
        keywords: ['胰岛素', '药品', '用药', '说明书']
      },
      {
        id: 'diary',
        name: '健康日志',
        nameEn: 'Voice Diary',
        icon: '📝',
        color: '#F59E0B',
        description: '记录日常健康状态',
        keywords: ['头晕', '不适', '症状', '感觉']
      },
      {
        id: 'knowledge',
        name: '知识问答',
        nameEn: 'Q&A',
        icon: '💡',
        color: '#8B5CF6',
        description: '糖尿病知识科普',
        keywords: ['什么是', '如何', '为什么', '怎么办']
      }
    ],
    
    // 当前场景
    currentScene: null,
    
    // 对话历史
    conversations: {},
    
    // 上传的文件
    uploadedFiles: [],
    
    // 风险等级
    riskLevels: {
      0: { name: '正常', color: '#10B981', icon: '✓' },
      1: { name: '趋势风险', color: '#F59E0B', icon: '⚠' },
      2: { name: '危急值', color: '#EF4444', icon: '⚡' }
    },
    
    // 当前风险等级
    currentRiskLevel: 0,
    
    // 紧急状态
    emergencyMode: false
  }),
  
  getters: {
    /**
     * 获取当前场景信息
     */
    currentSceneInfo: (state) => {
      return state.scenes.find(s => s.id === state.currentScene)
    },
    
    /**
     * 获取当前场景的对话历史
     */
    currentConversation: (state) => {
      return state.conversations[state.currentScene] || []
    },
    
    /**
     * 获取当前风险等级信息
     */
    currentRiskInfo: (state) => {
      return state.riskLevels[state.currentRiskLevel]
    },
    
    /**
     * 是否处于危险状态
     */
    isDangerous: (state) => {
      return state.currentRiskLevel === 2 || state.emergencyMode
    }
  },
  
  actions: {
    /**
     * 进入专科场景
     */
    enterScene(sceneId) {
      this.currentScene = sceneId
      
      // 初始化对话历史
      if (!this.conversations[sceneId]) {
        this.conversations[sceneId] = []
        
        // 添加欢迎消息
        const scene = this.scenes.find(s => s.id === sceneId)
        if (scene) {
          this.addMessage(sceneId, {
            role: 'assistant',
            content: this.getWelcomeMessage(sceneId),
            timestamp: new Date()
          })
        }
      }
    },
    
    /**
     * 获取欢迎消息
     */
    getWelcomeMessage(sceneId) {
      const messages = {
        report: '欢迎来到报告解读室！请上传您的血常规或糖化报告，我将为您分析趋势。',
        drug: '欢迎来到药品小药箱！请拍摄或扫描药盒，我将为您建立用药档案。',
        diary: '欢迎来到健康日志！请告诉我您今天的身体状况或遇到的问题。',
        knowledge: '欢迎来到知识问答！有什么关于糖尿病的问题想要了解吗？'
      }
      return messages[sceneId] || '您好，我是AI助手，有什么可以帮您的？'
    },
    
    /**
     * 添加消息
     */
    addMessage(sceneId, message) {
      if (!this.conversations[sceneId]) {
        this.conversations[sceneId] = []
      }
      
      this.conversations[sceneId].push({
        id: Date.now(),
        ...message
      })
      
      // 检查风险关键词
      if (message.role === 'user') {
        this.checkRiskKeywords(message.content)
      }
    },
    
    /**
     * 检查风险关键词
     */
    checkRiskKeywords(content) {
      const emergencyKeywords = ['酮症', '酸中毒', '昏迷', '抽搐', '呕吐不止', '呼吸困难']
      const warningKeywords = ['头晕', '出汗', '心慌', '手抖', '乏力']
      
      // 检查紧急关键词
      for (const keyword of emergencyKeywords) {
        if (content.includes(keyword)) {
          this.triggerEmergency()
          return
        }
      }
      
      // 检查警告关键词
      for (const keyword of warningKeywords) {
        if (content.includes(keyword)) {
          this.setRiskLevel(1)
          return
        }
      }
      
      // 正常状态
      this.setRiskLevel(0)
    },
    
    /**
     * 设置风险等级
     */
    setRiskLevel(level) {
      this.currentRiskLevel = level
    },
    
    /**
     * 触发紧急模式
     */
    triggerEmergency() {
      this.emergencyMode = true
      this.currentRiskLevel = 2
    },
    
    /**
     * 退出紧急模式
     */
    exitEmergency() {
      this.emergencyMode = false
      this.currentRiskLevel = 0
    },
    
    /**
     * 上传文件
     */
    uploadFile(file) {
      this.uploadedFiles.push({
        id: Date.now(),
        sceneId: this.currentScene,
        ...file,
        uploadedAt: new Date()
      })
    },
    
    /**
     * 清空当前场景对话
     */
    clearCurrentConversation() {
      if (this.currentScene) {
        this.conversations[this.currentScene] = []
      }
    },
    
    /**
     * 退出场景
     */
    exitScene() {
      this.currentScene = null
      this.currentRiskLevel = 0
      this.emergencyMode = false
    }
  }
})
