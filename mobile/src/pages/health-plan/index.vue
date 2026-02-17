<template>
  <view class="health-plan-page">
    <!-- 顶部导航 -->
    <view class="page-header">
      <text class="page-title">健康计划工坊</text>
      <text class="page-subtitle">AI 助力，科学管理</text>
    </view>

    <!-- 儿童模式：奶酪仓鼠风格 -->
    <view v-if="userRole === 'child_under_12'" class="child-plan-view">
      <!-- 顶部装饰 -->
      <view class="child-plan-header">
        <view class="header-deco">
          <text class="deco-star">✨</text>
          <text class="deco-star s2">⭐</text>
        </view>
        <view class="header-title-area">
          <text class="header-icon">📋</text>
          <text class="header-title">我的小任务</text>
        </view>
        <view class="level-badge-child">
          <text class="badge-icon">🏆</text>
          <text class="badge-text">Lv.{{ gamifiedView.level }}</text>
        </view>
      </view>

      <!-- 吉祥物鼓励卡片 -->
      <view class="mascot-encourage-card">
        <view class="mascot-left">
          <text class="mascot-face">🐹</text>
        </view>
        <view class="mascot-right">
          <view class="speech-box">
            <text class="speech-content">{{ encourageMessage }}</text>
          </view>
          <view class="progress-area">
            <text class="progress-label-child">今日进度</text>
            <view class="progress-bar-child">
              <view class="progress-fill-child" :style="{ width: todayCompletionRate + '%' }"></view>
            </view>
            <text class="progress-text-child">{{ todayCompletionRate }}%</text>
          </view>
        </view>
      </view>

      <!-- 勋章展示 -->
      <view v-if="gamifiedView.badges.length > 0" class="badges-card-child">
        <view class="badges-header">
          <text class="badges-title">🎖️ 我的勋章</text>
        </view>
        <view class="badges-grid">
          <view v-for="badge in gamifiedView.badges" :key="badge.name" class="badge-item-child">
            <text class="badge-emoji">{{ badge.icon }}</text>
            <text class="badge-name-child">{{ badge.name }}</text>
          </view>
        </view>
      </view>

      <!-- 今日任务列表 -->
      <view class="tasks-card-child">
        <view class="tasks-header-child">
          <text class="tasks-title-child">🎯 今日小挑战</text>
          <text class="tasks-count-child">{{ gamifiedView.progress }}/{{ gamifiedView.total }}</text>
        </view>
        <view class="tasks-list-child">
          <view 
            v-for="task in todayPendingTasks" 
            :key="task.id"
            class="task-item-child"
            @tap="completeChildTask(task)"
          >
            <view class="task-emoji-wrap">
              <text class="task-emoji-child">{{ getTaskEmoji(task.content) }}</text>
            </view>
            <view class="task-info-child">
              <text class="task-name-child">{{ simplifyTaskContent(task.content) }}</text>
              <text class="task-time-child">{{ formatTime(task.scheduled_time) }}</text>
            </view>
            <view class="task-action-child">
              <text class="action-icon">👆</text>
              <text class="action-text-child">完成</text>
            </view>
          </view>
          
          <!-- 已完成任务 -->
          <view 
            v-for="task in todayCompletedTasks" 
            :key="task.id"
            class="task-item-child done"
          >
            <view class="task-emoji-wrap done">
              <text class="task-emoji-child">✅</text>
            </view>
            <view class="task-info-child">
              <text class="task-name-child done">{{ simplifyTaskContent(task.content) }}</text>
              <text class="task-time-child">{{ formatTime(task.scheduled_time) }}</text>
            </view>
            <view class="task-reward-child">
              <text class="reward-star">⭐</text>
            </view>
          </view>
        </view>
        
        <!-- 空状态 -->
        <view v-if="todayTasks.length === 0" class="empty-child">
          <text class="empty-emoji">🎉</text>
          <text class="empty-text-child">今天没有任务啦</text>
          <text class="empty-hint-child">好好休息吧~</text>
        </view>
      </view>

      <!-- 底部装饰 -->
      <view class="child-footer">
        <text class="footer-cheese">🧀</text>
        <text class="footer-cheese">🧀</text>
        <text class="footer-cheese">🧀</text>
      </view>
    </view>

    <view v-else class="normal-view">
      <!-- 青少年/家属视图 -->
      
      <!-- 快速统计 -->
      <view class="stats-cards">
        <view class="stat-card">
          <text class="stat-value">{{ activePlans.length }}</text>
          <text class="stat-label">进行中</text>
        </view>
        <view class="stat-card">
          <text class="stat-value">{{ todayCompletionRate }}%</text>
          <text class="stat-label">今日完成</text>
        </view>
        <view v-if="userRole === 'guardian'" class="stat-card highlight">
          <text class="stat-value">{{ pendingPlans.length }}</text>
          <text class="stat-label">待审核</text>
        </view>
      </view>

      <!-- 今日任务时间轴 -->
      <view class="today-section">
        <view class="section-header">
          <text class="section-title">今日清单</text>
          <text class="section-date">{{ todayDate }}</text>
        </view>

        <view class="timeline">
          <!-- 待完成任务 -->
          <view 
            v-for="task in todayPendingTasks" 
            :key="task.id"
            class="timeline-item pending"
          >
            <view class="timeline-dot"></view>
            <view class="timeline-content">
              <view class="task-header">
                <text class="task-time">{{ formatTime(task.scheduled_time) }}</text>
                <view class="task-level" :class="'level-' + task.reminder_level">
                  {{ getLevelText(task.reminder_level) }}
                </view>
              </view>
              <text class="task-content">{{ task.content }}</text>
              <view class="task-actions">
                <button class="btn-complete" @tap="completeTask(task)">完成</button>
                <button class="btn-difficult" @tap="markDifficult(task)">太难了</button>
              </view>
            </view>
          </view>

          <!-- 已完成任务 -->
          <view 
            v-for="task in todayCompletedTasks" 
            :key="task.id"
            class="timeline-item completed"
          >
            <view class="timeline-dot checked"></view>
            <view class="timeline-content">
              <view class="task-header">
                <text class="task-time">{{ formatTime(task.scheduled_time) }}</text>
                <text class="completed-tag">✓ 已完成</text>
              </view>
              <text class="task-content">{{ task.content }}</text>
            </view>
          </view>

          <!-- 空状态 -->
          <view v-if="todayTasks.length === 0" class="empty-state">
            <text class="empty-icon">📋</text>
            <text class="empty-text">暂无任务</text>
            <text class="empty-hint">创建一个健康计划开始吧</text>
          </view>
        </view>
      </view>

      <!-- 我的计划列表 -->
      <view class="plans-section">
        <view class="section-header">
          <text class="section-title">我的计划</text>
          <text v-if="canCreatePlan" class="create-link" @tap="goToCreate">+ 新建</text>
        </view>

        <view class="plan-cards">
          <!-- 待审核计划（仅家属可见） -->
          <view 
            v-for="plan in pendingPlans" 
            :key="plan.id"
            class="plan-card pending"
            @tap="reviewPlan(plan)"
          >
            <view class="plan-header">
              <text class="plan-title">{{ plan.target_goal }}</text>
              <view class="plan-badge pending">待审核</view>
            </view>
            <text class="plan-type">{{ getPlanTypeText(plan.plan_type) }}</text>
            <text class="plan-date">创建于 {{ formatDate(plan.created_at) }}</text>
          </view>

          <!-- 进行中的计划 -->
          <view 
            v-for="plan in activePlans" 
            :key="plan.id"
            class="plan-card active"
            @tap="viewPlanDetail(plan)"
          >
            <view class="plan-header">
              <text class="plan-title">{{ plan.target_goal }}</text>
              <view class="plan-badge active">进行中</view>
            </view>
            <text class="plan-type">{{ getPlanTypeText(plan.plan_type) }}</text>
            <view class="plan-progress">
              <text class="progress-text">任务进度</text>
              <text class="progress-value">{{ calculatePlanProgress(plan) }}%</text>
            </view>
            <text class="plan-date">{{ formatDateRange(plan.start_date, plan.end_date) }}</text>
          </view>
        </view>
      </view>
    </view>

    <!-- 创建计划按钮（浮动） -->
    <view v-if="canCreatePlan && userRole !== 'child_under_12'" class="fab" @tap="goToCreate">
      <text class="fab-icon">+</text>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useHealthPlanStore } from '@/store/healthPlan'
