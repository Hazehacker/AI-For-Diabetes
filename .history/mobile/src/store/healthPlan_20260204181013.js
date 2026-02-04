/**
 * 个性化健康计划工坊状态管理
 * 功能编号：3.1
 */
import { defineStore } from 'pinia'

export const useHealthPlanStore = defineStore('healthPlan', {
  state: () => ({
    // 用户角色
    userRole: 'teen_above_12', // child_under_12, teen_above_12, guardian
    
    // 计划列表
    plans: [],
    
    // 当前编辑的计划
    currentPlan: null,
    
    // 今日任务列表
    todayTasks: [],
    
    // 计划生成向导状态
    wizard: {
      step: 1, // 1: 数据选择, 2: AI生成预览, 3: 微调发布
      selectedData: {
        glucoseTrend: true,
        medicalRecords: [],
        baseProfile: true
      },
      aiDraft: null,
      generating: false
    },
    
    // 任务反馈记录
    taskFeedback: [],
    
    // 提醒设置
    reminderSettings: {
      level1: { sound: false, vibrate: false }, // 静默
      level2: { sound: true, vibrate: true },   // 标准
      level3: { sound: true, vibrate: true, override: true } // 强制
    }
  }),
  
  getters: {
    /**
     * 获取进行中的计划
     */
    activePlans: (state) => {
      return state.plans.filter(p => p.review_status === 1)
    },
    
    /**
     * 获取待审核的计划（仅家属可见）
     */
    pendingPlans: (state) => {
      if (state.userRole !== 'guardian') return []
      return state.plans.filter(p => p.review_status === 0)
    },
    
    /**
     * 获取今日待完成任务
     */
    todayPendingTasks: (state) => {
      const now = new Date()
      return state.todayTasks
        .filter(t => !t.completed && new Date(t.scheduled_time) <= now)
        .sort((a, b) => new Date(a.scheduled_time) - new Date(b.scheduled_time))
    },
    
    /**
     * 获取今日已完成任务
     */
    todayCompletedTasks: (state) => {
      return state.todayTasks.filter(t => t.completed)
    },
    
    /**
     * 今日完成率
     */
    todayCompletionRate: (state) => {
      if (state.todayTasks.length === 0) return 0
      const completed = state.todayTasks.filter(t => t.completed).length
      return Math.round((completed / state.todayTasks.length) * 100)
    },
    
    /**
     * 是否可以创建计划
     */
    canCreatePlan: (state) => {
      return state.userRole === 'teen_above_12' || state.userRole === 'guardian'
    },
    
    /**
     * 是否可以审核计划
     */
    canReviewPlan: (state) => {
      return state.userRole === 'guardian'
    },
    
    /**
     * 获取游戏化视图（儿童模式）
     */
    gamifiedView: (state) => {
      if (state.userRole !== 'child_under_12') return null
      
      const total = state.todayTasks.length
      const completed = state.todayTasks.filter(t => t.completed).length
      const level = Math.floor(completed / 3) + 1
      
      return {
        level,
        progress: completed,
        total,
        badges: state.calculateBadges(completed),
        nextReward: Math.ceil(completed / 3) * 3
      }
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
     * 开始计划生成向导
     */
    startWizard() {
      this.wizard = {
        step: 1,
        selectedData: {
          glucoseTrend: true,
          medicalRecords: [],
          baseProfile: true
        },
        aiDraft: null,
        generating: false
      }
    },
    
    /**
     * 更新向导步骤
     */
    setWizardStep(step) {
      this.wizard.step = step
    },
    
    /**
     * 更新选中的数据
     */
    updateSelectedData(data) {
      this.wizard.selectedData = { ...this.wizard.selectedData, ...data }
    },
    
    /**
     * 生成AI计划草稿
     */
    async generateAIDraft(userGoal) {
      this.wizard.generating = true
      
      try {
        // TODO: 调用后端AI接口
        // const response = await fetch('/api/ai/generate-plan', {
        //   method: 'POST',
        //   body: JSON.stringify({
        //     selectedData: this.wizard.selectedData,
        //     userGoal
        //   })
        // })
        
        // 模拟AI生成
        await new Promise(resolve => setTimeout(resolve, 2000))
        
        const draft = this.mockGeneratePlan(userGoal)
        this.wizard.aiDraft = draft
        this.wizard.step = 2
        
        return draft
      } catch (error) {
        console.error('AI生成失败:', error)
        throw error
      } finally {
        this.wizard.generating = false
      }
    },
    
    /**
     * 模拟生成计划
     */
    mockGeneratePlan(userGoal) {
      const planTypes = {
        '血糖优化': {
          type: 4, // 运动
          title: '午后血糖改善试验',
          tasks: [
            { time: '15:00', content: '监测血糖', reminder: '该测血糖啦！', level: 2 },
            { time: '15:30', content: '快走20分钟', reminder: '该去散步啦，加油！', level: 1 },
            { time: '16:00', content: '补充水分', reminder: '记得喝水哦', level: 1 },
            { time: '17:00', content: '再次监测血糖', reminder: '看看效果如何', level: 2 }
          ]
        },
        '用药管理': {
          type: 1, // 用药
          title: '每日用药核对计划',
          tasks: [
            { time: '07:00', content: '早餐前胰岛素', reminder: '记得打针哦', level: 3 },
            { time: '12:00', content: '午餐前胰岛素', reminder: '该打针了', level: 3 },
            { time: '18:00', content: '晚餐前胰岛素', reminder: '记得打针', level: 3 },
            { time: '22:00', content: '睡前基础胰岛素', reminder: '睡前别忘了', level: 3 }
          ]
        },
        '饮食调整': {
          type: 3, // 饮食
          title: '低GI饮食优化计划',
          tasks: [
            { time: '07:30', content: '早餐：燕麦+鸡蛋', reminder: '健康早餐时间', level: 1 },
            { time: '10:00', content: '加餐：无糖酸奶', reminder: '补充能量', level: 1 },
            { time: '12:30', content: '午餐：糙米+蔬菜', reminder: '午餐时间到', level: 1 },
            { time: '15:30', content: '下午茶：坚果', reminder: '吃点坚果', level: 1 }
          ]
        }
      }
      
      const selected = planTypes[userGoal] || planTypes['血糖优化']
      
      return {
        plan_type: selected.type,
        target_goal: selected.title,
        task_items: selected.tasks.map((task, index) => ({
          id: Date.now() + index,
          time: task.time,
          content: task.content,
          reminder_text: task.reminder,
          reminder_level: task.level,
          difficulty: 1, // 0-太易, 1-适中, 2-太难
          editable: true
        })),
        duration_days: 7,
        created_by: this.userRole
      }
    },
    
    /**
     * 微调计划任务
     */
    updateDraftTask(taskId, updates) {
      if (!this.wizard.aiDraft) return
      
      const task = this.wizard.aiDraft.task_items.find(t => t.id === taskId)
      if (task) {
        Object.assign(task, updates)
      }
    },
    
    /**
     * 删除计划任务
     */
    removeDraftTask(taskId) {
      if (!this.wizard.aiDraft) return
      
      this.wizard.aiDraft.task_items = this.wizard.aiDraft.task_items.filter(
        t => t.id !== taskId
      )
    },
    
    /**
     * 添加自定义任务
     */
    addCustomTask(task) {
      if (!this.wizard.aiDraft) return
      
      this.wizard.aiDraft.task_items.push({
        id: Date.now(),
        time: task.time,
        content: task.content,
        reminder_text: task.reminder_text || task.content,
        reminder_level: task.reminder_level || 1,
        difficulty: 1,
        editable: true
      })
    },
    
    /**
     * 发布计划
     */
    async publishPlan() {
      if (!this.wizard.aiDraft) return
      
      // 冲突检测
      const conflicts = this.detectConflicts(this.wizard.aiDraft.task_items)
      if (conflicts.length > 0) {
        throw new Error(`检测到冲突：${conflicts.join(', ')}`)
      }
      
      const plan = {
        id: Date.now(),
        ...this.wizard.aiDraft,
        review_status: this.userRole === 'guardian' ? 1 : 0, // 家属直接通过，患者需审核
        created_at: new Date(),
        start_date: new Date(),
        end_date: new Date(Date.now() + this.wizard.aiDraft.duration_days * 24 * 60 * 60 * 1000)
      }
      
      this.plans.unshift(plan)
      
      // 如果是今天的计划，生成今日任务
      if (plan.review_status === 1) {
        this.generateTodayTasks(plan)
      }
      
      // 重置向导
      this.wizard = {
        step: 1,
        selectedData: {
          glucoseTrend: true,
          medicalRecords: [],
          baseProfile: true
        },
        aiDraft: null,
        generating: false
      }
      
      return plan
    },
    
    /**
     * 冲突检测
     */
    detectConflicts(tasks) {
      const conflicts = []
      
      // 检查时间冲突
      const times = tasks.map(t => t.time).sort()
      for (let i = 0; i < times.length - 1; i++) {
        if (times[i] === times[i + 1]) {
          conflicts.push(`${times[i]} 存在多个任务`)
        }
      }
      
      // 检查运动与用药冲突（简化逻辑）
      const exerciseTasks = tasks.filter(t => t.content.includes('运动') || t.content.includes('散步') || t.content.includes('快走'))
      const medicationTasks = tasks.filter(t => t.content.includes('胰岛素') || t.content.includes('用药'))
      
      exerciseTasks.forEach(exercise => {
        medicationTasks.forEach(med => {
          const exerciseTime = this.parseTime(exercise.time)
          const medTime = this.parseTime(med.time)
          const diff = Math.abs(exerciseTime - medTime)
          
          if (diff < 30) { // 30分钟内
            conflicts.push(`${exercise.time} 运动任务与用药时间过近`)
          }
        })
      })
      
      return conflicts
    },
    
    /**
     * 解析时间（HH:MM -> 分钟数）
     */
    parseTime(timeStr) {
      const [hours, minutes] = timeStr.split(':').map(Number)
      return hours * 60 + minutes
    },
    
    /**
     * 生成今日任务
     */
    generateTodayTasks(plan) {
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      
      plan.task_items.forEach(task => {
        const [hours, minutes] = task.time.split(':').map(Number)
        const scheduledTime = new Date(today)
        scheduledTime.setHours(hours, minutes, 0, 0)
        
        this.todayTasks.push({
          id: `${plan.id}_${task.id}`,
          plan_id: plan.id,
          task_id: task.id,
          content: task.content,
          scheduled_time: scheduledTime,
          reminder_text: task.reminder_text,
          reminder_level: task.reminder_level,
          completed: false,
          completed_at: null,
          difficulty_feedback: null
        })
      })
      
      // 按时间排序
      this.todayTasks.sort((a, b) => 
        new Date(a.scheduled_time) - new Date(b.scheduled_time)
      )
    },
    
    /**
     * 完成任务
     */
    completeTask(taskId, data = {}) {
      const task = this.todayTasks.find(t => t.id === taskId)
      if (task) {
        task.completed = true
        task.completed_at = new Date()
        
        // 如果有关联数据（如血糖值）
        if (data.glucose_value) {
          task.related_data = { glucose_value: data.glucose_value }
        }
      }
    },
    
    /**
     * 任务反馈（太难了）
     */
    feedbackTaskDifficulty(taskId, difficulty) {
      const task = this.todayTasks.find(t => t.id === taskId)
      if (task) {
        task.difficulty_feedback = difficulty
        
        // 记录反馈用于AI学习
        this.taskFeedback.push({
          task_id: taskId,
          content: task.content,
          difficulty,
          timestamp: new Date()
        })
      }
    },
    
    /**
     * 审核计划（仅家属）
     */
    reviewPlan(planId, approved) {
      if (this.userRole !== 'guardian') return
      
      const plan = this.plans.find(p => p.id === planId)
      if (plan) {
        plan.review_status = approved ? 1 : 2
        
        if (approved) {
          this.generateTodayTasks(plan)
        }
      }
    },
    
    /**
     * 终止计划
     */
    terminatePlan(planId) {
      const plan = this.plans.find(p => p.id === planId)
      if (plan) {
        plan.review_status = 2
        
        // 移除相关的今日任务
        this.todayTasks = this.todayTasks.filter(t => t.plan_id !== planId)
      }
    },
    
    /**
     * 计算勋章（儿童模式）
     */
    calculateBadges(completedCount) {
      const badges = []
      
      if (completedCount >= 3) badges.push({ name: '小试牛刀', icon: '🌟' })
      if (completedCount >= 5) badges.push({ name: '坚持不懈', icon: '⭐' })
      if (completedCount >= 10) badges.push({ name: '健康达人', icon: '🏆' })
      
      return badges
    },
    
    /**
     * 生成模拟数据
     */
    generateMockData() {
      // 生成一个示例计划
      const mockPlan = {
        id: Date.now(),
        plan_type: 4,
        target_goal: '午后血糖改善试验',
        task_items: [
          {
            id: 1,
            time: '15:00',
            content: '监测血糖',
            reminder_text: '该测血糖啦！',
            reminder_level: 2,
            difficulty: 1
          },
          {
            id: 2,
            time: '15:30',
            content: '快走20分钟',
            reminder_text: '该去散步啦，加油！',
            reminder_level: 1,
            difficulty: 1
          }
        ],
        review_status: 1,
        created_at: new Date(),
        start_date: new Date(),
        end_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000),
        created_by: this.userRole
      }
      
      this.plans.push(mockPlan)
      this.generateTodayTasks(mockPlan)
    }
  }
})
