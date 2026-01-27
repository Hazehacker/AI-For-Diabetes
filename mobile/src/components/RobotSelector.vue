<template>
  <view v-if="visible" class="modal-overlay" @tap="handleClose">
    <view class="modal-content" @tap.stop>
      <view class="modal-header">
        <text class="title">选择助手</text>
        <view class="close-btn" @tap="handleClose">
          <text class="icon">✕</text>
        </view>
      </view>

      <view class="robot-list">
        <view 
          v-for="robot in robots" 
          :key="robot.id"
          class="robot-item"
          :class="{ 'active': current.id === robot.id }"
          @tap="selectRobot(robot)"
        >
          <image class="robot-avatar" :src="robot.avatar" mode="aspectFill"></image>
          <view class="robot-info">
            <text class="robot-name">{{ robot.name }}</text>
            <text class="robot-desc">{{ robot.description }}</text>
          </view>
          <view v-if="current.id === robot.id" class="check-icon">
            <text>✓</text>
          </view>
        </view>
      </view>

      <view class="speed-section">
        <text class="section-title">语速设置</text>
        <view class="speed-control">
          <text class="speed-label">慢</text>
          <slider 
            class="speed-slider"
            :value="speed"
            :min="0.5"
            :max="2.0"
            :step="0.1"
            @change="onSpeedChange"
            activeColor="#5147FF"
          />
          <text class="speed-label">快</text>
        </view>
        <text class="speed-value">{{ speed.toFixed(1) }}x</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  visible: Boolean,
  robots: Array,
  current: Object
})

const emit = defineEmits(['close', 'select'])

const speed = ref(1.0)

const handleClose = () => {
  emit('close')
}

const selectRobot = (robot) => {
  emit('select', robot)
  handleClose()
}

const onSpeedChange = (e) => {
  speed.value = e.detail.value
  uni.setStorageSync('robotSpeed', speed.value)
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 40rpx;
}

.modal-content {
  width: 100%;
  max-width: 600rpx;
  max-height: 80vh;
  background: white;
  border-radius: 32rpx;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 32rpx;
  border-bottom: 2rpx solid #f3f4f6;
}

.title {
  font-size: 32rpx;
  font-weight: 600;
  color: #1f2937;
}

.close-btn {
  width: 48rpx;
  height: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn .icon {
  font-size: 32rpx;
  color: #6b7280;
}

.robot-list {
  padding: 32rpx;
  max-height: 50vh;
  overflow-y: auto;
}

.robot-item {
  display: flex;
  align-items: center;
  padding: 24rpx;
  background: #f9fafb;
  border-radius: 20rpx;
  margin-bottom: 16rpx;
  border: 2rpx solid transparent;
}

.robot-item.active {
  background: linear-gradient(135deg, #e0e7ff 0%, #f3e8ff 100%);
  border-color: #969FFF;
}

.robot-avatar {
  width: 80rpx;
  height: 80rpx;
  border-radius: 40rpx;
  margin-right: 24rpx;
}

.robot-info {
  flex: 1;
}

.robot-name {
  display: block;
  font-size: 30rpx;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8rpx;
}

.robot-desc {
  display: block;
  font-size: 24rpx;
  color: #6b7280;
}

.check-icon {
  width: 48rpx;
  height: 48rpx;
  background: #5147FF;
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28rpx;
}

.speed-section {
  padding: 32rpx;
  border-top: 2rpx solid #f3f4f6;
}

.section-title {
  display: block;
  font-size: 28rpx;
  font-weight: 500;
  color: #374151;
  margin-bottom: 24rpx;
}

.speed-control {
  display: flex;
  align-items: center;
  gap: 16rpx;
  margin-bottom: 16rpx;
}

.speed-label {
  font-size: 24rpx;
  color: #6b7280;
}

.speed-slider {
  flex: 1;
}

.speed-value {
  display: block;
  text-align: center;
  font-size: 28rpx;
  font-weight: 600;
  color: #5147FF;
}
</style>
