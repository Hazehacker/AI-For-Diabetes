<template>
  <view class="report-page">
    <!-- 顶部时间选择 -->
    <view class="time-selector">
      <view 
        v-for="period in timePeriods" 
        :key="period.value"
        class="time-item"
        :class="{ active: selectedPeriod === period.value }"
        @tap="selectPeriod(period.value)"
      >
        <text>{{ period.label }}</text>
      </view>
    </view>

    <!-- 综合评分卡片 -->
    <view class="score-card">
      <view class="score-header">
        <view class="score-info">
          <text class="score-label">血糖管理评分</text>
          <text class="score-date">{{ reportDateRange }}</text>
        </view>
        <view class="score-badge" :class="scoreLevel">
          <text class="badge-text">{{ scoreLevelText }}</text>
        </view>
      </view>
      <view class="score-main">
        <view class="score-circle" :style="{ background: scoreGradient }">
          <text class="score-value">{{ overallScore }}</text>
          <text class="score-unit">分</text>
        </view>
        <view class="score-details">
          <view class="detail-item">
            <text class="detail-label">达标率</text>
            <text class="detail-value good">{{ stats.inRangeRate }}%</text>
          </view>
          <view class="detail-item">
            <text class="detail-label">平均血糖</text>
            <text class="detail-value">{{ stats.avgGlucose }} mmol/L</text>
          </view>
          <view class="detail-item">
            <text class="detail-label">血糖变异</text>
            <text class="detail-value" :class="variabilityClass">{{ stats.variability }}%</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 血糖趋势图 -->
    <view class="chart-card">
      <view class="card-header">
        <text class="card-title">📈 血糖趋势</text>
        <view class="chart-legend">
          <view class="legend-item">
            <view class="legend-dot high"></view>
            <text>偏高</text>
          </view>
          <view class="legend-item">
            <view class="legend-dot normal"></view>
            <text>正常</text>
          </view>
          <view class="legend-item">
            <view class="legend-dot low"></view>
            <text>偏低</text>
          </view>
        </view>
      </view>
      <view class="trend-chart">
        <!-- 参考区域 -->
        <view class="reference-zone"></view>
        <!-- 数据点和曲线 -->
        <view class="chart-content">
          <view 
            v-for="(point, index) in trendData" 
            :key="index"
            class="data-point"
            :class="getPointClass(point.value)"
            :style="getPointStyle(point, index)"
          >
            <view class="point-dot"></view>
            <text class="point-value">{{ point.value }}</text>
          </view>
        </view>
        <!-- X轴标签 -->
        <view class="x-axis">
          <text v-for="(label, index) in xLabels" :key="index" class="x-label">{{ label }}</text>
        </view>
      </view>
    </view>

    <!-- 血糖分布 -->
    <view class="distribution-card">
      <view class="card-header">
        <text class="card-title">📊 血糖分布</text>
      </view>
      <view class="distribution-chart">
        <view class="dist-bar-container">
          <view class="dist-bar high" :style="{ width: distribution.high + '%' }">
            <text v-if="distribution.high > 10">{{ distribution.high }}%</text>
          </view>
          <view class="dist-bar normal" :style="{ width: distribution.normal + '%' }">
            <text>{{ distribution.normal }}%</text>
          </view>
          <view class="dist-bar low" :style="{ width: distribution.low + '%' }">
            <text v-if="distribution.low > 10">{{ distribution.low }}%</text>
          </view>
        </view>
        <view class="dist-labels">
          <view class="dist-label">
            <view class="label-dot high"></view>
            <text>偏高 (>10.0)</text>
          </view>
          <view class="dist-label">
            <view class="label-dot normal"></view>
            <text>正常 (3.9-10.0)</text>
          </view>
          <view class="dist-label">
            <view class="label-dot low"></view>
            <text>偏低 (<3.9)</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 详细统计 -->
    <view class="stats-card">
      <view class="card-header">
        <text class="card-title">📋 详细统计</text>
      </view>
      <view class="stats-grid">
        <view class="stat-item">
          <text class="stat-icon">🎯</text>
          <text class="stat-value">{{ stats.measurements }}</text>
          <text class="stat-label">测量次数</text>
        </view>
        <view class="stat-item">
          <text class="stat-icon">⬆️</text>
          <text class="stat-value high">{{ stats.maxGlucose }}</text>
          <text class="stat-label">最高血糖</text>
        </view>
        <view class="stat-item">
          <text class="stat-icon">⬇️</text>
          <text class="stat-value low">{{ stats.minGlucose }}</text>
          <text class="stat-label">最低血糖</text>
        </view>
        <view class="stat-item">
          <text class="stat-icon">📏</text>
          <text class="stat-value">{{ stats.stdDev }}</text>
          <text class="stat-label">标准差</text>
        </view>
      </view>
    </view>

    <!-- 时段分析 -->
    <view class="period-card">
      <view class="card-header">
        <text class="card-title">⏰ 时段分析</text>
      </view>
      <view class="period-list">
        <view 
          v-for="period in periodAnalysis" 
          :key="period.name"
          class="period-item"
        >
          <view class="period-info">
            <text class="period-icon">{{ period.icon }}</text>
            <text class="period-name">{{ period.name }}</text>
          </view>
          <view class="period-data">
            <text class="period-avg" :class="getValueClass(period.avg)">{{ period.avg }}</text>
            <view class="period-bar-bg">
              <view 
                class="period-bar" 
                :class="getValueClass(period.avg)"
                :style="{ width: getBarWidth(period.avg) + '%' }"
              ></view>
            </view>
          </view>
        </view>
      </view>
    </view>

    <!-- 健康建议 -->
    <view class="advice-card">
      <view class="card-header">
        <text class="card-title">💡 健康建议</text>
      </view>
      <view class="advice-list">
        <view 
          v-for="(advice, index) in healthAdvice" 
          :key="index"
          class="advice-item"
          :class="advice.type"
        >
          <text class="advice-icon">{{ advice.icon }}</text>
          <view class="advice-content">
            <text class="advice-title">{{ advice.title }}</text>
            <text class="advice-desc">{{ advice.desc }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 导出报告按钮 -->
    <view class="export-section">
      <view class="export-btn" @tap="exportReport">
        <text class="export-icon">📤</text>
        <text class="export-text">导出完整报告</text>
      </view>
      <view class="share-btn" @tap="shareReport">
        <text class="share-icon">🔗</text>
        <text class="share-text">分享给医生</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'

// 时间周期选择
const timePeriods = [
  { label: '7天', value: '7d' },
  { label: '14天', value: '14d' },
  { label: '30天', value: '30d' },
  { label: '90天', value: '90d' }
]
const selectedPeriod = ref('7d')

const selectPeriod = (period) => {
  selectedPeriod.value = period
}

// 报告日期范围
const reportDateRange = computed(() => {
  const end = new Date()
  const days = parseInt(selectedPeriod.value)
  const start = new Date(end.getTime() - days * 24 * 60 * 60 * 1000)
  return `${start.getMonth() + 1}/${start.getDate()} - ${end.getMonth() + 1}/${end.getDate()}`
})

// 综合评分
const overallScore = ref(85)
const scoreLevel = computed(() => {
  if (overallScore.value >= 90) return 'excellent'
  if (overallScore.value >= 75) return 'good'
  if (overallScore.value >= 60) return 'fair'
  return 'poor'
})
const scoreLevelText = computed(() => {
  if (overallScore.value >= 90) return '优秀'
  if (overallScore.value >= 75) return '良好'
  if (overallScore.value >= 60) return '一般'
  return '需改善'
})
const scoreGradient = computed(() => {
  if (overallScore.value >= 90) return 'linear-gradient(135deg, #10B981 0%, #059669 100%)'
  if (overallScore.value >= 75) return 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)'
  if (overallScore.value >= 60) return 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)'
  return 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)'
})

