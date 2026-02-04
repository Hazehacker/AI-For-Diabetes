/**
 * 互动板块状态管理
 * 功能：呼吸 & 冥想训练
 */
import { defineStore } from 'pinia'

export const useInteractionStore = defineStore('interaction', {
  state: () => ({
    // 用户角色
    userRole: 'teen_above_12',
    
    // 训练模式
    trainingMode: 'basic', // basic: 基础, advanced: 进阶
    
    // 训练时长（秒）
    trainingDuration: 180, // 默认3分钟
    
    // 训练记录
    sessions: [],
    
    // 当前训练会话
    currentSession: null,
    
    // 烦恼标签库
    stressTags: [
      '担心考试',
      '害怕低血糖',
      '朋友关系',
      '学业压力',
      '家庭矛盾',
      '身体不适',
      '未来担忧',
      '自我怀疑'
    ],
    
    // 心情选项
    moodOptions: [
      { value: 1, label: '很糟糕', emoji: '😢', color: '#EF4444' },
      { value: 2, label: '不太好', emoji: '😟', color: '#F59E0B' },
      { value: 3, label: '一般', emoji: '😐', color: '#9CA3AF' },
      { value: 4, label: '还不错', emoji: '🙂', color: '#10B981' },
      { value: 5, label: '很好', emoji: '😊', color: '#3B82F6' }
    ],
    
    // 奖章系统
    badges: [],
    
    // 总积分
    totalPoints: 0,
    
    // 电子宠物「糖小怪」
    pet: {
      name: '糖小怪',
      stage: 1,
      progress: 0,
      streak_days: 0,
      total_days: 0,
      last_feed_date: null,
      unlocked_forms: ['basic'],
      current_form: 'basic'
    },
    
    // 今日管理行为记录
    todayBehaviors: {
      glucose_check: false,
      meal_record: false,
      exercise: false,
      medication: false
    },
    
    // 宠物形态定义
    petForms: {
      basic: { name: '基础形态', emoji: '🥚', description: '刚刚孵化' },
      growing: { name: '成长期', emoji: '🐣', description: '开始成长' },
      active: { name: '活跃期', emoji: '🐥', description: '充满活力' },
      mature: { name: '成熟期', emoji: '🐤', description: '健康成长' },
      evolved: { name: '进化形态', emoji: '🦜', description: '完全进化' }
    },
    
    // 成长阶段定义
    petStages: [
      { stage: 1, name: '蛋蛋', emoji: '🥚', requiredDays: 0 },
      { stage: 2, name: '小怪', emoji: '🐣', requiredDays: 3 },
      { stage: 3, name: '活力怪', emoji: '🐥', requiredDays: 7 },
      { stage: 4, name: '健康怪', emoji: '🐤', requiredDays: 14 },
      { stage: 5, name: '超级怪', emoji: '🦜', requiredDays: 30 }
    ]
  }),
  
  getters: {
    /**
     * 获取训练历史（按时间倒序）
     */
    sortedSessions: (state) => {
      return [...state.sessions].sort((a, b) => 
        new Date(b.completed_at) - new Date(a.completed_at)
      )
    },
    
    /**
     * 获取本周训练次数
     */
    weeklySessionCount: (state) => {
      const oneWeekAgo = new Date()
      oneWeekAgo.setDate(oneWeekAgo.getDate() - 7)
      
      return state.sessions.filter(s => 
        new Date(s.completed_at) > oneWeekAgo
      ).length
    },
    
    /**
     * 获取平均节律得分
     */
    averageRhythmScore: (state) => {
      if (state.sessions.length === 0) return 0
      
      const sum = state.sessions.reduce((acc, s) => acc + s.rhythm_score, 0)
      return Math.round(sum / state.sessions.length)
    },
    
    /**
     * 获取心情改善趋势
     */
    moodImprovementRate: (state) => {
      const improved = state.sessions.filter(s => 
        s.mood_after > s.mood_before
      ).length
      
      if (state.sessions.length === 0) return 0
      return Math.round((improved / state.sessions.length) * 100)
    },
    
    /**
     * 是否显示简化界面（儿童模式）
     */
    isSimplifiedView: (state) => {
      return state.userRole === 'child_under_12'
    },
    
    /**
     * 获取已解锁的奖章
     */
    unlockedBadges: (state) => {
      return state.badges.filter(b => b.unlocked)
    },
    
    /**
     * 获取当前宠物阶段信息
     */
    currentPetStage: (state) => {
      return state.petStages.find(s => s.stage === state.pet.stage) || state.petStages[0]
    },
    
    /**
     * 获取下一阶段信息
     */
    nextPetStage: (state) => {
      return state.petStages.find(s => s.stage === state.pet.stage + 1)
    },
    
    /**
     * 今日完成度
     */
    todayCompletionRate: (state) => {
      const behaviors = Object.values(state.todayBehaviors)
      const completed = behaviors.filter(b => b).length
      return Math.round((completed / behaviors.length) * 100)
    },
    
    /**
     * 今日是否已完成
     */
    isTodayCompleted: (state) => {
      return Object.values(state.todayBehaviors).every(b => b)
    },
    
    /**
     * 距离下一阶段还需天数
     */
    daysToNextStage: (state, getters) => {
      if (!getters.nextPetStage) return 0
      return Math.max(0, getters.nextPetStage.requiredDays - state.pet.total_days)
    }
  },
  
  actions: {
    /**
     * 设置用户角色
     */
    setUserRole(role) {
      this.userRole = role
    },
    
    /**
     * 设置训练模式
     */
    setTrainingMode(mode) {
      this.trainingMode = mode
    },
    
    /**
     * 设置训练时长
     */
    setTrainingDuration(duration) {
      this.trainingDuration = duration
    },
    
    /**
     * 开始训练会话
     */
    startSession(config) {
      this.currentSession = {
        id: Date.now(),
        mode: config.mode || this.trainingMode,
        duration: config.duration || this.trainingDuration,
        stress_tags: config.stressTags || [],
        mood_before: config.moodBefore,
        started_at: new Date(),
        breath_data: [],
        clouds_cleared: 0
      }
      
      return this.currentSession
    },
    
    /**
     * 记录呼吸数据
     */
    recordBreath(breathData) {
      if (!this.currentSession) return
      
      this.currentSession.breath_data.push({
        timestamp: Date.now(),
        intensity: breathData.intensity,
        duration: breathData.duration,
        phase: breathData.phase // 'inhale' or 'exhale'
      })
    },
    
    /**
     * 清除一朵云
     */
    clearCloud() {
      if (!this.currentSession) return
      
      this.currentSession.clouds_cleared++
    },
    
    /**
     * 完成训练会话
     */
    completeSession(result) {
      if (!this.currentSession) return
      
      // 计算节律得分
      const rhythmScore = this.calculateRhythmScore(this.currentSession.breath_data)
      
      const completedSession = {
        ...this.currentSession,
        completed_at: new Date(),
        mood_after: result.moodAfter,
        rhythm_score: rhythmScore,
        reward_points: this.calculateRewardPoints(rhythmScore, this.currentSession.clouds_cleared),
        session_duration: Math.floor((new Date() - new Date(this.currentSession.started_at)) / 1000)
      }
      
      // 保存会话
      this.sessions.push(completedSession)
      
      // 更新总积分
      this.totalPoints += completedSession.reward_points
      
      // 检查奖章
      this.checkBadges()
      
      // 清除当前会话
      const finalSession = { ...completedSession }
      this.currentSession = null
      
      return finalSession
    },
    
    /**
     * 计算节律得分
     */
    calculateRhythmScore(breathData) {
      if (breathData.length === 0) return 0
      
      // 简化算法：基于呼吸次数和稳定性
      const breathCount = breathData.filter(b => b.phase === 'exhale').length
      const avgIntensity = breathData.reduce((sum, b) => sum + b.intensity, 0) / breathData.length
      
      // 理想呼吸次数：每分钟6-8次
      const idealBreathsPerMinute = 7
      const actualBreathsPerMinute = breathCount / (this.trainingDuration / 60)
      const breathRateScore = Math.max(0, 100 - Math.abs(actualBreathsPerMinute - idealBreathsPerMinute) * 10)
      
      // 强度稳定性（0-100）
      const intensityScore = Math.min(100, avgIntensity * 100)
      
      return Math.round((breathRateScore + intensityScore) / 2)
    },
    
    /**
     * 计算奖励积分
     */
    calculateRewardPoints(rhythmScore, cloudsCleared) {
      const basePoints = 10
      const rhythmBonus = Math.floor(rhythmScore / 10)
      const cloudBonus = cloudsCleared * 2
      
      return basePoints + rhythmBonus + cloudBonus
    },
    
    /**
     * 检查并解锁奖章
     */
    checkBadges() {
      const badgeDefinitions = [
        {
          id: 'first_session',
          name: '初次尝试',
          description: '完成第一次训练',
          icon: '🌟',
          condition: () => this.sessions.length >= 1
        },
        {
          id: 'week_warrior',
          name: '一周勇士',
          description: '一周内完成5次训练',
          icon: '🏆',
          condition: () => this.weeklySessionCount >= 5
        },
        {
          id: 'rhythm_master',
          name: '节奏大师',
          description: '平均节律得分达到80分',
          icon: '🎵',
          condition: () => this.averageRhythmScore >= 80
        },
        {
          id: 'mood_improver',
          name: '心情改善者',
          description: '80%的训练后心情改善',
          icon: '😊',
          condition: () => this.moodImprovementRate >= 80
        },
        {
          id: 'persistent',
          name: '坚持不懈',
          description: '累计完成20次训练',
          icon: '💪',
          condition: () => this.sessions.length >= 20
        }
      ]
      
      badgeDefinitions.forEach(def => {
        const existingBadge = this.badges.find(b => b.id === def.id)
        
        if (!existingBadge && def.condition()) {
          this.badges.push({
            ...def,
            unlocked: true,
            unlocked_at: new Date()
          })
        }
      })
    },
    
    /**
     * 获取家属可见的趋势数据
     */
    getGuardianTrend() {
      return {
        total_sessions: this.sessions.length,
        weekly_sessions: this.weeklySessionCount,
        average_rhythm: this.averageRhythmScore,
        mood_improvement: this.moodImprovementRate,
        last_session: this.sessions.length > 0 ? this.sessions[this.sessions.length - 1].completed_at : null
      }
    },
    
    /**
     * 生成模拟数据
     */
    generateMockData() {
      // 生成5条历史记录
      const now = Date.now()
      
      for (let i = 0; i < 5; i++) {
        const daysAgo = i * 2
        const completedAt = new Date(now - daysAgo * 24 * 60 * 60 * 1000)
        
        this.sessions.push({
          id: now + i,
          mode: i % 2 === 0 ? 'basic' : 'advanced',
          duration: 180,
          stress_tags: ['学业压力', '担心考试'].slice(0, Math.floor(Math.random() * 2) + 1),
          mood_before: Math.floor(Math.random() * 2) + 2, // 2-3
          mood_after: Math.floor(Math.random() * 2) + 4, // 4-5
          started_at: new Date(completedAt.getTime() - 180000),
          completed_at: completedAt,
          breath_data: [],
          clouds_cleared: Math.floor(Math.random() * 5) + 3,
          rhythm_score: Math.floor(Math.random() * 30) + 60, // 60-90
          reward_points: Math.floor(Math.random() * 20) + 20,
          session_duration: 180
        })
      }
      
      this.totalPoints = this.sessions.reduce((sum, s) => sum + s.reward_points, 0)
      this.checkBadges()
      
      // 生成宠物模拟数据
      this.pet.stage = 3
      this.pet.progress = 45
      this.pet.streak_days = 5
      this.pet.total_days = 12
      this.pet.last_feed_date = new Date(Date.now() - 24 * 60 * 60 * 1000).toDateString()
      
      // 模拟部分完成今日行为
      this.todayBehaviors.glucose_check = true
      this.todayBehaviors.meal_record = true
    }
  }
})
