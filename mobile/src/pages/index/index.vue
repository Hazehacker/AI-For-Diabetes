<template>
  <view class="home-page">
    <!-- 顶部欢迎区 -->
    <view class="welcome-header">
      <view class="welcome-text">
        <text class="greeting">{{ greetingText }}</text>
        <text class="username">{{ userInfo.nickname || '用户' }}</text>
      </view>
      <view class="role-badge" :class="'role-' + userRole">
        <text class="role-text">{{ roleText }}</text>
      </view>
    </view>

    <!-- 仪表盘核心区域 -->
    <view class="dashboard-section">
      <!-- 当前血糖状态 -->
      <view class="glucose-status-card" :class="statusColor">
        <view class="status-header">
          <text class="status-label">当前血糖</text>
          <text class="status-time">{{ currentTime }}</text>
        </view>
        <view class="status-value-area">
          <text class="glucose-value">{{ currentGlucose.value }}</text>
          <text class="glucose-unit">mmol/L</text>
          <text class="trend-arrow">{{ trendArrow }}</text>
        </view>
        <text class="status-text">{{ statusText }}</text>
      </view>

      <!-- 血糖曲线图 -->
      <view class="chart-card">
        <view class="card-header">
          <text class="card-title">今日血糖趋势</text>
          <text class="view-more" @tap="goToDashboard">查看详情 →</text>
        </view>
        <GlucoseCurveChart canvas-id="homeGlucoseChart" :compact="true" />
      </view>

      <!-- 每日统计 -->
      <view class="stats-grid">
        <view class="stat-item">
          <text class="stat-value">{{ stats.avgGlucose }}</text>
          <text class="stat-label">平均值</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ stats.timeInRange }}%</text>
          <text class="stat-label">达标率</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ stats.measureCount }}</text>
          <text class="stat-label">测量次数</text>
        </view>
      </view>
    </view>

    <!-- 同伴板块入口 -->
    <view class="section-card companion-card" @tap="goToCompanion">
      <view class="card-icon-area">
        <text class="card-icon">👥</text>
      </view>
      <view class="card-content">
        <text class="card-title">同伴板块</text>
        <text class="card-desc">与小伙伴一起分享经验</text>
        <view class="preview-tags">
          <text class="preview-tag">3条新动态</text>
          <text class="preview-tag">5人在线</text>
        </view>
      </view>
      <text class="card-arrow">→</text>
    </view>

    <!-- 互动板块入口 -->
    <view class="section-card interaction-card" @tap="goToInteraction">
      <view class="card-icon-area">
        <text class="card-icon">🎮</text>
      </view>
      <view class="card-content">
        <text class="card-title">互动板块</text>
        <text class="card-desc">参与挑战，赢取奖励</text>
        <view class="preview-tags">
          <text class="preview-tag">2个新挑战</text>
          <text class="preview-tag">积分排行</text>
        </view>
      </view>
      <text class="card-arrow">→</text>
    </view>

    <!-- 热量板块入口 -->
    <view class="section-card calories-card" @tap="goToCalories">
      <view class="card-icon-area">
        <text class="card-icon">🍱</text>
      </view>
      <view class="card-content">
        <text class="card-title">热量板块</text>
        <text class="card-desc">记录饮食，智能推荐食谱</text>
        <view class="preview-tags">
          <text class="preview-tag">热量记录</text>
          <text class="preview-tag">食谱推荐</text>
        </view>
      </view>
      <text class="card-arrow">→</text>
    </view>

    <!-- 底部占位 -->
    <view class="bottom-spacer"></view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useDashboardStore } from '@/store/dashboard'
import { useUserStore } from '@/store/user'
import { storeToRefs } from 'pinia'
import GlucoseCurveChart from '@/components/GlucoseCurveChart.vue'

const dashboardStore = useDashboardStore()
const userStore = useUserStore()

const { currentGlucose, stats, userRole } = storeToRefs(dashboardStore)
const { userInfo } = storeToRefs(userStore)
const { statusColor, trendArrow } = dashboardStore

// 当前时间
const currentTime = ref('')

// 问候语
const greetingText = computed(() => {
  const hour = new Date().getHours()
  if (hour < 6) return '夜深了'
  if (hour < 9) return '早上好'
  if (hour < 12) return '上午好'
  if (hour < 14) return '中午好'
  if (hour < 18) return '下午好'
  return '晚上好'
})

// 角色文本
const roleText = computed(() => {
  const map = {
    'child_under_12': '儿童模式',
    'teen_above_12': '青少年模式',
    'guardian': '家属模式'
  }
  return map[userRole.value] || '用户'
})

// 状态文本
const statusText = computed(() => {
  const value = currentGlucose.value.value
  if (value < 3.9) return '血糖偏低，请注意'
  if (value > 10.0) return '血糖偏高，请注意'
  if (value > 7.8) return '血糖略高'
  return '血糖正常'
})

