<template>
  <view class="glucose-curve-chart">
    <!-- 图表头部 -->
    <view class="chart-header">
      <view class="header-left">
        <text class="chart-title">血糖曲线</text>
        <text v-if="showDetailedValues" class="chart-subtitle">{{ viewTypeText }}</text>
      </view>
      
      <view class="header-right">
        <view class="view-tabs">
          <text 
            v-for="tab in viewTabs" 
            :key="tab.value"
            class="view-tab"
            :class="{ active: viewType === tab.value }"
            @tap="switchView(tab.value)"
          >
            {{ tab.label }}
          </text>
        </view>
      </view>
    </view>

    <!-- 统计信息（仅非儿童模式） -->
    <view v-if="showDetailedValues && statistics.totalCount > 0" class="statistics-bar">
      <view class="stat-item">
        <text class="stat-label">平均</text>
        <text class="stat-value">{{ statistics.avgGlucose }}</text>
      </view>
      <view class="stat-item">
        <text class="stat-label">最高</text>
        <text class="stat-value high">{{ statistics.maxGlucose }}</text>
      </view>
      <view class="stat-item">
        <text class="stat-label">最低</text>
        <text class="stat-value low">{{ statistics.minGlucose }}</text>
      </view>
      <view class="stat-item">
        <text class="stat-label">TIR</text>
        <text class="stat-value">{{ statistics.timeInRange }}%</text>
      </view>
    </view>

    <!-- 图表容器 -->
    <view class="chart-container">
      <canvas 
        :id="canvasId"
        :canvas-id="canvasId" 
        class="curve-canvas"
        @touchstart="handleTouchStart"
        @touchmove="handleTouchMove"
        @touchend="handleTouchEnd"
      ></canvas>
      
      <!-- 触摸提示框 -->
      <view v-if="touchInfo.visible" class="touch-tooltip" :style="tooltipStyle">
        <text class="tooltip-time">{{ touchInfo.time }}</text>
        <text class="tooltip-value">{{ touchInfo.value }} mmol/L</text>
      </view>
      
      <!-- 空数据提示 -->
      <view v-if="chartData.length === 0" class="empty-state">
        <text class="empty-icon">📊</text>
        <text class="empty-text">暂无血糖数据</text>
        <text class="empty-hint">开始记录您的血糖值</text>
      </view>
    </view>

    <!-- 参考范围说明 -->
    <view v-if="showDetailedValues" class="reference-legend">
      <view class="legend-item">
        <view class="legend-dot" style="background: #EF4444;"></view>
        <text class="legend-text">低血糖 (&lt;{{ referenceRange.min }})</text>
      </view>
      <view class="legend-item">
        <view class="legend-dot" style="background: #10B981;"></view>
        <text class="legend-text">正常范围</text>
      </view>
      <view class="legend-item">
        <view class="legend-dot" style="background: #F59E0B;"></view>
        <text class="legend-text">高血糖 (&gt;{{ referenceRange.max }})</text>
      </view>
    </view>

    <!-- 儿童模式简化提示 -->
    <view v-else class="child-mode-hint">
      <text class="hint-emoji">{{ moodEmoji }}</text>
      <text class="hint-text">{{ moodText }}</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { useGlucoseCurveStore } from '@/store/glucoseCurve'
import { storeToRefs } from 'pinia'

const props = defineProps({
  canvasId: {
    type: String,
    default: 'glucoseCurveCanvas'
  },
  height: {
    type: Number,
    default: 300
  }
})

const glucoseCurveStore = useGlucoseCurveStore()
const { 
  viewType, 
  statistics, 
  referenceRange,
  currentViewData,
  aggregatedData
} = storeToRefs(glucoseCurveStore)

const { showDetailedValues, getPointColor } = glucoseCurveStore

// 视图切换选项
const viewTabs = [
  { label: '日', value: 'day' },
  { label: '周', value: 'week' },
  { label: '月', value: 'month' }
]

// Canvas 相关
let ctx = null
let canvasWidth = 0
let canvasHeight = 0
const padding = { top: 30, right: 20, bottom: 40, left: 50 }

// 触摸交互
const touchInfo = ref({
  visible: false,
  x: 0,
  y: 0,
  time: '',
  value: ''
})

