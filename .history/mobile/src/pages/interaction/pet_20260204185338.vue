<template>
  <view class="pet-page">
    <!-- 宠物展示区 -->
    <view class="pet-display">
      <view class="pet-avatar" :class="'stage-' + pet.stage">
        <text class="pet-emoji">{{ currentPetStage.emoji }}</text>
      </view>
      <text class="pet-name">{{ pet.name }}</text>
      <text class="pet-stage-name">{{ currentPetStage.name }}</text>
      
      <!-- 成长进度条 -->
      <view class="progress-section">
        <view class="progress-header">
          <text class="progress-label">成长进度</text>
          <text class="progress-value">{{ pet.progress }}%</text>
        </view>
        <view class="progress-bar">
          <view class="progress-fill" :style="{ width: pet.progress + '%' }"></view>
        </view>
      </view>
    </view>

    <!-- 统计信息 -->
    <view class="stats-section">
      <view class="stat-card">
        <text class="stat-icon">🔥</text>
        <text class="stat-value">{{ pet.streak_days }}</text>
        <text class="stat-label">连续天数</text>
      </view>
      <view class="stat-card">
        <text class="stat-icon">📅</text>
        <text class="stat-value">{{ pet.total_days }}</text>
        <text class="stat-label">累计天数</text>
      </view>
      <view class="stat-card">
        <text class="stat-icon">⭐</text>
        <text class="stat-value">{{ nextStageInfo }}</text>
        <text class="stat-label">距离升级</text>
      </view>
    </view>

    <!-- 今日任务 -->
    <view class="tasks-section">
      <text class="section-title">今日管理任务</text>
      <view class="tasks-list">
        <view 
          v-for="(task, key) in tasksList" 
          :key="key"
          class="task-item"
          :class="{ completed: todayBehaviors[key] }"
          @tap="completeTask(key)"
        >
          <view class="task-checkbox">
            <text v-if="todayBehaviors[key]" class="check-icon">✓</text>
          </view>
          <view class="task-info">
            <text class="task-name">{{ task.name }}</text>
            <text class="task-desc">{{ task.desc }}</text>
          </view>
          <text class="task-emoji">{{ task.emoji }}</text>
        </view>
      </view>

      <!-- 完成度提示 -->
      <view class="completion-hint">
        <text class="hint-text">
          {{ isTodayCompleted ? '✨ 今日任务已完成！糖小怪很开心' : `还有 ${remainingTasks} 个任务待完成` }}
        </text>
      </view>
    </view>

    <!-- 喂养按钮 -->
    <view v-if="isTodayCompleted && !isTodayFed" class="feed-section">
      <button class="feed-btn" @tap="feedPet">
        <text class="btn-icon">🍖</text>
        <text class="btn-text">喂养糖小怪</text>
      </button>
    </view>

    <!-- 成长阶段说明 -->
    <view class="stages-section">
      <text class="section-title">成长阶段</text>
      <view class="stages-list">
        <view 
          v-for="stage in petStages" 
          :key="stage.stage"
          class="stage-item"
          :class="{ 
            current: stage.stage === pet.stage,
            unlocked: stage.stage <= pet.stage 
          }"
        >
          <text class="stage-emoji">{{ stage.emoji }}</text>
          <text class="stage-name">{{ stage.name }}</text>
          <text class="stage-days">{{ stage.requiredDays }}天</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useInteractionStore } from '@/store/interaction'
import { storeToRefs } from 'pinia'

const interactionStore = useInteractionStore()
const { 
  pet, 
  todayBehaviors, 
  currentPetStage, 
  nextPetStage,
  petStages,
  isTodayCompleted,
  daysToNextStage
} = storeToRefs(interactionStore)

// 任务列表定义
const tasksList = {
  glucose_check: {
    name: '血糖监测',
    desc: '记录今日血糖数据',
    emoji: '🩺'
  },
  meal_record: {
    name: '饮食记录',
    desc: '记录今日饮食情况',
    emoji: '🍽️'
  },
  exercise: {
    name: '运动打卡',
    desc: '完成今日运动计划',
    emoji: '🏃'
  },
  medication: {
    name: '用药记录',
    desc: '按时服用/注射药物',
    emoji: '💊'
  }
}

// 剩余任务数
const remainingTasks = computed(() => {
  return Object.values(todayBehaviors.value).filter(b => !b).length
})

// 今日是否已喂养
const isTodayFed = computed(() => {
  const today = new Date().toDateString()
  return pet.value.last_feed_date === today
})

// 下一阶段信息
const nextStageInfo = computed(() => {
  if (!nextPetStage.value) return '已满级'
  return `${daysToNextStage.value}天`
})

// 完成任务
const completeTask = (taskKey) => {
  if (todayBehaviors.value[taskKey]) {
    uni.showToast({
      title: '今日已完成',
      icon: 'none'
    })
    return
  }
  
  interactionStore.recordBehavior(taskKey)
  
  uni.showToast({
    title: '任务完成！',
    icon: 'success'
  })
  
  // 检查是否全部完成
  if (isTodayCompleted.value && !isTodayFed.value) {
    setTimeout(() => {
      uni.showModal({
        title: '太棒了！',
        content: '今日任务全部完成，快去喂养糖小怪吧！',
        showCancel: false
      })
    }, 500)
  }
}

