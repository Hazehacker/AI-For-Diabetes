<template>
  <view class="health-plan-page" :class="{ 'child-mode-page': isChildMode }">
    <!-- 儿童模式自定义导航栏 -->
    <view v-if="isChildMode" class="child-nav-bar">
      <image class="child-nav-back" src="/static/ch/ch_fr_return.png" mode="aspectFit" @tap="goBack"></image>
      <text class="child-nav-title">健康计划工坊</text>
      <view class="child-nav-placeholder"></view>
    </view>

    <!-- 顶部导航（非儿童模式） -->
    <view v-if="!isChildMode" class="page-header">
      <text class="page-title">健康计划工坊</text>
      <text class="page-subtitle">AI 助力，科学管理</text>
    </view>

    <!-- 主内容区域（所有模式共用，样式根据模式不同） -->
    <view class="main-content" :class="{ 'child-content': isChildMode }">
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
    <view v-if="canCreatePlan" class="fab" :class="{ 'child-fab': isChildMode }" @tap="goToCreate">
      <text class="fab-icon">+</text>
    </view>

    <!-- 儿童模式自定义弹窗 - 记录血糖值 -->
    <view v-if="isChildMode && showGlucoseModal" class="child-modal-overlay" @tap="closeGlucoseModal">
      <view class="child-modal" @tap.stop>
        <view class="child-modal-header">
          <text class="child-modal-title">记录血糖值</text>
        </view>
        <view class="child-modal-body">
          <input 
            class="child-modal-input" 
            type="digit" 
            v-model="glucoseValue" 
            placeholder="请输入血糖值"
          />
        </view>
        <view class="child-modal-footer">
          <view class="child-modal-btn cancel" @tap="closeGlucoseModal">取消</view>
          <view class="child-modal-btn confirm" @tap="confirmGlucose">确定</view>
        </view>
      </view>
    </view>

    <!-- 儿童模式自定义弹窗 - 任务反馈 -->
    <view v-if="isChildMode && showFeedbackModal" class="child-modal-overlay" @tap="closeFeedbackModal">
      <view class="child-modal" @tap.stop>
        <view class="child-modal-header">
          <text class="child-modal-title">任务反馈</text>
        </view>
        <view class="child-modal-body">
          <text class="child-modal-text">这个任务对你来说太难了吗？我们会调整难度。</text>
        </view>
        <view class="child-modal-footer">
          <view class="child-modal-btn cancel" @tap="closeFeedbackModal">取消</view>
          <view class="child-modal-btn confirm" @tap="confirmFeedback">是的</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useHealthPlanStore } from '@/store/healthPlan'
import { useDashboardStore } from '@/store/dashboard'
import { storeToRefs } from 'pinia'

const healthPlanStore = useHealthPlanStore()
const dashboardStore = useDashboardStore()

// 从 dashboardStore 获取实际的用户角色
const { userRole } = storeToRefs(dashboardStore)
const isChildMode = computed(() => userRole.value === 'child_under_12')

// 监听 userRole 变化，同步到 healthPlanStore
watch(userRole, (newRole) => {
  healthPlanStore.setUserRole(newRole)
}, { immediate: true })

const {
  todayTasks,
  activePlans,
  pendingPlans,
  todayPendingTasks,
  todayCompletedTasks,
  todayCompletionRate,
  canCreatePlan,
  gamifiedView
} = storeToRefs(healthPlanStore)

// 儿童模式弹窗状态
const showGlucoseModal = ref(false)
const showFeedbackModal = ref(false)
const glucoseValue = ref('')
const currentTaskForModal = ref(null)

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
    // 儿童模式使用自定义弹窗
    if (isChildMode.value) {
      currentTaskForModal.value = task
      glucoseValue.value = ''
      showGlucoseModal.value = true
    } else {
      uni.showModal({
        title: '记录血糖值',
        editable: true,
        placeholderText: '请输入血糖值',
        success: (res) => {
          if (res.confirm && res.content) {
            healthPlanStore.completeTask(task.id, {
              glucose_value: parseFloat(res.content)
            })
            showCelebration()
          }
        }
      })
    }
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
  // 儿童模式使用自定义弹窗
  if (isChildMode.value) {
    currentTaskForModal.value = task
    showFeedbackModal.value = true
  } else {
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
}