import { storeToRefs } from 'pinia'

const healthPlanStore = useHealthPlanStore()
const {
  userRole,
  todayTasks,
  activePlans,
  pendingPlans,
  todayPendingTasks,
  todayCompletedTasks,
  todayCompletionRate,
  canCreatePlan,
  gamifiedView
} = storeToRefs(healthPlanStore)

// 鼓励消息
const encourageMessage = computed(() => {
  const rate = todayCompletionRate.value
  if (rate === 100) return '太棒了！今天的任务全部完成啦！🎉'
  if (rate >= 80) return '就快完成了，加油！你是最棒的！💪'
  if (rate >= 50) return '已经完成一半啦，继续努力哦~'
  if (rate > 0) return '开始做任务啦，小仓鼠为你加油！'
  return '新的一天开始了，一起完成小任务吧！'
})

// 今日日期
const todayDate = computed(() => {
  const today = new Date()
  const month = today.getMonth() + 1
  const day = today.getDate()
  const weekdays = ['日', '一', '二', '三', '四', '五', '六']
  const weekday = weekdays[today.getDay()]
  
  return `${month}月${day}日 星期${weekday}`
})

// 计划类型文本
const getPlanTypeText = (type) => {
  const map = {
    1: '用药计划',
    2: '复查计划',
    3: '饮食计划',
    4: '运动计划'
  }
  return map[type] || '健康计划'
}