// 统计数据
const stats = ref({
  inRangeRate: 78,
  avgGlucose: 6.8,
  variability: 24,
  measurements: 42,
  maxGlucose: 12.3,
  minGlucose: 4.2,
  stdDev: 1.8
})

const variabilityClass = computed(() => {
  if (stats.value.variability <= 20) return 'good'
  if (stats.value.variability <= 36) return 'fair'
  return 'poor'
})

// 趋势数据
const trendData = ref([
  { time: '周一', value: 6.2 },
  { time: '周二', value: 7.8 },
  { time: '周三', value: 5.9 },
  { time: '周四', value: 8.5 },
  { time: '周五', value: 6.4 },
  { time: '周六', value: 11.2 },
  { time: '周日', value: 7.1 }
])

const xLabels = computed(() => trendData.value.map(d => d.time))

const getPointClass = (value) => {
  if (value > 10) return 'high'
  if (value < 3.9) return 'low'
  return 'normal'
}

const getPointStyle = (point, index) => {
  const minVal = 2
  const maxVal = 15
  const range = maxVal - minVal
  const bottom = ((point.value - minVal) / range) * 100
  const left = (index / (trendData.value.length - 1)) * 100
  return {
    bottom: `${Math.max(5, Math.min(95, bottom))}%`,
    left: `${left}%`
  }
}