// 更新时间
const updateTime = () => {
  const now = new Date()
  const hours = now.getHours().toString().padStart(2, '0')
  const minutes = now.getMinutes().toString().padStart(2, '0')
  currentTime.value = `${hours}:${minutes}`
}

// 跳转到完整仪表盘
const goToDashboard = () => {
  uni.navigateTo({
    url: '/pages/dashboard/dashboard'
  })
}

// 跳转到同伴板块
const goToCompanion = () => {
  uni.navigateTo({
    url: '/pages/community/companion'
  })
}

// 跳转到互动板块
const goToInteraction = () => {
  uni.navigateTo({
    url: '/pages/community/interaction'
  })
}

// 跳转到热量板块
const goToCalories = () => {
  uni.navigateTo({
    url: '/pages/calories/index'
  })
}

onMounted(() => {
  updateTime()
  setInterval(updateTime, 60000)
  
  // 初始化数据
  if (!currentGlucose.value.value) {
    dashboardStore.updateCurrentGlucose({
      value: 6.2,
      timestamp: new Date(),
      trend: 'stable'
    })
  }
})
</script>

<style scoped>
.home-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 50%, #F3F4F6 50%);
  padding: 20rpx;
  padding-bottom: 120rpx;
}

/* 欢迎区 */
.welcome-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 40rpx 20rpx;
}

.welcome-text {
  display: flex;
  flex-direction: column;
}

.greeting {
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 8rpx;
}

.username {
  font-size: 40rpx;
  font-weight: bold;
  color: white;
}

.role-badge {
  padding: 12rpx 24rpx;
  border-radius: 20rpx;
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10rpx);
}

.role-text {
  font-size: 24rpx;
  color: white;
}

/* 仪表盘区域 */
.dashboard-section {
  margin-bottom: 32rpx;
}

/* 血糖状态卡片 */
.glucose-status-card {
  background: white;
  border-radius: 24rpx;
  padding: 32rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
}

.glucose-status-card.status-normal {
  border-left: 8rpx solid #10B981;
}

.glucose-status-card.status-warning {
  border-left: 8rpx solid #F59E0B;
}

.glucose-status-card.status-danger {
  border-left: 8rpx solid #EF4444;
}

.status-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20rpx;
}

.status-label {
  font-size: 28rpx;
  color: #6B7280;
}

.status-time {
  font-size: 24rpx;
  color: #9CA3AF;
}

.status-value-area {
  display: flex;
  align-items: baseline;
  margin-bottom: 16rpx;
}

.glucose-value {
  font-size: 80rpx;
  font-weight: bold;
  color: #1F2937;
  line-height: 1;
}

.glucose-unit {
  font-size: 28rpx;
  color: #6B7280;
  margin-left: 12rpx;
}

.trend-arrow {
  font-size: 48rpx;
  margin-left: 16rpx;
}

.status-text {
  font-size: 28rpx;
  color: #6B7280;
}

/* 图表卡片 */
.chart-card {
  background: white;
  border-radius: 20rpx;
  padding: 24rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.card-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
}

.view-more {
  font-size: 24rpx;
  color: #3B82F6;
}

/* 统计网格 */
.stats-grid {
  display: flex;
  gap: 16rpx;
  margin-bottom: 20rpx;
}

.stat-item {
  flex: 1;
  background: white;
  border-radius: 16rpx;
  padding: 24rpx;
  text-align: center;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.stat-value {
  display: block;
  font-size: 40rpx;
  font-weight: bold;
  color: #3B82F6;
  margin-bottom: 8rpx;
}

.stat-label {
  display: block;
  font-size: 24rpx;
  color: #6B7280;
}

/* 功能入口卡片 */
.section-card {
  display: flex;
  align-items: center;
  gap: 20rpx;
  background: white;
  border-radius: 20rpx;
  padding: 32rpx;
  margin-bottom: 20rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
  transition: transform 0.2s;
}

.section-card:active {
  transform: scale(0.98);
}

.card-icon-area {
  width: 100rpx;
  height: 100rpx;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.interaction-card .card-icon-area {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.card-icon {
  font-size: 60rpx;
}

.card-content {
  flex: 1;
}

.card-title {
  display: block;
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
  margin-bottom: 8rpx;
}

.card-desc {
  display: block;
  font-size: 24rpx;
  color: #6B7280;
  margin-bottom: 12rpx;
}

.preview-tags {
  display: flex;
  gap: 12rpx;
}

.preview-tag {
  padding: 4rpx 12rpx;
  background: #EFF6FF;
  color: #3B82F6;
  border-radius: 8rpx;
  font-size: 20rpx;
}

.card-arrow {
  font-size: 48rpx;
  color: #D1D5DB;
}

/* 底部占位 */
.bottom-spacer {
  height: 40rpx;
}
</style>
