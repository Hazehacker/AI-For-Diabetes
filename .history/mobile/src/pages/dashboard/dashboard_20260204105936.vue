<template>
  <view class="dashboard-container" :style="{ backgroundColor: containerBgColor }">
    <!-- 顶部警报横幅 -->
    <view v-if="showAlertBanner" class="alert-banner" :class="alertBannerClass">
      <text class="alert-icon">{{ alertIcon }}</text>
      <text class="alert-text">{{ alertText }}</text>
    </view>

    <!-- 数据中断提示 -->
    <view v-if="!dataConnection.isConnected" class="connection-lost-banner">
      <text class="banner-icon">⚠️</text>
      <text class="banner-text">传感器信号丢失，数据不是实时的</text>
    </view>

    <!-- 当前状态区 -->
    <view class="status-zone" :class="statusZoneClass" @tap="showDetailCard">
      <view v-if="userRole === 'child_under_12'" class="child-mode">
        <!-- 儿童模式：卡通形象 + 能量条 -->
        <view class="character-container">
          <text class="character-emoji">{{ characterEmoji }}</text>
          <text class="character-message">{{ characterMessage }}</text>
        </view>
        
        <view class="energy-bar-container">
          <text class="energy-label">我的能量值</text>
          <view class="energy-bar">
            <view class="energy-fill" :style="{ width: energyPercentage + '%', backgroundColor: statusColor }"></view>
            <view class="energy-indicator" :style="{ left: energyPercentage + '%' }">
              <text class="indicator-emoji">{{ indicatorEmoji }}</text>
            </view>
          </view>
          <view class="energy-range">
            <text class="range-text">低</text>
            <text class="range-text">刚刚好</text>
            <text class="range-text">高</text>
          </view>
        </view>
      </view>

      <view v-else class="normal-mode">
        <!-- 正常模式：数值显示 -->
        <view class="status-header">
          <text class="status-label">当前状态</text>
          <text class="last-update">{{ lastUpdateText }}</text>
        </view>
        
        <view class="glucose-display">
          <text v-if="currentGlucose.value" class="glucose-value">{{ currentGlucose.value }}</text>
          <text v-else class="glucose-value placeholder">--.-</text>
          <text class="glucose-unit">mmol/L</text>
        </view>
        
        <view class="trend-display">
          <text class="trend-arrow">{{ trendArrow }}</text>
          <text class="trend-text">{{ trendText }}</text>
        </view>
      </view>
    </view>

    <!-- 目标区间指示器（仅非儿童模式） -->
    <view v-if="userRole !== 'child_under_12'" class="target-range-indicator">
      <text class="indicator-label">目标区间</text>
      <view class="range-bar">
        <view class="range-background">
          <view class="safe-zone" :style="safeZoneStyle"></view>
        </view>
        <view class="current-position" :style="currentPositionStyle">
          <view class="position-dot" :class="{ pulse: isPulseActive }"></view>
        </view>
      </view>
      <view class="range-labels">
        <text class="range-label">{{ targetRange.min }}</text>
        <text class="range-label">{{ targetRange.max }}</text>
      </view>
    </view>

    <!-- 实时曲线图（仅≥12岁和家属） -->
    <view v-if="showFullDashboard" class="chart-section">
      <view class="chart-header">
        <text class="chart-title">血糖趋势</text>
        <view class="time-tabs">
          <text 
            v-for="tab in timeTabs" 
            :key="tab.value"
            class="time-tab"
            :class="{ active: selectedTimeRange === tab.value }"
            @tap="selectTimeRange(tab.value)"
          >
            {{ tab.label }}
          </text>
        </view>
      </view>
      
      <view class="chart-container">
        <canvas 
          canvas-id="glucoseChart" 
          class="glucose-chart"
          @touchstart="handleChartTouchStart"
          @touchmove="handleChartTouchMove"
          @touchend="handleChartTouchEnd"
        ></canvas>
        
        <!-- 事件标记层 -->
        <view class="event-markers">
          <view 
            v-for="event in visibleEvents" 
            :key="event.id"
            class="event-marker"
            :style="{ left: event.position + '%' }"
            @tap="showEventDetail(event)"
          >
            <text class="event-icon">{{ event.icon }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 每日统计（仅≥12岁和家属） -->
    <view v-if="showFullDashboard" class="stats-section">
      <view class="stat-card">
        <text class="stat-label">TIR</text>
        <text class="stat-value">{{ stats.tir || '--' }}%</text>
      </view>
      <view class="stat-card">
        <text class="stat-label">GMI</text>
        <text class="stat-value">{{ stats.gmi || '--' }}%</text>
      </view>
      <view class="stat-card">
        <text class="stat-label">CV</text>
        <text class="stat-value">{{ stats.cv || '--' }}%</text>
      </view>
    </view>

    <!-- AI 建议区 -->
    <view class="suggestion-section" :class="suggestionClass">
      <view class="suggestion-header">
        <text class="suggestion-icon">{{ suggestionIcon }}</text>
        <text class="suggestion-title">{{ suggestionTitle }}</text>
      </view>
      <text class="suggestion-text">{{ currentSuggestion.text }}</text>
      
      <button 
        v-if="currentSuggestion.action" 
        class="action-button"
        :class="suggestionClass"
        @tap="handleSuggestionAction"
      >
        {{ actionButtonText }}
      </button>
    </view>

    <!-- 底部导航占位 -->
    <view class="bottom-spacer"></view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useDashboardStore } from '@/store/dashboard'
