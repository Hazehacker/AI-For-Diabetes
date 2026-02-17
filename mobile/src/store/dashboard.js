/**
 * 仪表盘状态管理
 */
import { defineStore } from 'pinia'

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    // 当前血糖数据
    currentGlucose: {
      value: null,
      timestamp: null,
      trend: 'stable', // up, down, stable
      trendRate: 'normal', // fast, normal, slow
      status: 'normal' // normal, warning, alert, emergency, data_loss
    },
    
    // 目标区间配置
    targetRange: {
      min: 3.9,
      max: 10.0,
      warningLow: 4.4,
      warningHigh: 9.0
    },
    
    // 历史数据（用于曲线图）
    historyData: [],
    
    // 统计指标
    stats: {
      tir: null, // 目标范围内时间占比
      gmi: null, // 估算糖化血红蛋白
      cv: null   // 血糖波动性
    },
    
    // 警报状态
    alerts: [],
    
    // 用户角色
    userRole: 'child_under_12', // child_under_12, teen_above_12, guardian
    
    // 数据连接状态
    dataConnection: {
      isConnected: true,
      lastUpdateTime: null,
      sensorBattery: 100,
      sensorDaysLeft: 14
    },
    
    // 事件标记
    events: []
  }),
  
  getters: {
    // 获取当前状态颜色
    statusColor: (state) => {
      const statusMap = {
        normal: '#10B981',
        warning: '#F59E0B',
        alert: '#F59E0B',
        emergency: '#EF4444',
        data_loss: '#9CA3AF'
      }
      return statusMap[state.currentGlucose.status] || '#9CA3AF'
    },
    
    // 获取趋势箭头
    trendArrow: (state) => {
      const { trend, trendRate } = state.currentGlucose
      if (trend === 'up') {
        return trendRate === 'fast' ? '⇈' : '↑'
      } else if (trend === 'down') {
        return trendRate === 'fast' ? '⇊' : '↓'
      }
      return '→'
    },
    
    // 判断是否需要显示完整仪表盘
    showFullDashboard: (state) => {
      return state.userRole !== 'child_under_12'
    },
    
    // 获取当前建议
    currentSuggestion: (state) => {
      const { value, trend, status } = state.currentGlucose
      
      if (status === 'data_loss') {
        return {
          type: 'warning',
          text: '数据连接中断，请检查传感器',
          action: 'reconnect'
        }
      }
      
      if (status === 'emergency') {
        if (value < 3.9) {
          return {
            type: 'emergency',
            text: '血糖过低！建议立即补充 15g 碳水',
            action: 'add_carbs'
          }
        } else {
          return {
            type: 'emergency',
            text: '血糖过高！建议复测并联系医生',
            action: 'retest'
          }
        }
      }
      
      if (status === 'alert' || status === 'warning') {
        if (trend === 'down' && value < 4.4) {
          return {
            type: 'warning',
            text: '血糖下降中，注意监测',
            action: 'monitor'
          }
        }
      }
      
      return {
        type: 'info',
        text: '状态良好，继续保持',
        action: null
      }
    }
  },
  
  actions: {
    // 更新当前血糖值
    updateGlucose(data) {
      this.currentGlucose = {
        ...this.currentGlucose,
        ...data,
        timestamp: data.timestamp || new Date()
      }
      
      // 更新状态
      this.updateStatus()
      
      // 更新数据连接状态
      this.dataConnection.isConnected = true
      this.dataConnection.lastUpdateTime = new Date()
    },
    
    // 更新状态判定
    updateStatus() {
      const { value } = this.currentGlucose
      const { min, max, warningLow, warningHigh } = this.targetRange
      
      if (!value) {
        this.currentGlucose.status = 'data_loss'
        return
      }
      
      // 紧急状态
      if (value < min || value > max) {
        this.currentGlucose.status = 'emergency'
      }
      // 警告状态
      else if (value < warningLow || value > warningHigh) {
        this.currentGlucose.status = 'alert'
      }
      // 正常状态
      else {
        this.currentGlucose.status = 'normal'
      }
    },
    
    // 添加历史数据
    addHistoryData(data) {
      this.historyData.push(data)
      // 保持最近24小时的数据
      const oneDayAgo = new Date().getTime() - 24 * 60 * 60 * 1000
      this.historyData = this.historyData.filter(
        item => new Date(item.timestamp).getTime() > oneDayAgo
      )
    },
    
    // 设置用户角色
    setUserRole(role) {
      this.userRole = role
    },
    
    // 添加警报
    addAlert(alert) {
      this.alerts.unshift({
        ...alert,
        id: Date.now(),
        timestamp: new Date(),
        status: 'unhandled'
      })
    },
    
    // 标记警报已处理
    markAlertHandled(alertId) {
      const alert = this.alerts.find(a => a.id === alertId)
      if (alert) {
        alert.status = 'handled'
      }
    },
    
    // 添加事件标记
    addEvent(event) {
      this.events.push({
        ...event,
        id: Date.now(),
        timestamp: event.timestamp || new Date()
      })
    },
    
    // 检查数据连接
    checkDataConnection() {
      const now = new Date().getTime()
      const lastUpdate = this.dataConnection.lastUpdateTime
      
      if (lastUpdate) {
        const timeDiff = now - new Date(lastUpdate).getTime()
        // 超过15分钟未更新
        if (timeDiff > 15 * 60 * 1000) {
          this.dataConnection.isConnected = false
          this.currentGlucose.status = 'data_loss'
        }
      }
    },
    
    // 生成模拟数据（用于演示）
    generateMockData() {
      const now = new Date()
      const historyData = []
      
      // 生成今天的24小时血糖数据
      for (let i = 0; i < 24; i++) {
        const timestamp = new Date(now.getFullYear(), now.getMonth(), now.getDate(), i, 0, 0)
        
        // 模拟血糖波动：早餐后、午餐后、晚餐后会升高
        let baseValue = 5.5
        const hour = i
        
        // 早餐后 (7-10点)
        if (hour >= 7 && hour <= 10) {
          baseValue = 7.0 + Math.random() * 2
        }
        // 午餐后 (12-15点)
        else if (hour >= 12 && hour <= 15) {
          baseValue = 7.5 + Math.random() * 2.5
        }
        // 晚餐后 (18-21点)
        else if (hour >= 18 && hour <= 21) {
          baseValue = 7.2 + Math.random() * 2
        }
        // 夜间 (0-6点)
        else if (hour >= 0 && hour <= 6) {
          baseValue = 5.0 + Math.random() * 1.5
        }
        // 其他时间
        else {
          baseValue = 5.5 + Math.random() * 1.5
        }
        
        historyData.push({
          value: parseFloat(baseValue.toFixed(1)),
          timestamp: timestamp.toISOString(),
          type: 'cgm' // 持续血糖监测
        })
      }
      
      this.historyData = historyData
      
      // 设置当前血糖值为最新的数据
      const currentHour = now.getHours()
      const latestData = historyData.find(d => new Date(d.timestamp).getHours() === currentHour)
      
      if (latestData) {
        this.updateGlucose({
          value: latestData.value,
          timestamp: now,
          trend: this.calculateTrend(historyData, currentHour),
          trendRate: 'normal'
        })
      }
      
      // 计算统计数据
      this.calculateStats()
    },
    
    // 计算趋势
    calculateTrend(data, currentHour) {
      const current = data.find(d => new Date(d.timestamp).getHours() === currentHour)
      const previous = data.find(d => new Date(d.timestamp).getHours() === currentHour - 1)
      
      if (!current || !previous) return 'stable'
      
      const diff = current.value - previous.value
      if (diff > 0.5) return 'up'
      if (diff < -0.5) return 'down'
      return 'stable'
    },
    
    // 计算统计数据
    calculateStats() {
      if (this.historyData.length === 0) {
        this.stats = {
          avgGlucose: '-',
          timeInRange: 0,
          measureCount: 0
        }
        return
      }
      
      const values = this.historyData.map(d => d.value)
      const sum = values.reduce((a, b) => a + b, 0)
      const avg = sum / values.length
      
      // 计算在目标范围内的时间占比
      const inRange = values.filter(v => v >= this.targetRange.min && v <= this.targetRange.max)
      const tir = Math.round((inRange.length / values.length) * 100)
      
      this.stats = {
        avgGlucose: avg.toFixed(1),
        timeInRange: tir,
        measureCount: values.length
      }
    }
  }
})