// 血糖分布
const distribution = ref({
  high: 15,
  normal: 78,
  low: 7
})

// 时段分析
const periodAnalysis = ref([
  { name: '空腹', icon: '🌅', avg: 5.8 },
  { name: '早餐后', icon: '🍳', avg: 8.2 },
  { name: '午餐后', icon: '🍱', avg: 7.5 },
  { name: '晚餐后', icon: '🍲', avg: 9.1 },
  { name: '睡前', icon: '🌙', avg: 6.4 }
])

const getValueClass = (value) => {
  if (value > 10) return 'high'
  if (value < 3.9) return 'low'
  return 'normal'
}

const getBarWidth = (value) => {
  return Math.min(100, (value / 15) * 100)
}

// 健康建议
const healthAdvice = ref([
  {
    type: 'warning',
    icon: '⚠️',
    title: '晚餐后血糖偏高',
    desc: '建议减少晚餐碳水摄入，餐后适当散步15-30分钟'
  },
  {
    type: 'success',
    icon: '✅',
    title: '空腹血糖控制良好',
    desc: '继续保持规律作息和健康饮食习惯'
  },
  {
    type: 'info',
    icon: '💊',
    title: '用药提醒',
    desc: '请按时服用降糖药物，不要漏服或自行调整剂量'
  }
])

// 导出报告
const exportReport = () => {
  uni.showToast({
    title: '报告已生成',
    icon: 'success'
  })
}

// 分享报告
const shareReport = () => {
  uni.showToast({
    title: '已复制分享链接',
    icon: 'success'
  })
}
</script>

<style scoped>
.report-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #FEF3E7 0%, #F3F4F6 30%);
  padding: 20rpx;
  padding-bottom: 40rpx;
}

/* 时间选择器 */
.time-selector {
  display: flex;
  background: white;
  border-radius: 16rpx;
  padding: 8rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 2rpx 12rpx rgba(0, 0, 0, 0.06);
}

.time-item {
  flex: 1;
  text-align: center;
  padding: 16rpx 0;
  border-radius: 12rpx;
  font-size: 26rpx;
  color: #6B7280;
  transition: all 0.3s;
}

.time-item.active {
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
  color: white;
  font-weight: 600;
}

/* 评分卡片 */
.score-card {
  background: white;
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.score-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32rpx;
}

.score-label {
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
  display: block;
}