import { storeToRefs } from 'pinia'
import { GlucoseChartHelper, generateMockData } from '@/utils/chartHelper'

const dashboardStore = useDashboardStore()
const { 
  currentGlucose, 
  targetRange, 
  stats, 
  userRole, 
  dataConnection,
  historyData,
  events
} = storeToRefs(dashboardStore)

const { 
  statusColor, 
  trendArrow, 
  showFullDashboard, 
  currentSuggestion 
} = dashboardStore

// 图表实例
let chartHelper = null

// 时间范围选项
const timeTabs = [
  { label: '1小时', value: '1h' },
  { label: '6小时', value: '6h' },
  { label: '24小时', value: '24h' }
]
const selectedTimeRange = ref('6h')

// 定时器
let refreshTimer = null
let connectionCheckTimer = null

// 容器背景色
const containerBgColor = computed(() => {
  if (currentGlucose.value.status === 'emergency') {
    return '#FEE2E2'
  }
  return '#F3F4F6'
})

// 警报横幅
const showAlertBanner = computed(() => {
  return currentGlucose.value.status === 'emergency' || currentGlucose.value.status === 'alert'
})

const alertBannerClass = computed(() => {
  return currentGlucose.value.status === 'emergency' ? 'emergency' : 'warning'
})

const alertIcon = computed(() => {
  return currentGlucose.value.status === 'emergency' ? '🚨' : '⚠️'
})

const alertText = computed(() => {
  if (currentGlucose.value.status === 'emergency') {
    return currentGlucose.value.value < 3.9 ? '紧急低血糖警报' : '紧急高血糖警报'
  }
  return '血糖异常，请注意'
})

// 状态区样式
const statusZoneClass = computed(() => {
  return `status-${currentGlucose.value.status}`
})

// 儿童模式相关
const characterEmoji = computed(() => {
  const status = currentGlucose.value.status
  if (status === 'emergency') return '😰'
  if (status === 'alert') return '😟'
  if (status === 'data_loss') return '😴'
  return '😊'
})

const characterMessage = computed(() => {
  const status = currentGlucose.value.status
  if (status === 'emergency') return '需要帮助！'
  if (status === 'alert') return '要注意哦'
  if (status === 'data_loss') return '信号断了'
  return '你做得很棒！'
})

const energyPercentage = computed(() => {
  if (!currentGlucose.value.value) return 50
  const { min, max } = targetRange.value
  const value = currentGlucose.value.value
  
  // 将血糖值映射到0-100的能量条
  const percentage = ((value - min) / (max - min)) * 100
  return Math.max(0, Math.min(100, percentage))
})

const indicatorEmoji = computed(() => {
  const status = currentGlucose.value.status
  if (status === 'emergency') return '🔴'
  if (status === 'alert') return '🟡'
  return '🟢'
})

// 趋势文本
const trendText = computed(() => {
  const { trend, trendRate } = currentGlucose.value
  if (trend === 'up') {
    return trendRate === 'fast' ? '快速上升' : '缓慢上升'
  } else if (trend === 'down') {
    return trendRate === 'fast' ? '快速下降' : '缓慢下降'
  }
  return '平稳'
})

// 最后更新时间
const lastUpdateText = computed(() => {
  if (!dataConnection.value.lastUpdateTime) return ''
  const now = new Date()
  const last = new Date(dataConnection.value.lastUpdateTime)
  const diff = Math.floor((now - last) / 1000 / 60)
  
  if (diff < 1) return '刚刚'
  if (diff < 60) return `${diff}分钟前`
  return `${Math.floor(diff / 60)}小时前`
})

