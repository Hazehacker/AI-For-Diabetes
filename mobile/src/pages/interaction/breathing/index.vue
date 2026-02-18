<template>
  <view class="breathing-page">
    <!-- 顶部导航 -->
    <view class="nav-bar">
      <image class="nav-back-icon" src="/static/ch/ch_fr_return.png" mode="aspectFit" @tap="goBack" @error="onImageError"></image>
      <text class="nav-title">呼吸 & 冥想训练</text>
      <view class="nav-placeholder"></view>
    </view>

    <!-- 主要内容 -->
    <view class="main-content">
      <!-- 呼吸动画区域 -->
      <view class="breathing-circle-wrapper" :class="{ 'child-mode-wrapper': isChildMode }">
        <!-- 儿童模式：功夫熊猫图片 -->
        <image v-if="isChildMode" class="kungfu-image" :class="{ 'kungfu-breathing': isBreathing }" src="/static/ch/ch_play_kungfu.png" mode="aspectFit"></image>
        <view class="breathing-circle" :class="{ breathing: isBreathing }">
          <view class="inner-circle">
            <text class="breath-text">{{ breathText }}</text>
          </view>
        </view>
      </view>

      <!-- 呼吸指导 -->
      <view class="instruction-card" :class="{ 'child-instruction-card': isChildMode }">
        <view class="instruction-text">
          <text v-if="!isChildMode" class="instruction-icon">🌈</text>
          <text class="instruction-title">{{ currentExercise.name }}</text>
          <text class="instruction-desc">{{ currentExercise.description }}</text>
        </view>
        <image v-if="isChildMode" class="blow-icon" src="/static/ch/ch_play_blow.png" mode="aspectFit"></image>
      </view>

      <!-- 练习选择 -->
      <view class="exercise-list">
        <view 
          v-for="exercise in exercises" 
          :key="exercise.id"
          class="exercise-item"
          :class="{ active: currentExercise.id === exercise.id }"
          @tap="selectExercise(exercise)"
        >
          <text class="exercise-icon">{{ exercise.icon }}</text>
          <view class="exercise-info">
            <text class="exercise-name">{{ exercise.name }}</text>
            <text class="exercise-duration">{{ exercise.duration }}</text>
          </view>
        </view>
      </view>

      <!-- 控制按钮 -->
      <view class="control-section">
        <button 
          class="start-btn" 
          :class="{ stop: isBreathing }"
          @tap="toggleBreathing"
        >
          <text>{{ isBreathing ? '停止' : '开始练习' }}</text>
        </button>
      </view>

      <!-- 完成次数 -->
      <view class="stats-card">
        <view class="stat-item">
          <text class="stat-value">{{ completedCount }}</text>
          <text class="stat-label">已完成次数</text>
        </view>
        <view class="stat-item">
          <text class="stat-value">{{ totalMinutes }}</text>
          <text class="stat-label">累计分钟</text>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, reactive, onUnmounted, computed } from 'vue'
import { useDashboardStore } from '@/store/dashboard'
import { storeToRefs } from 'pinia'

const dashboardStore = useDashboardStore()
const { userRole } = storeToRefs(dashboardStore)
const isChildMode = computed(() => userRole.value === 'child_under_12')

const isBreathing = ref(false)
const breathText = ref('准备开始')
const completedCount = ref(0)
const totalMinutes = ref(0)
let breathingTimer = null
let breathPhase = 0

const exercises = [
  { id: 1, name: '4-7-8 呼吸法', icon: '🌙', duration: '3分钟', inhale: 4, hold: 7, exhale: 8, description: '吸气4秒，屏息7秒，呼气8秒，帮助放松入睡' },
  { id: 2, name: '方块呼吸', icon: '⬜', duration: '2分钟', inhale: 4, hold: 4, exhale: 4, description: '吸气、屏息、呼气各4秒，平衡身心' },
  { id: 3, name: '腹式呼吸', icon: '🎈', duration: '5分钟', inhale: 5, hold: 2, exhale: 5, description: '深呼吸让肚子像气球一样鼓起来' }
]

const currentExercise = ref(exercises[0])

const goBack = () => {
  uni.navigateBack({ delta: 1 })
}

// 图片加载错误处理
const onImageError = () => {
  console.log('返回按钮图片加载失败')
}

const selectExercise = (exercise) => {
  if (isBreathing.value) return
  currentExercise.value = exercise
}

const toggleBreathing = () => {
  if (isBreathing.value) {
    stopBreathing()
  } else {
    startBreathing()
  }
}

const startBreathing = () => {
  isBreathing.value = true
  breathPhase = 0
  runBreathingCycle()
}

const stopBreathing = () => {
  isBreathing.value = false
  breathText.value = '准备开始'
  if (breathingTimer) {
    clearTimeout(breathingTimer)
    breathingTimer = null
  }
  completedCount.value++
  totalMinutes.value += parseInt(currentExercise.value.duration)
}

const runBreathingCycle = () => {
  if (!isBreathing.value) return
  
  const exercise = currentExercise.value
  const phases = [
    { text: '吸气...', duration: exercise.inhale * 1000 },
    { text: '屏息...', duration: exercise.hold * 1000 },
    { text: '呼气...', duration: exercise.exhale * 1000 }
  ]
  
  const phase = phases[breathPhase % 3]
  breathText.value = phase.text
  
  breathingTimer = setTimeout(() => {
    breathPhase++
    runBreathingCycle()
  }, phase.duration)
}