.score-date {
  font-size: 24rpx;
  color: #9CA3AF;
  margin-top: 8rpx;
  display: block;
}

.score-badge {
  padding: 8rpx 20rpx;
  border-radius: 20rpx;
  font-size: 24rpx;
  font-weight: 600;
}

.score-badge.excellent {
  background: #D1FAE5;
  color: #059669;
}

.score-badge.good {
  background: #DBEAFE;
  color: #2563EB;
}

.score-badge.fair {
  background: #FEF3C7;
  color: #D97706;
}

.score-badge.poor {
  background: #FEE2E2;
  color: #DC2626;
}

.score-main {
  display: flex;
  align-items: center;
  gap: 40rpx;
}

.score-circle {
  width: 180rpx;
  height: 180rpx;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.15);
}

.score-value {
  font-size: 64rpx;
  font-weight: bold;
  color: white;
  line-height: 1;
}

.score-unit {
  font-size: 24rpx;
  color: rgba(255, 255, 255, 0.9);
  margin-top: 4rpx;
}

.score-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12rpx 0;
  border-bottom: 1rpx solid #F3F4F6;
}

.detail-item:last-child {
  border-bottom: none;
}

.detail-label {
  font-size: 26rpx;
  color: #6B7280;
}

.detail-value {
  font-size: 28rpx;
  font-weight: 600;
  color: #1F2937;
}

.detail-value.good {
  color: #10B981;
}

.detail-value.fair {
  color: #F59E0B;
}

.detail-value.poor {
  color: #EF4444;
}

/* 图表卡片通用样式 */
.chart-card, .distribution-card, .stats-card, .period-card, .advice-card {
  background: white;
  border-radius: 24rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 4rpx 20rpx rgba(0, 0, 0, 0.08);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.card-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #1F2937;
}

/* 图例 */
.chart-legend {
  display: flex;
  gap: 16rpx;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6rpx;
  font-size: 22rpx;
  color: #6B7280;
}

.legend-dot {
  width: 16rpx;
  height: 16rpx;
  border-radius: 50%;
}