// 目标区间样式
const safeZoneStyle = computed(() => {
  const { min, max } = targetRange.value
  const totalRange = max - min
  return {
    left: '0%',
    width: '100%',
    backgroundColor: 'rgba(16, 185, 129, 0.2)'
  }
})

const currentPositionStyle = computed(() => {
  if (!currentGlucose.value.value) return { left: '50%' }
  
  const { min, max } = targetRange.value
  const value = currentGlucose.value.value
  const percentage = ((value - min) / (max - min)) * 100
  
  return {
    left: Math.max(0, Math.min(100, percentage)) + '%'
  }
})

const isPulseActive = computed(() => {
  return currentGlucose.value.status === 'emergency' || currentGlucose.value.status === 'alert'
})

// 可见事件
const visibleEvents = computed(() => {
  // TODO: 根据选中的时间范围过滤事件
  return events.value.map(event => ({
    ...event,
    position: 50, // 临时位置，实际需要根据时间计算
    icon: getEventIcon(event.type)
  }))
})

// 建议区样式
const suggestionClass = computed(() => {
  return `suggestion-${currentSuggestion.type}`
})

const suggestionIcon = computed(() => {
  const iconMap = {
    emergency: '🚨',
    warning: '⚠️',
    info: '💡'
  }
  return iconMap[currentSuggestion.type] || '💡'
})

const suggestionTitle = computed(() => {
  const titleMap = {
    emergency: '紧急建议',
    warning: '温馨提示',
    info: 'AI 洞察'
  }
  return titleMap[currentSuggestion.type] || 'AI 洞察'
})

const actionButtonText = computed(() => {
  const actionMap = {
    add_carbs: '记录补糖',
    retest: '重新测量',
    monitor: '继续监测',
    reconnect: '重新连接'
  }
  return actionMap[currentSuggestion.action] || '了解详情'
})

// 方法
const showDetailCard = () => {
  // TODO: 显示详细信息卡片
  console.log('显示详细信息')
}

const selectTimeRange = (range) => {
  selectedTimeRange.value = range
  drawChart()
}

const handleChartTouchStart = (e) => {
  // TODO: 处理图表触摸开始
}

const handleChartTouchMove = (e) => {
  // TODO: 处理图表触摸移动
}

const handleChartTouchEnd = (e) => {
  // TODO: 处理图表触摸结束
}

const showEventDetail = (event) => {
  // TODO: 显示事件详情
  console.log('事件详情:', event)
}

const handleSuggestionAction = () => {
  const action = currentSuggestion.action
  
  if (action === 'add_carbs') {
    // TODO: 跳转到记录页面
    uni.showToast({ title: '跳转到记录页面', icon: 'none' })
  } else if (action === 'retest') {
    // TODO: 提示重新测量
    uni.showToast({ title: '请重新测量血糖', icon: 'none' })
  } else if (action === 'reconnect') {
    // TODO: 尝试重新连接
    uni.showToast({ title: '正在重新连接...', icon: 'loading' })
  }
}

const getEventIcon = (type) => {
  const iconMap = {
    meal: '🍽️',
    exercise: '🏃',
    medication: '💊',
    sleep: '😴'
  }
  return iconMap[type] || '📌'
}

// 初始化图表
const initChart = async () => {
  if (!showFullDashboard) return
  
  await nextTick()
  
  try {
    // 获取canvas尺寸
    const query = uni.createSelectorQuery()
    query.select('.glucose-chart').boundingClientRect()
    query.exec((res) => {
      if (res[0]) {
        const { width, height } = res[0]
        chartHelper = new GlucoseChartHelper('glucoseChart', width, height)
        
        chartHelper.init().then(() => {
          drawChart()
        })
      }
    })
  } catch (error) {
    console.error('图表初始化失败:', error)
  }
}

// 绘制图表
const drawChart = () => {
  if (!chartHelper) return
  
  // 获取对应时间范围的数据
  let data = historyData.value
  
  // 如果没有真实数据，使用模拟数据
  if (data.length === 0) {
    const hours = selectedTimeRange.value === '1h' ? 1 : (selectedTimeRange.value === '6h' ? 6 : 24)
    data = generateMockData(hours)
  }
  
  chartHelper.draw(data, {
    targetMin: targetRange.value.min,
    targetMax: targetRange.value.max,
    warningLow: targetRange.value.warningLow,
    warningHigh: targetRange.value.warningHigh
  })
}