// 图表数据
const chartData = computed(() => {
  return viewType.value === 'day' ? currentViewData.value : aggregatedData.value
})

// 视图类型文本
const viewTypeText = computed(() => {
  const map = {
    day: '今日',
    week: '近7天',
    month: '近30天'
  }
  return map[viewType.value] || ''
})

// 儿童模式情绪提示
const moodEmoji = computed(() => {
  if (statistics.value.totalCount === 0) return '😊'
  
  const tir = statistics.value.timeInRange
  if (tir >= 70) return '😊'
  if (tir >= 50) return '😐'
  return '😟'
})

const moodText = computed(() => {
  if (statistics.value.totalCount === 0) return '还没有记录哦'
  
  const tir = statistics.value.timeInRange
  if (tir >= 70) return '你做得很棒！'
  if (tir >= 50) return '继续加油！'
  return '需要多注意一下'
})

// 提示框样式
const tooltipStyle = computed(() => {
  return {
    left: touchInfo.value.x + 'px',
    top: (touchInfo.value.y - 60) + 'px'
  }
})

// 切换视图
const switchView = (type) => {
  glucoseCurveStore.setViewType(type)
  nextTick(() => {
    drawChart()
  })
}

// 初始化 Canvas
const initCanvas = () => {
  return new Promise((resolve) => {
    setTimeout(() => {
      const query = uni.createSelectorQuery()
      query.select(`#${props.canvasId}`).boundingClientRect()
      query.exec((res) => {
        console.log('Canvas boundingClientRect:', res)
        if (res && res[0]) {
          canvasWidth = res[0].width
          canvasHeight = res[0].height || props.height
          
          console.log('Canvas size:', canvasWidth, 'x', canvasHeight)
          
          // 使用旧版 API（更兼容）
          try {
            ctx = uni.createCanvasContext(props.canvasId)
            console.log('Canvas context created:', !!ctx)
            
            if (ctx) {
              console.log('Canvas initialization successful')
              resolve()
            } else {
              console.error('Canvas context is null')
              resolve()
            }
          } catch (error) {
            console.error('Error creating canvas context:', error)
            resolve()
          }
        } else {
          console.error('Canvas element not found with ID:', props.canvasId)
          console.log('Query result:', res)
          resolve()
        }
      })
    }, 500)
  })
}

// 绘制图表
const drawChart = () => {
  console.log('drawChart called, ctx:', !!ctx, 'data length:', chartData.value.length)
  
  if (!ctx) {
    console.error('Canvas context not initialized')
    return
  }
  
  if (chartData.value.length === 0) {
    console.warn('No chart data available')
    return
  }
  
  // 清空画布
  ctx.clearRect && ctx.clearRect(0, 0, canvasWidth, canvasHeight)
  
  const chartWidth = canvasWidth - padding.left - padding.right
  const chartHeight = canvasHeight - padding.top - padding.bottom
  
  console.log('Chart dimensions:', chartWidth, chartHeight)
  
  // 计算数据范围
  const values = chartData.value.map(d => d.glucose_value)
  const minValue = Math.min(...values, referenceRange.value.min - 1)
  const maxValue = Math.max(...values, referenceRange.value.max + 1)
  const valueRange = maxValue - minValue
  
  console.log('Value range:', minValue, maxValue)
  
  // 绘制参考范围背景
  drawReferenceZone(chartWidth, chartHeight, minValue, valueRange)
  
  // 绘制网格
  drawGrid(chartWidth, chartHeight)
  
  // 绘制坐标轴
  drawAxes(chartWidth, chartHeight, minValue, maxValue)
  
  // 绘制曲线
  drawCurve(chartWidth, chartHeight, minValue, valueRange)
  
  // 绘制数据点
  drawDataPoints(chartWidth, chartHeight, minValue, valueRange)
  
  // 执行绘制
  if (ctx.draw) {
    ctx.draw()
  }
}

// 绘制参考范围
const drawReferenceZone = (chartWidth, chartHeight, minValue, valueRange) => {
  const yMin = valueToY(referenceRange.value.min, chartHeight, minValue, valueRange)
  const yMax = valueToY(referenceRange.value.max, chartHeight, minValue, valueRange)
  
  ctx.fillStyle = 'rgba(16, 185, 129, 0.1)'
  ctx.fillRect(
    padding.left,
    padding.top + yMax,
    chartWidth,
    yMin - yMax
  )
}