.legend-dot.high { background: #EF4444; }
.legend-dot.normal { background: #10B981; }
.legend-dot.low { background: #F59E0B; }

/* 趋势图 */
.trend-chart {
  position: relative;
  height: 300rpx;
  margin-top: 20rpx;
}

.reference-zone {
  position: absolute;
  left: 0;
  right: 0;
  top: 30%;
  bottom: 30%;
  background: rgba(16, 185, 129, 0.1);
  border-top: 2rpx dashed #10B981;
  border-bottom: 2rpx dashed #10B981;
}

.chart-content {
  position: absolute;
  left: 20rpx;
  right: 20rpx;
  top: 20rpx;
  bottom: 60rpx;
}

.data-point {
  position: absolute;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.point-dot {
  width: 20rpx;
  height: 20rpx;
  border-radius: 50%;
  border: 4rpx solid white;
  box-shadow: 0 2rpx 8rpx rgba(0, 0, 0, 0.2);
}

.data-point.high .point-dot { background: #EF4444; }
.data-point.normal .point-dot { background: #10B981; }
.data-point.low .point-dot { background: #F59E0B; }

.point-value {
  font-size: 20rpx;
  color: #6B7280;
  margin-top: 8rpx;
}

.x-axis {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  padding: 0 10rpx;
}

.x-label {
  font-size: 22rpx;
  color: #9CA3AF;
}

/* 分布图 */
.distribution-chart {
  padding: 20rpx 0;
}

.dist-bar-container {
  display: flex;
  height: 48rpx;
  border-radius: 24rpx;
  overflow: hidden;
  margin-bottom: 24rpx;
}

.dist-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22rpx;
  font-weight: 600;
  color: white;
  transition: width 0.5s ease;
}

.dist-bar.high { background: linear-gradient(90deg, #EF4444, #F87171); }
.dist-bar.normal { background: linear-gradient(90deg, #10B981, #34D399); }
.dist-bar.low { background: linear-gradient(90deg, #F59E0B, #FBBF24); }

.dist-labels {
  display: flex;
  justify-content: space-around;
}

.dist-label {
  display: flex;
  align-items: center;
  gap: 8rpx;
  font-size: 24rpx;
  color: #6B7280;
}

.label-dot {
  width: 20rpx;
  height: 20rpx;
  border-radius: 6rpx;
}

.label-dot.high { background: #EF4444; }
.label-dot.normal { background: #10B981; }
.label-dot.low { background: #F59E0B; }

/* 统计网格 */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
}

.stat-item {
  background: #F9FAFB;
  border-radius: 16rpx;
  padding: 24rpx;
  text-align: center;
}

.stat-icon {
  font-size: 40rpx;
  display: block;
  margin-bottom: 12rpx;
}

.stat-value {
  font-size: 36rpx;
  font-weight: bold;
  color: #1F2937;
  display: block;
}

.stat-value.high { color: #EF4444; }
.stat-value.low { color: #F59E0B; }

.stat-label {
  font-size: 24rpx;
  color: #6B7280;
  margin-top: 8rpx;
  display: block;
}

/* 时段分析 */
.period-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.period-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 16rpx;
  background: #F9FAFB;
  border-radius: 12rpx;
}

.period-info {
  display: flex;
  align-items: center;
  gap: 12rpx;
  width: 160rpx;
}

.period-icon {
  font-size: 32rpx;
}

.period-name {
  font-size: 26rpx;
  color: #374151;
}

.period-data {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 16rpx;
}

.period-avg {
  font-size: 28rpx;
  font-weight: 600;
  width: 80rpx;
}

.period-avg.high { color: #EF4444; }
.period-avg.normal { color: #10B981; }
.period-avg.low { color: #F59E0B; }

.period-bar-bg {
  flex: 1;
  height: 16rpx;
  background: #E5E7EB;
  border-radius: 8rpx;
  overflow: hidden;
}

.period-bar {
  height: 100%;
  border-radius: 8rpx;
  transition: width 0.5s ease;
}

.period-bar.high { background: linear-gradient(90deg, #EF4444, #F87171); }
.period-bar.normal { background: linear-gradient(90deg, #10B981, #34D399); }
.period-bar.low { background: linear-gradient(90deg, #F59E0B, #FBBF24); }

/* 健康建议 */
.advice-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.advice-item {
  display: flex;
  gap: 16rpx;
  padding: 20rpx;
  border-radius: 16rpx;
}

.advice-item.warning {
  background: linear-gradient(135deg, #FEF3C7 0%, #FDE68A 100%);
}

.advice-item.success {
  background: linear-gradient(135deg, #D1FAE5 0%, #A7F3D0 100%);
}

.advice-item.info {
  background: linear-gradient(135deg, #DBEAFE 0%, #BFDBFE 100%);
}

.advice-icon {
  font-size: 40rpx;
}

.advice-content {
  flex: 1;
}

.advice-title {
  font-size: 28rpx;
  font-weight: 600;
  color: #1F2937;
  display: block;
  margin-bottom: 8rpx;
}

.advice-desc {
  font-size: 24rpx;
  color: #4B5563;
  line-height: 1.5;
}

/* 导出按钮 */
.export-section {
  display: flex;
  gap: 20rpx;
  margin-top: 32rpx;
}

.export-btn, .share-btn {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12rpx;
  padding: 28rpx;
  border-radius: 16rpx;
  font-size: 28rpx;
  font-weight: 600;
}

.export-btn {
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
  color: white;
  box-shadow: 0 4rpx 16rpx rgba(245, 158, 11, 0.4);
}

.share-btn {
  background: white;
  color: #F59E0B;
  border: 2rpx solid #F59E0B;
}

.export-icon, .share-icon {
  font-size: 32rpx;
}
</style>