// 模拟数据更新
const simulateDataUpdate = () => {
  // 生成模拟血糖值
  const mockValue = 3.9 + Math.random() * 6.1
  const mockTrend = Math.random() > 0.5 ? 'up' : (Math.random() > 0.5 ? 'down' : 'stable')
  const mockTrendRate = Math.random() > 0.7 ? 'fast' : 'normal'
  
  dashboardStore.updateGlucose({
    value: parseFloat(mockValue.toFixed(1)),
    trend: mockTrend,
    trendRate: mockTrendRate
  })
  
  // 添加到历史数据
  dashboardStore.addHistoryData({
    timestamp: new Date(),
    value: parseFloat(mockValue.toFixed(1))
  })
  
  // 更新图表
  if (chartHelper) {
    drawChart()
  }
}

onMounted(() => {
  // 初始化数据
  simulateDataUpdate()
  
  // 初始化图表
  setTimeout(() => {
    initChart()
  }, 500)
  
  // 设置定时刷新（每5秒模拟一次数据更新）
  refreshTimer = setInterval(() => {
    simulateDataUpdate()
  }, 5000)
  
  // 设置连接检查定时器
  connectionCheckTimer = setInterval(() => {
    dashboardStore.checkDataConnection()
  }, 60000)
})

onUnmounted(() => {
  if (refreshTimer) clearInterval(refreshTimer)
  if (connectionCheckTimer) clearInterval(connectionCheckTimer)
})
</script>

<style scoped>
.dashboard-container {
  min-height: 100vh;
  padding: 20rpx;
  transition: background-color 0.3s ease;
}

/* 警报横幅 */
.alert-banner {
  padding: 24rpx;
  border-radius: 16rpx;
  margin-bottom: 20rpx;
  display: flex;
  align-items: center;
  animation: pulse 2s infinite;
}