// 提醒级别文本
const getLevelText = (level) => {
  const map = {
    1: '普通',
    2: '重要',
    3: '紧急'
  }
  return map[level] || '普通'
}

// 格式化时间
const formatTime = (date) => {
  const d = new Date(date)
  const hours = d.getHours().toString().padStart(2, '0')
  const minutes = d.getMinutes().toString().padStart(2, '0')
  return `${hours}:${minutes}`
}

// 格式化日期
const formatDate = (date) => {
  const d = new Date(date)
  const month = d.getMonth() + 1
  const day = d.getDate()
  return `${month}月${day}日`
}

// 格式化日期范围
const formatDateRange = (start, end) => {
  return `${formatDate(start)} - ${formatDate(end)}`
}

// 计算计划进度
const calculatePlanProgress = (plan) => {
  const completed = todayCompletedTasks.value.filter(t => t.plan_id === plan.id).length
  const total = todayTasks.value.filter(t => t.plan_id === plan.id).length
  
  if (total === 0) return 0
  return Math.round((completed / total) * 100)
}

// 完成任务
const completeTask = (task) => {
  // 如果任务需要输入数据（如血糖值）
  if (task.content.includes('监测血糖') || task.content.includes('测血糖')) {
    uni.showModal({
      title: '记录血糖值',
      editable: true,
      placeholderText: '请输入血糖值',
      success: (res) => {
        if (res.confirm && res.content) {
          healthPlanStore.completeTask(task.id, {
            glucose_value: parseFloat(res.content)
          })
          
          // 撒花特效
          showCelebration()
        }
      }
    })
  } else {
    healthPlanStore.completeTask(task.id)
    showCelebration()
  }
}

// 儿童模式完成任务
const completeChildTask = (task) => {
  healthPlanStore.completeTask(task.id)
  showCelebration()
  
  // 检查是否获得新勋章
  const badges = gamifiedView.value.badges
  if (badges.length > 0) {
    const latestBadge = badges[badges.length - 1]
    uni.showToast({
      title: `获得勋章：${latestBadge.name}`,
      icon: 'success',
      duration: 2000
    })
  }
}