// 绘制网格
const drawGrid = (chartWidth, chartHeight) => {
  ctx.strokeStyle = '#E5E7EB'
  ctx.lineWidth = 1
  
  // 水平网格线
  for (let i = 0; i <= 5; i++) {
    const y = padding.top + (chartHeight / 5) * i
    ctx.beginPath()
    ctx.moveTo(padding.left, y)
    ctx.lineTo(padding.left + chartWidth, y)
    ctx.stroke()
  }
}

// 绘制坐标轴
const drawAxes = (chartWidth, chartHeight, minValue, maxValue) => {
  ctx.strokeStyle = '#9CA3AF'
  ctx.lineWidth = 2
  
  // Y轴
  ctx.beginPath()
  ctx.moveTo(padding.left, padding.top)
  ctx.lineTo(padding.left, padding.top + chartHeight)
  ctx.stroke()
  
  // X轴
  ctx.beginPath()
  ctx.moveTo(padding.left, padding.top + chartHeight)
  ctx.lineTo(padding.left + chartWidth, padding.top + chartHeight)
  ctx.stroke()
  
  // Y轴刻度
  ctx.fillStyle = '#6B7280'
  ctx.font = '12px sans-serif'
  ctx.textAlign = 'right'
  ctx.textBaseline = 'middle'
  
  for (let i = 0; i <= 5; i++) {
    const value = minValue + ((maxValue - minValue) / 5) * (5 - i)
    const y = padding.top + (chartHeight / 5) * i
    ctx.fillText(value.toFixed(1), padding.left - 10, y)
  }
  
  // X轴时间标签
  ctx.textAlign = 'center'
  ctx.textBaseline = 'top'
  
  if (chartData.value.length > 0) {
    const labelCount = Math.min(4, chartData.value.length)
    const step = Math.floor(chartData.value.length / labelCount)
    
    for (let i = 0; i < labelCount; i++) {
      const index = i * step
      if (chartData.value[index]) {
        const x = padding.left + (chartWidth / (chartData.value.length - 1)) * index
        const time = formatTime(chartData.value[index].measure_time)
        ctx.fillText(time, x, padding.top + chartHeight + 10)
      }
    }
  }
}

// 绘制曲线
const drawCurve = (chartWidth, chartHeight, minValue, valueRange) => {
  if (chartData.value.length < 2) return
  
  ctx.strokeStyle = '#3B82F6'
  ctx.lineWidth = 2
  ctx.lineJoin = 'round'
  ctx.lineCap = 'round'
  
  ctx.beginPath()
  
  chartData.value.forEach((point, index) => {
    const x = padding.left + (chartWidth / (chartData.value.length - 1)) * index
    const y = valueToY(point.glucose_value, chartHeight, minValue, valueRange)
    
    if (index === 0) {
      ctx.moveTo(x, padding.top + y)
    } else {
      ctx.lineTo(x, padding.top + y)
    }
  })
  
  ctx.stroke()
}

// 绘制数据点
const drawDataPoints = (chartWidth, chartHeight, minValue, valueRange) => {
  chartData.value.forEach((point, index) => {
    const x = padding.left + (chartWidth / (chartData.value.length - 1)) * index
    const y = valueToY(point.glucose_value, chartHeight, minValue, valueRange)
    
    const color = getPointColor(point.glucose_value)
    
    ctx.fillStyle = color
    ctx.beginPath()
    ctx.arc(x, padding.top + y, 4, 0, Math.PI * 2)
    ctx.fill()
    
    ctx.strokeStyle = '#FFFFFF'
    ctx.lineWidth = 2
    ctx.stroke()
  })
}

// 值转Y坐标
const valueToY = (value, chartHeight, minValue, valueRange) => {
  return chartHeight - ((value - minValue) / valueRange) * chartHeight
}