// 儿童模式弹窗方法
const closeGlucoseModal = () => {
  showGlucoseModal.value = false
  glucoseValue.value = ''
  currentTaskForModal.value = null
}

const confirmGlucose = () => {
  if (glucoseValue.value && currentTaskForModal.value) {
    healthPlanStore.completeTask(currentTaskForModal.value.id, {
      glucose_value: parseFloat(glucoseValue.value)
    })
    showCelebration()
  }
  closeGlucoseModal()
}

const closeFeedbackModal = () => {
  showFeedbackModal.value = false
  currentTaskForModal.value = null
}

const confirmFeedback = () => {
  if (currentTaskForModal.value) {
    healthPlanStore.feedbackTaskDifficulty(currentTaskForModal.value.id, 2)
    uni.showToast({
      title: '已记录反馈，下次会调整',
      icon: 'none'
    })
  }
  closeFeedbackModal()
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

// 返回
const goBack = () => {
  const pages = getCurrentPages()
  if (pages.length > 1) {
    uni.navigateBack({ delta: 1 })
  } else {
    uni.switchTab({ url: '/pages/index/index' })
  }
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

/* 儿童模式页面背景 */
.health-plan-page.child-mode-page {
  background: linear-gradient(180deg, #FEF7ED 0%, #FFF8E7 50%, #FFFBF0 100%);
  padding: 0;
  padding-bottom: 120rpx;
}

/* 儿童模式导航栏 */
.child-nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16rpx 24rpx;
  padding-top: calc(env(safe-area-inset-top) + 16rpx);
  background: #FFFEF7;
  border-bottom: 1rpx solid #E3C7A4;
  box-shadow: 0 2rpx 8rpx rgba(203, 142, 84, 0.1);
}

.child-nav-back {
  width: 64rpx;
  height: 64rpx;
  display: block;
  padding: 10rpx;
  cursor: pointer;
  z-index: 100;
  position: relative;
}

.child-nav-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #602F27;
}

.child-nav-placeholder {
  width: 64rpx;
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

/* ========== 儿童模式样式覆盖 ========== */
.child-content {
  padding: 20rpx 24rpx;
}

/* 儿童模式统计卡片 */
.child-content .stat-card {
  background: white;
  border: 3rpx solid #E3C7A4;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 0 #D5A874;
}

.child-content .stat-value {
  color: #602F27;
}

.child-content .stat-label {
  color: #A85835;
}

.child-content .stat-card.highlight {
  background: #FFF8E7;
  border-color: #E3C7A4;
}

/* 儿童模式区块标题 */
.child-content .section-title {
  color: #602F27;
}

.child-content .section-date {
  color: #A85835;
}

.child-content .create-link {
  color: #CB8E54;
  font-weight: 600;
}

/* 儿童模式时间轴 */
.child-content .timeline {
  background: white;
  border: 3rpx solid #E3C7A4;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 12rpx rgba(96, 47, 39, 0.08);
}

.child-content .timeline-dot {
  background: #F6CD75;
  box-shadow: 0 0 0 2rpx #E5BC64;
}

.child-content .timeline-dot.checked {
  background: #90C67C;
  box-shadow: 0 0 0 2rpx #7AB368;
}

.child-content .timeline-content {
  background: #FFF8E7;
  border: 2rpx solid #E3C7A4;
  border-radius: 20rpx;
}

.child-content .task-time {
  color: #602F27;
}

.child-content .task-level {
  border-radius: 16rpx;
}

.child-content .task-level.level-1 {
  background: #E3C7A4;
  color: #602F27;
}

.child-content .task-level.level-2 {
  background: #F6CD75;
  color: #602F27;
}

.child-content .task-level.level-3 {
  background: #CB8E54;
  color: white;
}

.child-content .task-content {
  color: #602F27;
}

.child-content .btn-complete {
  background: #F6CD75;
  color: #602F27;
  border: 3rpx solid #E5BC64;
  box-shadow: 0 4rpx 0 #D4AB53;
  border-radius: 20rpx;
  font-weight: 600;
}

.child-content .btn-difficult {
  background: white;
  color: #A85835;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 4rpx 0 #D5C4B0;
  border-radius: 20rpx;
  font-weight: 600;
}

.child-content .completed-tag {
  color: #7AB368;
  font-weight: 600;
}

/* 儿童模式计划卡片 */
.child-content .plan-card {
  background: white;
  border: 3rpx solid #E3C7A4;
  border-radius: 24rpx;
  box-shadow: 0 4rpx 12rpx rgba(96, 47, 39, 0.08);
}

.child-content .plan-card.pending {
  border-left: 8rpx solid #F6CD75;
}

.child-content .plan-card.active {
  border-left: 8rpx solid #90C67C;
}

.child-content .plan-title {
  color: #602F27;
}

.child-content .plan-badge {
  border-radius: 16rpx;
  font-weight: 600;
}

.child-content .plan-badge.pending {
  background: #F6CD75;
  color: #602F27;
}

.child-content .plan-badge.active {
  background: #90C67C;
  color: white;
}

.child-content .plan-type {
  color: #A85835;
}

.child-content .plan-date {
  color: #CB8E54;
}

.child-content .progress-text {
  color: #A85835;
}

.child-content .progress-value {
  color: #602F27;
}

/* 儿童模式空状态 */
.child-content .empty-state {
  background: white;
  border: 3rpx solid #E3C7A4;
  border-radius: 24rpx;
  margin: 20rpx 0;
}

.child-content .empty-text {
  color: #602F27;
}

.child-content .empty-hint {
  color: #A85835;
}

/* 儿童模式浮动按钮 */
.fab.child-fab {
  background: #F6CD75;
  border: 4rpx solid #E5BC64;
  box-shadow: 0 6rpx 0 #D4AB53;
}

.fab.child-fab .fab-icon {
  color: #602F27;
}

/* 儿童模式自定义弹窗 */
.child-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 40rpx;
}

.child-modal {
  width: 100%;
  max-width: 560rpx;
  background: white;
  border-radius: 32rpx;
  border: 4rpx solid #E3C7A4;
  box-shadow: 0 8rpx 0 #D5A874;
  overflow: hidden;
}

.child-modal-header {
  padding: 32rpx;
  text-align: center;
  border-bottom: 2rpx solid #F2E5D3;
}

.child-modal-title {
  font-size: 34rpx;
  font-weight: 700;
  color: #602F27;
}

.child-modal-body {
  padding: 32rpx;
}

.child-modal-input {
  width: 100%;
  height: 88rpx;
  padding: 0 24rpx;
  background: #FFF8E7;
  border: 3rpx solid #E3C7A4;
  border-radius: 20rpx;
  font-size: 30rpx;
  color: #602F27;
  box-sizing: border-box;
}

.child-modal-input::placeholder {
  color: #CB8E54;
}

.child-modal-text {
  display: block;
  font-size: 28rpx;
  color: #602F27;
  line-height: 1.6;
  text-align: center;
}

.child-modal-footer {
  display: flex;
  border-top: 2rpx solid #F2E5D3;
}

.child-modal-btn {
  flex: 1;
  height: 96rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32rpx;
  font-weight: 600;
}

.child-modal-btn.cancel {
  color: #A85835;
  background: white;
  border-right: 2rpx solid #F2E5D3;
}

.child-modal-btn.confirm {
  color: #602F27;
  background: #F6CD75;
}

.child-modal-btn:active {
  opacity: 0.8;
}
</style>