// 标记任务太难
const markDifficult = (task) => {
  uni.showModal({
    title: '任务反馈',
    content: '这个任务对你来说太难了吗？我们会调整难度。',
    confirmText: '是的',
    cancelText: '取消',
    success: (res) => {
      if (res.confirm) {
        healthPlanStore.feedbackTaskDifficulty(task.id, 2)
        
        uni.showToast({
          title: '已记录反馈，下次会调整',
          icon: 'none'
        })
      }
    }
  })
}

// 撒花特效
const showCelebration = () => {
  uni.showToast({
    title: '太棒了！',
    icon: 'success'
  })
}

// 简化任务内容（儿童模式）
const simplifyTaskContent = (content) => {
  const map = {
    '监测血糖': '测一测',
    '快走': '去散步',
    '胰岛素': '打针针',
    '补充水分': '喝水水'
  }
  
  for (const [key, value] of Object.entries(map)) {
    if (content.includes(key)) {
      return value
    }
  }
  
  return content
}

// 获取任务表情
const getTaskEmoji = (content) => {
  if (content.includes('监测') || content.includes('测')) return '🩺'
  if (content.includes('运动') || content.includes('散步') || content.includes('快走')) return '🏃'
  if (content.includes('胰岛素') || content.includes('用药')) return '💉'
  if (content.includes('饮食') || content.includes('餐')) return '🍽️'
  if (content.includes('水')) return '💧'
  return '✨'
}

// 跳转到创建页面
const goToCreate = () => {
  uni.navigateTo({
    url: '/pages/health-plan/create'
  })
}

// 查看计划详情
const viewPlanDetail = (plan) => {
  uni.navigateTo({
    url: `/pages/health-plan/detail?id=${plan.id}`
  })
}

// 审核计划
const reviewPlan = (plan) => {
  uni.navigateTo({
    url: `/pages/health-plan/review?id=${plan.id}`
  })
}

onMounted(() => {
  // 生成模拟数据
  if (healthPlanStore.plans.length === 0) {
    healthPlanStore.generateMockData()
  }
})
</script>

<style scoped>
.health-plan-page {
  min-height: 100vh;
  background: #F3F4F6;
  padding: 20rpx;
  padding-bottom: 120rpx;
}

/* 页面头部 */
.page-header {
  padding: 40rpx 20rpx;
  text-align: center;
}

.page-title {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: #1F2937;
  margin-bottom: 8rpx;
}

.page-subtitle {
  display: block;
  font-size: 28rpx;
  color: #9CA3AF;
}

/* 儿童游戏化视图 */
.child-view {
  padding: 20rpx;
}

.game-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.level-badge {
  display: flex;
  align-items: center;
  gap: 12rpx;
  padding: 16rpx 32rpx;
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
  border-radius: 40rpx;
}

.level-icon {
  font-size: 40rpx;
}

.level-text {
  font-size: 32rpx;
  font-weight: bold;
  color: white;
}

.progress-info {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.progress-text {
  font-size: 24rpx;
  color: #6B7280;
}

.progress-value {
  font-size: 36rpx;
  font-weight: bold;
  color: #1F2937;
}

.progress-bar-container {
  margin-bottom: 32rpx;
}

.progress-bar {
  height: 40rpx;
  background: #E5E7EB;
  border-radius: 20rpx;
  overflow: hidden;
  margin-bottom: 12rpx;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #10B981 0%, #059669 100%);
  transition: width 0.5s ease;
}

.progress-label {
  display: block;
  text-align: right;
  font-size: 28rpx;
  font-weight: bold;
  color: #10B981;
}

/* 勋章 */
.badges-section {
  margin-bottom: 32rpx;
}

.badges-list {
  display: flex;
  gap: 16rpx;
  flex-wrap: wrap;
}

.badge-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20rpx;
  background: white;
  border-radius: 16rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.1);
}

.badge-icon {
  font-size: 60rpx;
  margin-bottom: 8rpx;
}

.badge-name {
  font-size: 24rpx;
  color: #6B7280;
}

/* 任务卡片（儿童模式） */
.task-card.child-mode {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 24rpx;
  background: white;
  border-radius: 20rpx;
  margin-bottom: 16rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);
}

.task-icon {
  font-size: 60rpx;
}

