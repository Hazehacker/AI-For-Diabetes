<template>
  <view class="scenes-page">
    <view class="page-header">
      <text class="page-title">AI专科对话</text>
      <text class="page-subtitle">选择您需要的专科场景</text>
    </view>

    <!-- 场景卡片列表 -->
    <view class="scenes-list">
      <view 
        v-for="scene in scenes" 
        :key="scene.id"
        class="scene-card"
        :style="{ borderColor: scene.color }"
        @tap="enterScene(scene.id)"
      >
        <view class="card-header">
          <text class="scene-icon">{{ scene.icon }}</text>
          <view class="scene-badge" :style="{ background: scene.color }">
            专科
          </view>
        </view>
        <text class="scene-name">{{ scene.name }}</text>
        <text class="scene-name-en">{{ scene.nameEn }}</text>
        <text class="scene-desc">{{ scene.description }}</text>
      </view>
    </view>

    <!-- 免责声明 -->
    <view class="disclaimer">
      <text class="disclaimer-icon">⚠️</text>
      <text class="disclaimer-text">AI建议不代表医师诊断，遇紧急情况请立即就医</text>
    </view>
  </view>
</template>

<script setup>
import { useSpecialistStore } from '@/store/specialist'
import { storeToRefs } from 'pinia'

const specialistStore = useSpecialistStore()
const { scenes } = storeToRefs(specialistStore)

const enterScene = (sceneId) => {
  specialistStore.enterScene(sceneId)
  
  // 跳转到对应场景页面
  const routes = {
    report: '/pages/chat/report-lab',
    drug: '/pages/chat/medicine-box',
    diary: '/pages/chat/health-diary',
    knowledge: '/pages/chat/knowledge-qa'
  }
  
  const url = routes[sceneId]
  if (url) {
    uni.navigateTo({ url })
  }
}
</script>

<style scoped>
.scenes-page {
  min-height: 100vh;
  background: linear-gradient(180deg, #667eea 0%, #764ba2 20%, #F3F4F6 20%);
  padding: 20rpx;
  padding-bottom: 120rpx;
}

.page-header {
  padding: 40rpx 20rpx;
  text-align: center;
}

.page-title {
  display: block;
  font-size: 48rpx;
  font-weight: bold;
  color: white;
  margin-bottom: 8rpx;
}

.page-subtitle {
  display: block;
  font-size: 28rpx;
  color: rgba(255, 255, 255, 0.9);
}

.scenes-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20rpx;
  padding: 20rpx;
}

.scene-card {
  background: white;
  border-radius: 24rpx;
  padding: 32rpx 24rpx;
  border: 3rpx solid transparent;
  box-shadow: 0 8rpx 24rpx rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.scene-card:active {
  transform: scale(0.95);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16rpx;
}

.scene-icon {
  font-size: 64rpx;
}

.scene-badge {
  padding: 4rpx 12rpx;
  border-radius: 8rpx;
  font-size: 20rpx;
  color: white;
  font-weight: bold;
}

.scene-name {
  display: block;
  font-size: 32rpx;
  font-weight: bold;
  color: #1F2937;
  margin-bottom: 4rpx;
}

.scene-name-en {
  display: block;
  font-size: 22rpx;
  color: #9CA3AF;
  margin-bottom: 12rpx;
}

.scene-desc {
  display: block;
  font-size: 24rpx;
  color: #6B7280;
  line-height: 1.5;
}

.disclaimer {
  margin-top: 32rpx;
  padding: 24rpx;
  background: #FEF3C7;
  border-radius: 16rpx;
  display: flex;
  gap: 12rpx;
  align-items: center;
}

.disclaimer-icon {
  font-size: 32rpx;
}

.disclaimer-text {
  flex: 1;
  font-size: 24rpx;
  color: #92400E;
  line-height: 1.5;
}
</style>
