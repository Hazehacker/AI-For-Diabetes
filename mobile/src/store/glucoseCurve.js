/**
 * 血糖曲线状态管理
 * 功能编号：监测-1.3
 */
import { defineStore } from 'pinia'
import { useDashboardStore } from './dashboard'

export const useGlucoseCurveStore = defineStore('glucoseCurve', {
  state: () => ({
    // 血糖记录数据
    glucoseRecords: [],
    
    // 当前视图类型
    viewType: 'day', // day, week, month
    
    // 选中的日期
    selectedDate: new Date(),
    
    // 参考范围
    referenceRange: {
      min: 3.9,
      max: 6.1
    },
    
    // 用户角色
    userRole: 'teen_above_12', // child_under_12, teen_above_12, guardian
    
    // 数据加载状态
    loading: false,
    
    // 统计数据
    statistics: {
      avgGlucose: null,
      maxGlucose: null,
      minGlucose: null,
      outOfRangeCount: 0,
      totalCount: 0,
      timeInRange: null // TIR 百分比
    }
  }),
  
  getters: {
    /**
     * 获取当前视图的血糖数据
     */
    currentViewData: (state) => {
      const now = state.selectedDate
      let startTime, endTime
      
      switch (state.viewType) {
        case 'day':
          // 当天 00:00 到 23:59
          startTime = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 0, 0, 0)
          endTime = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59)
          break
          
        case 'week':
          // 最近7天
          startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
          startTime.setHours(0, 0, 0, 0)
          endTime = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59)
          break
          
        case 'month':
          // 最近30天
          startTime = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000)
          startTime.setHours(0, 0, 0, 0)
          endTime = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59)
          break
          
        default:
          return []
      }
      
      return state.glucoseRecords.filter(record => {
        const recordTime = new Date(record.measure_time)
        return recordTime >= startTime && recordTime <= endTime
      }).sort((a, b) => new Date(a.measure_time) - new Date(b.measure_time))
    },
    
    /**
     * 判断数据点是否超出范围
     */
    isOutOfRange: (state) => (value) => {
      return value < state.referenceRange.min || value > state.referenceRange.max
    },
    
    /**
     * 获取数据点的状态颜色
     */
    getPointColor: (state) => (value) => {
      if (value < state.referenceRange.min) {
        return '#EF4444' // 低血糖 - 红色
      } else if (value > state.referenceRange.max) {
        return '#F59E0B' // 高血糖 - 橙色
      } else {
        return '#10B981' // 正常 - 绿色
      }
    },
    
    /**
     * 是否可以编辑数据（角色权限）
     */
    canEditData: (state) => {
      return state.userRole === 'teen_above_12' || state.userRole === 'guardian'
    },
    
    /**
     * 是否显示详细数值（儿童模式简化）
     */
    showDetailedValues: (state) => {
      return state.userRole !== 'child_under_12'
    },
    
    /**
     * 聚合后的曲线数据（用于周/月视图）
     */
    aggregatedData: (state) => {
      const data = state.currentViewData
      
      if (state.viewType === 'day') {
        return data
      }
      
      // 按日期分组聚合
      const grouped = {}
      data.forEach(record => {
        const date = new Date(record.measure_time).toLocaleDateString()
        if (!grouped[date]) {
          grouped[date] = []
        }
        grouped[date].push(record.glucose_value)
      })
      
      // 计算每天的平均值
      return Object.keys(grouped).map(date => ({
        measure_time: new Date(date),
        glucose_value: grouped[date].reduce((a, b) => a + b, 0) / grouped[date].length,
        is_aggregated: true,
        count: grouped[date].length
      })).sort((a, b) => a.measure_time - b.measure_time)
    }
  },
  
  actions: {
    /**
     * 添加血糖记录
     */
    addGlucoseRecord(record) {
      const newRecord = {
        id: Date.now(),
        glucose_value: record.glucose_value,
        measure_time: record.measure_time || new Date(),
        period_type: this.viewType,
        is_out_of_range: this.isOutOfRange(record.glucose_value),
        source: record.source || 'manual', // manual, device
        note: record.note || ''
      }
      
      this.glucoseRecords.unshift(newRecord)
      this.updateStatistics()
      
      return newRecord
    },
    
    /**
     * 批量添加血糖记录
     */
    addBatchRecords(records) {
      records.forEach(record => {
        this.addGlucoseRecord(record)
      })
    },
    
    /**
     * 删除血糖记录
     */
    deleteGlucoseRecord(recordId) {
      const index = this.glucoseRecords.findIndex(r => r.id === recordId)
      if (index !== -1) {
        this.glucoseRecords.splice(index, 1)
        this.updateStatistics()
      }
    },
    
    /**
     * 更新血糖记录
     */
    updateGlucoseRecord(recordId, updates) {
      const record = this.glucoseRecords.find(r => r.id === recordId)
      if (record) {
        Object.assign(record, updates)
        record.is_out_of_range = this.isOutOfRange(record.glucose_value)
        this.updateStatistics()
      }
    },
    
    /**
     * 切换视图类型
     */
    setViewType(type) {
      this.viewType = type
      this.updateStatistics()
    },
    
    /**
     * 设置选中日期
     */
    setSelectedDate(date) {
      this.selectedDate = new Date(date)
      this.updateStatistics()
    },
    
    /**
     * 设置用户角色
     */
    setUserRole(role) {
      this.userRole = role
    },
    
    /**
     * 更新统计数据
     */
    updateStatistics() {
      const data = this.currentViewData
      
      if (data.length === 0) {
        this.statistics = {
          avgGlucose: null,
          maxGlucose: null,
          minGlucose: null,
          outOfRangeCount: 0,
          totalCount: 0,
          timeInRange: null
        }
        return
      }
      
      const values = data.map(r => r.glucose_value)
      const sum = values.reduce((a, b) => a + b, 0)
      const avg = sum / values.length
      const max = Math.max(...values)
      const min = Math.min(...values)
      
      const outOfRangeCount = data.filter(r => r.is_out_of_range).length
      const inRangeCount = data.length - outOfRangeCount
      const timeInRange = (inRangeCount / data.length) * 100
      
      this.statistics = {
        avgGlucose: parseFloat(avg.toFixed(1)),
        maxGlucose: parseFloat(max.toFixed(1)),
        minGlucose: parseFloat(min.toFixed(1)),
        outOfRangeCount,
        totalCount: data.length,
        timeInRange: parseFloat(timeInRange.toFixed(1))
      }
    },
    
    /**
     * 从后端加载数据
     */
    async loadGlucoseData(startDate, endDate) {
      this.loading = true
      
      try {
        // TODO: 调用后端 API
        // const response = await fetch(`/api/glucose/records?start=${startDate}&end=${endDate}`)
        // const data = await response.json()
        // this.glucoseRecords = data.records
        
        // 暂时使用模拟数据
        console.log('加载血糖数据:', startDate, endDate)
        
        this.updateStatistics()
      } catch (error) {
        console.error('加载血糖数据失败:', error)
      } finally {
        this.loading = false
      }
    },
    
    /**
     * 生成模拟数据（用于测试）
     */
    generateMockData(days = 7) {
      const now = new Date()
      const records = []
      
      for (let d = 0; d < days; d++) {
        // 每天生成 4-8 个数据点
        const pointsPerDay = 4 + Math.floor(Math.random() * 5)
        
        for (let p = 0; p < pointsPerDay; p++) {
          const hour = Math.floor(Math.random() * 24)
          const minute = Math.floor(Math.random() * 60)
          const date = new Date(now.getTime() - d * 24 * 60 * 60 * 1000)
          date.setHours(hour, minute, 0, 0)
          
          // 生成血糖值（3.0 - 10.0 范围）
          const baseValue = 5.5
          const variation = (Math.random() - 0.5) * 4
          const value = Math.max(3.0, Math.min(10.0, baseValue + variation))
          
          records.push({
            glucose_value: parseFloat(value.toFixed(1)),
            measure_time: date,
            source: 'mock'
          })
        }
      }
      
      this.addBatchRecords(records)
    },
    
    /**
     * 从dashboard store同步数据
     */
    syncFromDashboard() {
      const dashboardStore = useDashboardStore()
      
      if (dashboardStore.historyData && dashboardStore.historyData.length > 0) {
        // 转换dashboard数据格式为glucoseCurve格式
        const records = dashboardStore.historyData.map(item => ({
          glucose_value: item.value,
          measure_time: new Date(item.timestamp),
          source: item.type || 'cgm',
          is_out_of_range: item.value < this.referenceRange.min || item.value > this.referenceRange.max
        }))
        
        this.glucoseRecords = records
        this.updateStatistics()
      }
    }
  }
})