.task-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.action-btn {
  width: 80rpx;
  height: 80rpx;
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48rpx;
  font-weight: bold;
}

/* 正常视图 */
.normal-view {
  padding: 20rpx;
}

/* 统计卡片 */
.stats-cards {
  display: flex;
  gap: 16rpx;
  margin-bottom: 32rpx;
}

.stat-card {
  flex: 1;
  padding: 32rpx;
  background: white;
  border-radius: 16rpx;
  text-align: center;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.stat-card.highlight {
  background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%);
  border: 2rpx solid #3B82F6;
}

.stat-value {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: #1F2937;
  margin-bottom: 8rpx;
}

.stat-label {
  display: block;
  font-size: 24rpx;
  color: #6B7280;
}

/* 区块 */
.today-section,
.plans-section,
.tasks-section {
  margin-bottom: 32rpx;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
}

.section-date {
  font-size: 24rpx;
  color: #9CA3AF;
}

.create-link {
  font-size: 28rpx;
  color: #3B82F6;
  font-weight: 500;
}

/* 时间轴 */
.timeline {
  background: white;
  border-radius: 16rpx;
  padding: 32rpx;
}

.timeline-item {
  position: relative;
  padding-left: 60rpx;
  padding-bottom: 40rpx;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-item::before {
  content: '';
  position: absolute;
  left: 16rpx;
  top: 32rpx;
  bottom: -8rpx;
  width: 2rpx;
  background: #E5E7EB;
}

.timeline-item:last-child::before {
  display: none;
}

.timeline-dot {
  position: absolute;
  left: 8rpx;
  top: 8rpx;
  width: 20rpx;
  height: 20rpx;
  background: #3B82F6;
  border-radius: 50%;
  border: 4rpx solid white;
  box-shadow: 0 0 0 2rpx #3B82F6;
}

.timeline-dot.checked {
  background: #10B981;
  box-shadow: 0 0 0 2rpx #10B981;
}

.timeline-content {
  background: #F9FAFB;
  padding: 20rpx;
  border-radius: 12rpx;
}

.timeline-item.completed .timeline-content {
  opacity: 0.6;
}

.task-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.task-time {
  font-size: 28rpx;
  font-weight: bold;
  color: #1F2937;
}

.task-level {
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  font-size: 20rpx;
  color: white;
}

.task-level.level-1 {
  background: #9CA3AF;
}

.task-level.level-2 {
  background: #F59E0B;
}

.task-level.level-3 {
  background: #EF4444;
}

.completed-tag {
  font-size: 24rpx;
  color: #10B981;
  font-weight: 500;
}

.task-content {
  display: block;
  font-size: 28rpx;
  color: #374151;
  margin-bottom: 16rpx;
}

.task-actions {
  display: flex;
  gap: 12rpx;
}

.btn-complete,
.btn-difficult {
  flex: 1;
  height: 64rpx;
  border-radius: 8rpx;
  font-size: 24rpx;
  border: none;
}

.btn-complete {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  color: white;
}

.btn-difficult {
  background: #F3F4F6;
  color: #6B7280;
}

/* 计划卡片 */
.plan-cards {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.plan-card {
  padding: 32rpx;
  background: white;
  border-radius: 16rpx;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.plan-card.pending {
  border-left: 8rpx solid #F59E0B;
}

.plan-card.active {
  border-left: 8rpx solid #10B981;
}

.plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12rpx;
}

.plan-title {
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
}

.plan-badge {
  padding: 8rpx 16rpx;
  border-radius: 12rpx;
  font-size: 22rpx;
  color: white;
}

.plan-badge.pending {
  background: #F59E0B;
}

.plan-badge.active {
  background: #10B981;
}

.plan-type {
  display: block;
  font-size: 24rpx;
  color: #6B7280;
  margin-bottom: 8rpx;
}

.plan-progress {
  display: flex;
  justify-content: space-between;
  margin: 12rpx 0;
}

.plan-date {
  display: block;
  font-size: 22rpx;
  color: #9CA3AF;
  margin-top: 8rpx;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 80rpx 20rpx;
}

.empty-icon {
  font-size: 100rpx;
  display: block;
  margin-bottom: 20rpx;
}

.empty-text {
  display: block;
  font-size: 32rpx;
  color: #6B7280;
  margin-bottom: 8rpx;
}

.empty-hint {
  display: block;
  font-size: 24rpx;
  color: #9CA3AF;
}

/* 浮动按钮 */
.fab {
  position: fixed;
  bottom: 100rpx;
  right: 40rpx;
  width: 120rpx;
  height: 120rpx;
  background: linear-gradient(135deg, #3B82F6 0%, #2563EB 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 24rpx rgba(59, 130, 246, 0.4);
  z-index: 100;
}

.fab-icon {
  font-size: 60rpx;
  color: white;
  font-weight: bold;
}

/* ========== 儿童模式 - 奶酪仓鼠风格 ========== */
.child-plan-view {
  padding: 0 20rpx;
}

.health-plan-page:has(.child-plan-view) {
  background: linear-gradient(180deg, #FEF7ED 0%, #FFF8E7 50%, #FFFBF0 100%);
}

.health-plan-page:has(.child-plan-view) .page-header {
  background: transparent;
}

.health-plan-page:has(.child-plan-view) .page-title {
  color: #602F27;
}

.health-plan-page:has(.child-plan-view) .page-subtitle {
  color: #A85835;
}

.child-plan-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24rpx;
}

.header-deco {
  display: flex;
  gap: 8rpx;
}

.deco-star {
  font-size: 32rpx;
  animation: twinkle 2s ease-in-out infinite;
}

.deco-star.s2 {
  animation-delay: 1s;
}

@keyframes twinkle {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}

.header-title-area {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.header-icon {
  font-size: 40rpx;
}

.header-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #602F27;
}

.level-badge-child {
  display: flex;
  align-items: center;
  gap: 8rpx;
  background: linear-gradient(135deg, #D5A874 0%, #CB8E54 100%);
  padding: 12rpx 20rpx;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 12rpx rgba(203, 142, 84, 0.3);
}

.level-badge-child .badge-icon {
  font-size: 28rpx;
}

.level-badge-child .badge-text {
  font-size: 26rpx;
  font-weight: bold;
  color: white;
}

/* 吉祥物鼓励卡片 */
.mascot-encourage-card {
  display: flex;
  gap: 20rpx;
  background: white;
  border-radius: 32rpx;
  padding: 28rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 6rpx 24rpx rgba(96, 47, 39, 0.1);
  border: 3rpx solid #E3C7A4;
}

.mascot-left {
  flex-shrink: 0;
}

.mascot-face {
  font-size: 80rpx;
  display: block;
  animation: bounce 2s ease-in-out infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-12rpx); }
}

.mascot-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.speech-box {
  background: linear-gradient(135deg, #FAF6F0 0%, #F2E5D3 100%);
  border: 2rpx solid #E3C7A4;
  border-radius: 16rpx;
  padding: 16rpx 20rpx;
  position: relative;
}

.speech-box::before {
  content: '';
  position: absolute;
  left: -16rpx;
  top: 50%;
  transform: translateY(-50%);
  border-top: 12rpx solid transparent;
  border-bottom: 12rpx solid transparent;
  border-right: 16rpx solid #E3C7A4;
}

.speech-content {
  font-size: 26rpx;
  color: #602F27;
  line-height: 1.5;
}

.progress-area {
  display: flex;
  align-items: center;
  gap: 12rpx;
}

.progress-label-child {
  font-size: 24rpx;
  color: #74362C;
  flex-shrink: 0;
}

.progress-bar-child {
  flex: 1;
  height: 24rpx;
  background: #E3C7A4;
  border-radius: 12rpx;
  overflow: hidden;
}

.progress-fill-child {
  height: 100%;
  background: linear-gradient(90deg, #4ADE80 0%, #22C55E 100%);
  border-radius: 12rpx;
  transition: width 0.5s ease;
}

.progress-text-child {
  font-size: 26rpx;
  font-weight: bold;
  color: #22C55E;
  flex-shrink: 0;
}

/* 勋章卡片 */
.badges-card-child {
  background: white;
  border-radius: 28rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 6rpx 24rpx rgba(96, 47, 39, 0.08);
  border: 3rpx solid #E3C7A4;
}

.badges-header {
  margin-bottom: 20rpx;
}

.badges-title {
  font-size: 30rpx;
  font-weight: bold;
  color: #602F27;
}

.badges-grid {
  display: flex;
  gap: 16rpx;
  flex-wrap: wrap;
}

.badge-item-child {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 16rpx 20rpx;
  background: linear-gradient(135deg, #FAF6F0 0%, #F2E5D3 100%);
  border-radius: 16rpx;
  border: 2rpx solid #D5A874;
}

.badge-emoji {
  font-size: 48rpx;
  margin-bottom: 8rpx;
}

.badge-name-child {
  font-size: 22rpx;
  color: #8E422F;
}

/* 任务卡片 */
.tasks-card-child {
  background: white;
  border-radius: 28rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  box-shadow: 0 6rpx 24rpx rgba(96, 47, 39, 0.08);
  border: 3rpx solid #E3C7A4;
}

.tasks-header-child {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20rpx;
}

.tasks-title-child {
  font-size: 30rpx;
  font-weight: bold;
  color: #602F27;
}

.tasks-count-child {
  font-size: 28rpx;
  font-weight: 600;
  color: #A85835;
}

.tasks-list-child {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
}

.task-item-child {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 20rpx;
  background: #FAF6F0;
  border-radius: 20rpx;
  border: 2rpx solid #E3C7A4;
  transition: all 0.3s ease;
}

.task-item-child:active {
  transform: scale(0.98);
  background: #F2E5D3;
}

.task-item-child.done {
  background: linear-gradient(135deg, #F0FFF0 0%, #E8FFE8 100%);
  border-color: #90EE90;
}

.task-emoji-wrap {
  width: 64rpx;
  height: 64rpx;
  background: linear-gradient(135deg, #E3C7A4 0%, #D5A874 100%);
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.task-emoji-wrap.done {
  background: linear-gradient(135deg, #90EE90 0%, #4ADE80 100%);
}

.task-emoji-child {
  font-size: 36rpx;
}

.task-info-child {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 4rpx;
}

.task-name-child {
  font-size: 28rpx;
  font-weight: 500;
  color: #602F27;
}

.task-name-child.done {
  color: #22C55E;
  text-decoration: line-through;
}

.task-time-child {
  font-size: 24rpx;
  color: #A85835;
}

.task-action-child {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;
  padding: 12rpx 16rpx;
  background: linear-gradient(135deg, #4ADE80 0%, #22C55E 100%);
  border-radius: 16rpx;
}

.action-icon {
  font-size: 28rpx;
}

.action-text-child {
  font-size: 22rpx;
  color: white;
  font-weight: 500;
}

.task-reward-child {
  padding: 12rpx;
}

.reward-star {
  font-size: 40rpx;
  animation: starPop 0.5s ease;
}

@keyframes starPop {
  0% { transform: scale(0); }
  50% { transform: scale(1.3); }
  100% { transform: scale(1); }
}

/* 空状态 */
.empty-child {
  text-align: center;
  padding: 60rpx 20rpx;
}

.empty-emoji {
  font-size: 80rpx;
  display: block;
  margin-bottom: 16rpx;
}

.empty-text-child {
  display: block;
  font-size: 30rpx;
  color: #602F27;
  margin-bottom: 8rpx;
}

.empty-hint-child {
  display: block;
  font-size: 26rpx;
  color: #A85835;
}

/* 底部装饰 */
.child-footer {
  display: flex;
  justify-content: center;
  gap: 48rpx;
  padding: 20rpx 0;
  opacity: 0.5;
}

.footer-cheese {
  font-size: 48rpx;
  animation: float 3s ease-in-out infinite;
}

.footer-cheese:nth-child(2) {
  animation-delay: 1s;
}

.footer-cheese:nth-child(3) {
  animation-delay: 2s;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-16rpx); }
}
</style>