// 格式化时间
const formatTime = (timestamp) => {
  const date = new Date(timestamp)
  
  if (viewType.value === 'day') {
    return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`
  } else {
    return `${date.getMonth() + 1}/${date.getDate()}`
  }
}

// 触摸事件处理
const handleTouchStart = (e) => {
  if (chartData.value.length === 0) return
  handleTouch(e)
}

const handleTouchMove = (e) => {
  if (chartData.value.length === 0) return
  handleTouch(e)
}

const handleTouchEnd = () => {
  touchInfo.value.visible = false
}

const handleTouch = (e) => {
  const touch = e.touches[0]
  const x = touch.x
  const y = touch.y
  
  // 计算最近的数据点
  const chartWidth = canvasWidth - padding.left - padding.right
  const relativeX = x - padding.left
  
  if (relativeX < 0 || relativeX > chartWidth) return
  
  const index = Math.round((relativeX / chartWidth) * (chartData.value.length - 1))
  const point = chartData.value[index]
  
  if (point) {
    touchInfo.value = {
      visible: true,
      x: x,
      y: y,
      time: formatTime(point.measure_time),
      value: point.glucose_value.toFixed(1)
    }
  }
}

// 监听数据变化
watch(() => chartData.value, (newData) => {
  console.log('Chart data changed, length:', newData.length)
  if (ctx) {
    nextTick(() => {
      drawChart()
    })
  } else {
    console.warn('Canvas context not ready yet')
  }
}, { deep: true })

onMounted(async () => {
  console.log('Component mounted, initializing canvas...')
  await initCanvas()
  console.log('Canvas initialized, drawing chart...')
  nextTick(() => {
    drawChart()
  })
})
</script>

<style scoped>
.glucose-curve-chart {
  background: white;
  border-radius: 16rpx;
  padding: 32rpx;
  margin-bottom: 20rpx;
}

.glucose-curve-chart.compact {
  background: transparent;
  padding: 0;
  margin-bottom: 0;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.header-left {
  display: flex;
  flex-direction: column;
}

.chart-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
}

.chart-subtitle {
  font-size: 24rpx;
  color: #9CA3AF;
  margin-top: 4rpx;
}

.view-tabs {
  display: flex;
  gap: 8rpx;
  background: #F3F4F6;
  border-radius: 12rpx;
  padding: 4rpx;
}

.view-tab {
  padding: 8rpx 20rpx;
  font-size: 24rpx;
  color: #6B7280;
  border-radius: 8rpx;
  transition: all 0.3s;
}

.view-tab.active {
  background: white;
  color: #3B82F6;
  font-weight: bold;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.1);
}

.statistics-bar {
  display: flex;
  justify-content: space-around;
  padding: 20rpx;
  background: #F9FAFB;
  border-radius: 12rpx;
  margin-bottom: 24rpx;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat-label {
  font-size: 22rpx;
  color: #9CA3AF;
  margin-bottom: 8rpx;
}

.stat-value {
  font-size: 28rpx;
  font-weight: bold;
  color: #1F2937;
}

.stat-value.high {
  color: #F59E0B;
}

.stat-value.low {
  color: #EF4444;
}

.chart-container {
  position: relative;
  height: 300rpx;
  margin-bottom: 20rpx;
}

.curve-canvas {
  width: 100%;
  height: 100%;
}

.touch-tooltip {
  position: absolute;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 12rpx 16rpx;
  border-radius: 8rpx;
  font-size: 22rpx;
  pointer-events: none;
  transform: translateX(-50%);
  white-space: nowrap;
  z-index: 10;
}

.tooltip-time {
  display: block;
  margin-bottom: 4rpx;
}

.tooltip-value {
  display: block;
  font-weight: bold;
}

.empty-state {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.empty-icon {
  font-size: 80rpx;
  display: block;
  margin-bottom: 16rpx;
}

.empty-text {
  font-size: 28rpx;
  color: #6B7280;
  display: block;
  margin-bottom: 8rpx;
}

.empty-hint {
  font-size: 24rpx;
  color: #9CA3AF;
  display: block;
}

.reference-legend {
  display: flex;
  justify-content: center;
  gap: 32rpx;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8rpx;
}

.legend-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
}

.legend-text {
  font-size: 22rpx;
  color: #6B7280;
}

.child-mode-hint {
  text-align: center;
  padding: 32rpx;
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
  border-radius: 16rpx;
}

.hint-emoji {
  font-size: 80rpx;
  display: block;
  margin-bottom: 16rpx;
}

.hint-text {
  font-size: 32rpx;
  font-weight: bold;
  color: #92400E;
}
</style>