// 喂养宠物
const feedPet = () => {
  const result = interactionStore.feedPet()
  
  if (result.success) {
    uni.showToast({
      title: result.message,
      icon: 'success',
      duration: 2000
    })
    
    // 检查是否升级
    if (pet.value.progress === 0) {
      setTimeout(() => {
        uni.showModal({
          title: '🎉 恭喜升级！',
          content: `糖小怪进化成了 ${currentPetStage.value.name}！`,
          showCancel: false
        })
      }, 1000)
    }
  } else {
    uni.showToast({
      title: result.message,
      icon: 'none'
    })
  }
}
</script>

<style scoped>
.pet-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #FCD34D 0%, #F59E0B 30%, #F3F4F6 30%);
  padding: 20rpx;
  padding-bottom: 120rpx;
}

/* 宠物展示区 */
.pet-display {
  text-align: center;
  padding: 40rpx 20rpx;
  margin-bottom: 32rpx;
}

.pet-avatar {
  width: 280rpx;
  height: 280rpx;
  margin: 0 auto 24rpx;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 8rpx 32rpx rgba(245, 158, 11, 0.3);
  animation: float 3s ease-in-out infinite;
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20rpx); }
}

.pet-emoji {
  font-size: 160rpx;
}

.pet-name {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: white;
  margin-bottom: 8rpx;
}

.pet-stage-name {
  display: block;
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: 32rpx;
}

.progress-section {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10rpx);
  border-radius: 16rpx;
  padding: 24rpx;
}

.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12rpx;
}

.progress-label {
  font-size: 28rpx;
  color: #6B7280;
}

.progress-value {
  font-size: 28rpx;
  font-weight: bold;
  color: #F59E0B;
}

.progress-bar {
  height: 16rpx;
  background: #E5E7EB;
  border-radius: 8rpx;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #FCD34D 0%, #F59E0B 100%);
  transition: width 0.5s ease;
}

/* 统计卡片 */
.stats-section {
  display: flex;
  gap: 16rpx;
  margin-bottom: 32rpx;
}

.stat-card {
  flex: 1;
  background: white;
  border-radius: 16rpx;
  padding: 24rpx;
  text-align: center;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.05);
}

.stat-icon {
  display: block;
  font-size: 48rpx;
  margin-bottom: 12rpx;
}

.stat-value {
  display: block;
  font-size: 40rpx;
  font-weight: bold;
  color: #F59E0B;
  margin-bottom: 8rpx;
}

.stat-label {
  display: block;
  font-size: 24rpx;
  color: #6B7280;
}

/* 任务区域 */
.tasks-section {
  margin-bottom: 32rpx;
}

.section-title {
  display: block;
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
  margin-bottom: 20rpx;
}

.tasks-list {
  background: white;
  border-radius: 16rpx;
  overflow: hidden;
  margin-bottom: 16rpx;
}

.task-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 24rpx;
  border-bottom: 1rpx solid #F3F4F6;
  transition: background 0.2s;
}

.task-item:last-child {
  border-bottom: none;
}

.task-item.completed {
  background: #F0FDF4;
}

.task-checkbox {
  width: 48rpx;
  height: 48rpx;
  border: 3rpx solid #D1D5DB;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
}

.task-item.completed .task-checkbox {
  background: #10B981;
  border-color: #10B981;
}

.check-icon {
  font-size: 32rpx;
  color: white;
  font-weight: bold;
}

.task-info {
  flex: 1;
}

.task-name {
  display: block;
  font-size: 30rpx;
  font-weight: 500;
  color: #1F2937;
  margin-bottom: 4rpx;
}

.task-desc {
  display: block;
  font-size: 24rpx;
  color: #9CA3AF;
}

.task-emoji {
  font-size: 48rpx;
}

.completion-hint {
  background: #EFF6FF;
  border-radius: 12rpx;
  padding: 20rpx;
  text-align: center;
}

.hint-text {
  font-size: 28rpx;
  color: #3B82F6;
}

/* 喂养按钮 */
.feed-section {
  margin-bottom: 32rpx;
}

.feed-btn {
  width: 100%;
  height: 100rpx;
  background: linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%);
  border-radius: 16rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16rpx;
  border: none;
  box-shadow: 0 8rpx 24rpx rgba(245, 158, 11, 0.3);
}

.btn-icon {
  font-size: 48rpx;
}

.btn-text {
  font-size: 36rpx;
  font-weight: bold;
  color: white;
}

/* 成长阶段 */
.stages-section {
  margin-bottom: 32rpx;
}

.stages-list {
  background: white;
  border-radius: 16rpx;
  padding: 24rpx;
}

.stage-item {
  display: flex;
  align-items: center;
  gap: 20rpx;
  padding: 20rpx;
  border-radius: 12rpx;
  margin-bottom: 12rpx;
  opacity: 0.4;
}

.stage-item:last-child {
  margin-bottom: 0;
}

.stage-item.unlocked {
  opacity: 1;
}

.stage-item.current {
  background: #FEF3C7;
  border: 2rpx solid #F59E0B;
}

.stage-emoji {
  font-size: 60rpx;
}

.stage-name {
  flex: 1;
  font-size: 28rpx;
  font-weight: 500;
  color: #1F2937;
}

.stage-days {
  font-size: 24rpx;
  color: #9CA3AF;
}
</style>