.alert-banner.emergency {
  background: linear-gradient(135deg, #EF4444 0%, #DC2626 100%);
  color: white;
}

.alert-banner.warning {
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
  color: white;
}

.alert-icon {
  font-size: 48rpx;
  margin-right: 16rpx;
}

.alert-text {
  font-size: 32rpx;
  font-weight: bold;
}

/* 数据中断横幅 */
.connection-lost-banner {
  background: #FEF3C7;
  padding: 20rpx;
  border-radius: 12rpx;
  margin-bottom: 20rpx;
  display: flex;
  align-items: center;
}

.banner-icon {
  font-size: 40rpx;
  margin-right: 12rpx;
}

.banner-text {
  font-size: 28rpx;
  color: #92400E;
}

/* 状态区 */
.status-zone {
  background: white;
  border-radius: 24rpx;
  padding: 40rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
}

.status-zone.status-emergency {
  border: 4rpx solid #EF4444;
  animation: shake 0.5s infinite;
}

.status-zone.status-alert {
  border: 4rpx solid #F59E0B;
}

.status-zone.status-normal {
  border: 4rpx solid #10B981;
}

/* 儿童模式 */
.child-mode {
  text-align: center;
}

.character-container {
  margin-bottom: 40rpx;
}

.character-emoji {
  font-size: 120rpx;
  display: block;
  margin-bottom: 20rpx;
}

.character-message {
  font-size: 36rpx;
  font-weight: bold;
  color: #374151;
}

.energy-bar-container {
  margin-top: 40rpx;
}

.energy-label {
  font-size: 28rpx;
  color: #6B7280;
  display: block;
  margin-bottom: 16rpx;
}

.energy-bar {
  position: relative;
  height: 60rpx;
  background: linear-gradient(to right, #EF4444 0%, #F59E0B 25%, #10B981 50%, #F59E0B 75%, #EF4444 100%);
  border-radius: 30rpx;
  overflow: visible;
}

.energy-fill {
  height: 100%;
  border-radius: 30rpx;
  transition: width 0.5s ease;
}

.energy-indicator {
  position: absolute;
  top: -20rpx;
  transform: translateX(-50%);
  transition: left 0.5s ease;
}

.indicator-emoji {
  font-size: 60rpx;
  filter: drop-shadow(0 4rpx 8rpx rgba(0, 0, 0, 0.2));
}

.energy-range {
  display: flex;
  justify-content: space-between;
  margin-top: 16rpx;
}

.range-text {
  font-size: 24rpx;
  color: #9CA3AF;
}

/* 正常模式 */
.normal-mode {
  text-align: center;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.status-label {
  font-size: 28rpx;
  color: #6B7280;
}

.last-update {
  font-size: 24rpx;
  color: #9CA3AF;
}

.glucose-display {
  display: flex;
  align-items: baseline;
  justify-content: center;
  margin-bottom: 20rpx;
}

.glucose-value {
  font-size: 120rpx;
  font-weight: bold;
  color: #1F2937;
}

.glucose-value.placeholder {
  color: #D1D5DB;
}

.glucose-unit {
  font-size: 32rpx;
  color: #6B7280;
  margin-left: 12rpx;
}

.trend-display {
  display: flex;
  align-items: center;
  justify-content: center;
}

.trend-arrow {
  font-size: 48rpx;
  margin-right: 12rpx;
}

.trend-text {
  font-size: 32rpx;
  color: #6B7280;
}

/* 目标区间指示器 */
.target-range-indicator {
  background: white;
  border-radius: 16rpx;
  padding: 32rpx;
  margin-bottom: 20rpx;
}

.indicator-label {
  font-size: 28rpx;
  color: #6B7280;
  display: block;
  margin-bottom: 16rpx;
}

.range-bar {
  position: relative;
  height: 40rpx;
  margin-bottom: 12rpx;
}

.range-background {
  height: 100%;
  background: #E5E7EB;
  border-radius: 20rpx;
  overflow: hidden;
}

.safe-zone {
  height: 100%;
  transition: all 0.3s ease;
}

.current-position {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  transition: left 0.5s ease;
}

.position-dot {
  width: 32rpx;
  height: 32rpx;
  background: #3B82F6;
  border-radius: 50%;
  border: 4rpx solid white;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.2);
}

.position-dot.pulse {
  animation: pulse 1.5s infinite;
}

.range-labels {
  display: flex;
  justify-content: space-between;
}

.range-label {
  font-size: 24rpx;
  color: #9CA3AF;
}

/* 图表区 */
.chart-section {
  background: white;
  border-radius: 16rpx;
  padding: 32rpx;
  margin-bottom: 20rpx;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.chart-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
}

.time-tabs {
  display: flex;
  gap: 12rpx;
}

.time-tab {
  padding: 8rpx 20rpx;
  font-size: 24rpx;
  color: #6B7280;
  background: #F3F4F6;
  border-radius: 12rpx;
}

.time-tab.active {
  color: white;
  background: #3B82F6;
}

.chart-container {
  position: relative;
  height: 400rpx;
}

.glucose-chart {
  width: 100%;
  height: 100%;
}

.event-markers {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 100%;
  pointer-events: none;
}

.event-marker {
  position: absolute;
  top: 20rpx;
  transform: translateX(-50%);
  pointer-events: all;
}

.event-icon {
  font-size: 40rpx;
}

/* 统计区 */
.stats-section {
  display: flex;
  gap: 16rpx;
  margin-bottom: 20rpx;
}

.stat-card {
  flex: 1;
  background: white;
  border-radius: 16rpx;
  padding: 24rpx;
  text-align: center;
}

.stat-label {
  font-size: 24rpx;
  color: #6B7280;
  display: block;
  margin-bottom: 8rpx;
}

.stat-value {
  font-size: 36rpx;
  font-weight: bold;
  color: #1F2937;
}

/* 建议区 */
.suggestion-section {
  background: white;
  border-radius: 16rpx;
  padding: 32rpx;
  margin-bottom: 20rpx;
}

.suggestion-section.suggestion-emergency {
  background: #FEE2E2;
  border: 2rpx solid #EF4444;
}

.suggestion-section.suggestion-warning {
  background: #FEF3C7;
  border: 2rpx solid #F59E0B;
}

.suggestion-header {
  display: flex;
  align-items: center;
  margin-bottom: 16rpx;
}

.suggestion-icon {
  font-size: 40rpx;
  margin-right: 12rpx;
}

.suggestion-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
}

.suggestion-text {
  font-size: 28rpx;
  color: #4B5563;
  line-height: 1.6;
  margin-bottom: 20rpx;
}

.action-button {
  width: 100%;
  padding: 24rpx;
  border-radius: 12rpx;
  font-size: 28rpx;
  font-weight: bold;
  border: none;
}

.action-button.suggestion-emergency {
  background: #EF4444;
  color: white;
}

.action-button.suggestion-warning {
  background: #F59E0B;
  color: white;
}

.action-button.suggestion-info {
  background: #3B82F6;
  color: white;
}

/* 底部占位 */
.bottom-spacer {
  height: 120rpx;
}

/* 动画 */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

@keyframes shake {
  0%, 100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-10rpx);
  }
  75% {
    transform: translateX(10rpx);
  }
}
</style>