onUnmounted(() => {
  if (breathingTimer) {
    clearTimeout(breathingTimer)
  }
})
</script>

<style scoped>
.breathing-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #FEF7ED 0%, #FFF8E7 50%, #FFFBF0 100%);
  padding-bottom: 40rpx;
}

.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16rpx 24rpx;
  padding-top: calc(env(safe-area-inset-top) + 16rpx);
  background: #FFFEF7;
  border-bottom: 1rpx solid #E3C7A4;
  box-shadow: 0 2rpx 8rpx rgba(203, 142, 84, 0.1);
}

.nav-back-icon {
  width: 64rpx;
  height: 64rpx;
  display: block;
  padding: 10rpx;
  cursor: pointer;
  z-index: 100;
  position: relative;
}

.nav-title {
  font-size: 36rpx;
  font-weight: bold;
  color: #602F27;
}

.nav-placeholder {
  width: 64rpx;
}

.main-content {
  padding: 24rpx;
}

.breathing-circle-wrapper {
  display: flex;
  justify-content: center;
  padding: 40rpx 0;
}

.breathing-circle {
  width: 220rpx;
  height: 220rpx;
  border-radius: 50%;
  background: linear-gradient(135deg, #F6D387 0%, #E3C7A4 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 4s ease-in-out;
  box-shadow: 0 8rpx 24rpx rgba(203, 142, 84, 0.3);
}

.breathing-circle.breathing {
  animation: breathe 8s ease-in-out infinite;
}

@keyframes breathe {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.3); }
}

.inner-circle {
  width: 160rpx;
  height: 160rpx;
  border-radius: 50%;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: inset 0 2rpx 8rpx rgba(203, 142, 84, 0.2);
}

.breath-text {
  font-size: 32rpx;
  color: #602F27;
  font-weight: 600;
}

.instruction-card {
  background: white;
  border-radius: 28rpx;
  padding: 24rpx;
  margin-bottom: 24rpx;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 6rpx 20rpx rgba(96, 47, 39, 0.08);
}

.instruction-title {
  display: block;
  font-size: 32rpx;
  font-weight: 600;
  color: #602F27;
  margin-bottom: 12rpx;
}

.instruction-desc {
  font-size: 26rpx;
  color: #A85835;
  line-height: 1.5;
}

.exercise-list {
  display: flex;
  flex-direction: column;
  gap: 16rpx;
  margin-bottom: 32rpx;
}

.exercise-item {
  display: flex;
  align-items: center;
  gap: 16rpx;
  background: white;
  border-radius: 20rpx;
  padding: 20rpx;
  border: 2rpx solid #E3C7A4;
}

.exercise-item.active {
  background: linear-gradient(135deg, #FFF8E7 0%, #F2E5D3 100%);
  border: 3rpx solid #CB8E54;
}

.exercise-icon {
  font-size: 40rpx;
}

.exercise-info {
  flex: 1;
}

.exercise-name {
  display: block;
  font-size: 28rpx;
  color: #602F27;
  font-weight: 500;
}

.exercise-duration {
  font-size: 24rpx;
  color: #A85835;
}

.control-section {
  margin-bottom: 32rpx;
}

.start-btn {
  width: 100%;
  height: 88rpx;
  background: #F6D387;
  color: #602F27;
  font-size: 32rpx;
  font-weight: 600;
  border-radius: 44rpx;
  border: 4rpx solid #E3C7A4;
  box-shadow: 0 6rpx 0 #D5A874;
}

.start-btn:active {
  transform: translateY(4rpx);
  box-shadow: 0 2rpx 0 #D5A874;
}

.start-btn.stop {
  background: #E5E7EB;
  color: #9CA3AF;
  border-color: #D1D5DB;
  box-shadow: 0 6rpx 0 #D1D5DB;
}

.stats-card {
  display: flex;
  background: white;
  border-radius: 28rpx;
  padding: 24rpx;
  border: 3rpx solid #E3C7A4;
  box-shadow: 0 6rpx 20rpx rgba(96, 47, 39, 0.08);
}

.stat-item {
  flex: 1;
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 40rpx;
  font-weight: 700;
  color: #CB8E54;
}

.stat-label {
  font-size: 24rpx;
  color: #A85835;
}

/* 儿童模式样式 */
.child-mode-wrapper {
  flex-direction: column;
  align-items: center;
  min-height: calc(100vh - 200rpx);
  justify-content: center;
  padding: 40rpx 0;
}

.kungfu-image {
  width: 500rpx;
  height: 500rpx;
  margin-bottom: 30rpx;
  transition: transform 0.3s ease;
}

.kungfu-breathing {
  animation: kungfu-breathe 4s ease-in-out infinite !important;
}

@keyframes kungfu-breathe {
  0%, 100% { 
    transform: scale(1) translateY(0px); 
  }
  25% { 
    transform: scale(1.05) translateY(-8px); 
  }
  50% { 
    transform: scale(1.1) translateY(-15px); 
  }
  75% { 
    transform: scale(1.05) translateY(-8px); 
  }
}

.child-instruction-card {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: space-between;
}

.instruction-text {
  flex: 1;
}

.blow-icon {
  width: 120rpx;
  height: 120rpx;
  flex-shrink: 0;
}

.instruction-icon {
  font-size: 40rpx;
  margin-right: 8rpx;
  vertical-align: middle;
}
</style>
